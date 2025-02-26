import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database settings
DATABASE_PATH = os.getenv('DATABASE_PATH', 'word_groups.db')

# Amazon Bedrock settings
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
BEDROCK_MODEL_ID = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-5-sonnet-20240620-v1:0')

# Application settings
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'