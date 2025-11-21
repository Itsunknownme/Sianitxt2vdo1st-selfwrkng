#ANONYMOUS
# Add your details here and then deploy by clicking on HEROKU Deploy button
import os
from dotenv import load_dotenv

load_dotenv()  # load .env

def get_env_int(name, default=0):
    val = os.getenv(name)
    return int(val) if val else default

API_ID = get_env_int("API_ID")
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
OWNER = get_env_int("OWNER")
CREDIT = os.getenv("CREDIT", "UploaderBot")

# 👇 Add the missing variables required by drm_handler.py
api_url = os.getenv("API_URL", "") # Assuming it's a URL (string)
api_token = os.getenv("API_TOKEN", "") # Assuming it's a token (string)

AUTH_USERS = []
TOTAL_USERS = []
cookies_file_path = "cookies.json"
  
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
api_url = "http://master-api-v3.vercel.app/"
api_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNzkxOTMzNDE5NSIsInRnX3VzZXJuYW1lIjoi4p61IFtvZmZsaW5lXSIsImlhdCI6MTczODY5MjA3N30.SXzZ1MZcvMp5sGESj0hBKSghhxJ3k1GTWoBUbivUe1I"
# .....,.....,.......,...,.......,.

