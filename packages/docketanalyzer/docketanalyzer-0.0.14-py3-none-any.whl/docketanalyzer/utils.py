import os
from dotenv import load_dotenv
import openai
from pathlib import Path
import simplejson as json


load_dotenv()

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME')
AWS_S3_BUCKET_NAME = os.environ.get('AWS_S3_BUCKET_NAME')

HUGGING_FACE_HUB_TOKEN = os.environ.get('HUGGING_FACE_HUB_TOKEN')

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

RUNPOD_API_KEY = os.environ.get('RUNPOD_API_KEY')
RUNPOD_INFERENCE_ENDPOINT_ID = os.environ.get('RUNPOD_INFERENCE_ENDPOINT_ID')
RUNPOD_VOLUME_ID = os.environ.get('RUNPOD_VOLUME_ID')
RUNPOD_DATACENTER_ID = os.environ.get('RUNPOD_DATACENTER_ID')

default_data_dir = None
try: 
    default_data_dir = Path.home().resolve() / 'data' / 'docketanalyzer'
except:
    pass
DATA_DIR = Path(os.environ.get('DOCKET_ANALYZER_DATA_DIR', default_data_dir))

