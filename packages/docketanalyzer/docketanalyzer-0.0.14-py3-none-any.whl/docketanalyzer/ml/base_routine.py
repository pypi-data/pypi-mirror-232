import shutil
import os
from typing import Any, Optional
from datasets import Dataset
from huggingface_hub import HfApi
import pandas as pd
from pathlib import Path
try:
    from auto_gptq import AutoGPTQForCausalLM, BaseQuantizeConfig
    import bitsandbytes as bnb
    from bitsandbytes.functional import dequantize_4bit
    from peft import prepare_model_for_kbit_training, PeftModel
    from peft import PeftModel, AutoPeftModelForCausalLM
    from peft import LoraConfig, get_peft_model
    from peft.utils import _get_submodules
    import torch
    import torch.nn as nn
    from transformers import (
        AutoTokenizer, 
        AutoModelForCausalLM, 
        BitsAndBytesConfig, 
        Trainer, 
        TrainingArguments, 
        DataCollatorForLanguageModeling,
    )
except ImportError:
    pass


def get_label_mask(input_ids, eos_token_id, separator=[518, 29914, 25580, 29962]):
    if not isinstance(input_ids, torch.Tensor):
        input_ids = torch.tensor(input_ids)
    if not isinstance(separator, torch.Tensor):
        separator = torch.tensor(separator)

    separator_len = separator.size(0)
    input_len = input_ids.size(0)
    start = 0
    end = input_len
    for i in range(input_len):
        if not i + separator_len > input_len:
            if torch.all(input_ids[i:i+separator_len] == separator):
                start = i + separator_len
        if input_ids[i] == eos_token_id and start > 0:
            end = i
            break
            
    if end < input_len:
        end += 1

    if start > 0:
        start -= 1

    mask = torch.full_like(input_ids, 0)
    mask[start:end] = 1
    return mask


class BaseRoutine:
    def __init__(
        self,
        train_data,
        model_name,
        base_model='meta-llama/Llama-2-7b-chat-hf',
        training_args={},
        eval_data=None,
        quantization_config=None,
        lora_config=None,
        train_on_prompts=True,
        max_length=1024,
        hf_token=None,
        adapters_name=None,
        quantized_name=None,
        **kwargs,
    ):
        if 'output_dir' not in training_args:
            training_args['output_dir'] = 'outputs'
        self.train_data = train_data
        self.model_name = model_name
        self.base_model = base_model
        self.training_args = training_args
        self.eval_data = eval_data
        self.quantization_config = quantization_config
        self.lora_config = lora_config
        self.train_on_prompts = train_on_prompts
        self.max_length = max_length
        self.hf_token = hf_token
        
        self.adapters_name = adapters_name if adapters_name is not None else model_name + '-adapters'
        self.quantized_name = quantized_name if quantized_name is not None else model_name + '-GPTQ'
        if isinstance(self.train_data, list):
            self.train_data = pd.DataFrame(self.train_data)
        if isinstance(self.eval_data, list):
            self.eval_data = pd.DataFrame(self.eval_data)
        self.tokenizer = self.load_tokenizer()

    def get_trainer_class(self):
        if self.train_on_prompts:
            class CustomTrainer(Trainer):
                def compute_loss(self, model, inputs, return_outputs=False):
                    inputs['labels'] = inputs['input_ids']
                    return super().compute_loss(model, inputs, return_outputs)
        else:
            class CustomTrainer(Trainer):
                def compute_loss(self, model, inputs, return_outputs=False):
                    labels = torch.full_like(inputs['input_ids'], -100)
                    for i in range(inputs['input_ids'].shape[0]):
                        mask = get_label_mask(
                            inputs['input_ids'][i].detach().cpu(),
                            self.tokenizer.eos_token_id,
                        )
                        labels[i, mask == 1] = inputs['input_ids'][i, mask == 1]
                    inputs['labels'] = labels.to(model.device)
                    return super().compute_loss(model, inputs, return_outputs)
        return CustomTrainer

    def load_tokenizer(self):
        tokenizer = AutoTokenizer.from_pretrained(
            self.base_model, 
            use_fast=False,
        )
        tokenizer.pad_token = tokenizer.eos_token
        return tokenizer

    def load_model(self):
        model_args = {
            'torch_dtype': torch.bfloat16,
            'device_map': 'auto',
        }

        if self.quantization_config:
            model_args['quantization_config'] = BitsAndBytesConfig(**self.quantization_config)

        model = AutoModelForCausalLM.from_pretrained(
            self.base_model,
            **model_args,
        )

        if self.lora_config:
            lora_config = LoraConfig(**self.lora_config)
            model.gradient_checkpointing_enable()
            model = prepare_model_for_kbit_training(model)
            model = get_peft_model(model, lora_config)
            class CastOutputToFloat(nn.Sequential):
                def forward(self, x): return super().forward(x).to(torch.float32)
            model.lm_head = CastOutputToFloat(model.lm_head)

        return model

    def load_dataset(self, data):
        def tokenize_text(example):
            return self.tokenizer(example['text'], truncation=True, max_length=self.max_length)
        data = data[['text']]
        return Dataset.from_pandas(data).map(tokenize_text, batched=True)
    
    def get_trainer_class_args(self):
        return {
            'data_collator': DataCollatorForLanguageModeling(self.tokenizer, mlm=False),
        }

    def train(self, push=True):
        train_dataset = self.load_dataset(self.train_data)
        eval_dataset = None if self.eval_data is None else self.load_dataset(self.eval_data)

        trainer_class_args = self.get_trainer_class_args() 
        if eval_dataset is not None:
            trainer_class_args['eval_dataset'] = eval_dataset

        model = self.load_model()

        trainer_class = self.get_trainer_class()
        trainer = trainer_class(
            args=TrainingArguments(
                **self.training_args
            ),
            model=model,
            tokenizer=self.tokenizer,
            train_dataset=train_dataset,
            **trainer_class_args
        )
        
        model.config.use_cache = False
        trainer.train()

        if eval_dataset is not None:
            trainer.evaluate()

        trainer.save_model(self.training_args['output_dir'])
        if push:
            self.tokenizer.push_to_hub(self.adapters_name, private=True)
            trainer.model.push_to_hub(self.adapters_name)

    def dequantize(self, dtype=torch.bfloat16):
        quantization_config = BitsAndBytesConfig(**self.quantization_config)
        
        model = AutoModelForCausalLM.from_pretrained(
            self.base_model,
            torch_dtype=torch.bfloat16,
            quantization_config=quantization_config,
            device_map={"": 0}
        )

        cls = bnb.nn.Linear4bit

        with torch.no_grad():
            for name, module in model.named_modules():
                if isinstance(module, cls):
                    print(f"Dequantizing `{name}`...")
                    quant_state = copy.deepcopy(module.weight.quant_state)
    
                    quant_state[2] = dtype
    
                    weights = dequantize_4bit(module.weight.data, quant_state=quant_state, quant_type="nf4").to(dtype)
    
                    new_module = torch.nn.Linear(module.in_features, module.out_features, bias=None, dtype=dtype)
                    new_module.weight = torch.nn.Parameter(weights)
                    new_module.to(device='cuda', dtype=dtype)
    
                    parent, target, target_name = _get_submodules(model, name)
                    setattr(parent, target_name, new_module)
    
            model.is_loaded_in_4bit = False
            return model

    def process_merge_args(self, merged_model_path=None, merged_name=None, offload_path=None):
        if merged_model_path is None:
            merged_model_path = Path(self.training_args['output_dir']) / 'merged_model'
        merged_model_path = Path(merged_model_path)
        if merged_name is None:
            merged_name = self.model_name
        if offload_path is None:
            offload_path = Path(self.training_args['output_dir']) / 'offload'
        offload_path = Path(offload_path)
        return merged_model_path, merged_name, offload_path

    def push_merged_model(self, merged_model_path=None, merged_name=None):
        merged_model_path, merged_name, _ = self.process_merge_args(merged_model_path, merged_name)
        self.tokenizer.push_to_hub(merged_name, private=True)
        api = HfApi()
        api.upload_folder(
            repo_id=merged_name,
            folder_path=merged_model_path,
        )
        
    def merge(self, merged_model_path=None, merged_name=None, offload_path=None, push=True):
        merged_model_path, merged_name, offload_path = self.process_merge_args(merged_model_path, merged_name, offload_path)

        print("Dequantizing model")
        model = self.dequantize()
        print("Merging and saving model, this can take a while")
        model = PeftModel.from_pretrained(model=model, model_id=self.adapters_name)
        print(model)
        model = model.merge_and_unload(progressbar=True)
        print(model)

        if merged_model_path.exists():
            shutil.rmtree(merged_model_path)
        merged_model_path.mkdir(exist_ok=True, parents=True)
        
        self.tokenizer.save_pretrained(merged_model_path)
        model.save_pretrained(merged_model_path, safe_serialization=True)
        model.config.save_pretrained(merged_model_path)
        
        config_path = (merged_model_path / 'config.json')
        config_data = json.loads(config_path.read_text())
        config_data.pop("quantization_config", None)
        config_data.pop("pretraining_tp", None)
        config_path.write_text(json.dumps(config_data, indent=2))

        if push:
            self.push_merged_model(merged_model_path, merged_name)

    def process_quantize_args(self, quantized_model_path=None, quantized_name=None, merged_name=None):
        if quantized_model_path is None:
            quantized_model_path = Path(self.training_args['output_dir']) / 'quantized_model'
        quantized_model_path = Path(quantized_model_path)

        if quantized_name is None:
            quantized_name = self.quantized_name

        if merged_name is None:
            merged_name = self.model_name
        return quantized_model_path, quantized_name, merged_name

    def push_quantized_model(self, quantized_model_path=None, quantized_name=None):
        quantized_model_path, quantized_name, _ = self.process_quantize_args(
            quantized_model_path, quantized_name,
        )
        self.tokenizer.push_to_hub(quantized_name, private=True)
        api = HfApi()
        api.upload_folder(
            repo_id=quantized_name,
            folder_path=quantized_model_path,
        )
        
    def quantize(
        self, 
        examples=None, 
        num_examples=128, 
        gptq_config=None,
        quantized_model_path=None, 
        quantized_name=None, 
        merged_name=None, 
        push=True,
    ):
        quantized_model_path, quantized_name, merged_name = self.process_quantize_args(
            quantized_model_path, quantized_name, merged_name
        )

        if examples is None:
            print(f"No tuning examples provided, using up to {num_examples} training examples")
            examples = self.train_data
            if len(examples) > num_examples:
                examples = examples.sample(num_examples)
            examples = examples['text'].tolist()
        examples = [self.tokenizer(x) for x in examples]

        default_gptq_config = {
            'bits': 4, 
            'group_size': 128,
            'desc_act': False,
        }
        if gptq_config is None:
            print(f"No gptq_config provided, using default: {default_gptq_config}")
            gptq_config = default_gptq_config

        gptq_config = BaseQuantizeConfig(**gptq_config)
    
        model = AutoGPTQForCausalLM.from_pretrained(
            merged_name, 
            gptq_config,
            torch_dtype=torch.float16,
        )

        print("Quantizing model, this can take a while")
        model.quantize(examples)

        if quantized_model_path.exists():
            shutil.rmtree(quantized_model_path)
        quantized_model_path.mkdir(exist_ok=True, parents=True)

        self.tokenizer.save_pretrained(quantized_model_path)
        model.save_quantized(quantized_model_path, use_safetensors=True)
        model.config.save_pretrained(quantized_model_path)

        if push:
            self.push_quantized_model(quantized_model_path, quantized_name)