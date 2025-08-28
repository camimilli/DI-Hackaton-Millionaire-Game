# Configurations for API / dirpath 

import os
from dotenv import load_dotenv

# Load all environment variables from the .env file 
load_dotenv()

# config variables for database and gemini AI 
dir_path = os.path.dirname(os.path.realpath(__file__))
api_db = 'https://opentdb.com/api.php'

# Access GEMINI API from .env 
gemini_api_key = os.getenv('GEMINI_API_KEY')