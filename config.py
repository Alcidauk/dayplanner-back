"""
config file to run the app locally without docker container
"""

from dotenv import load_dotenv
import os

load_dotenv()
env_file = "envs/.env.local" if os.getenv("ENV_LOCAL") == "true" else "envs/.env.docker"
load_dotenv(env_file)

SECRET_KEY = os.getenv("SECRET_KEY")
JWT_SECRET = os.getenv("JWT_SECRET")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
DATABASE_URL = os.getenv("DATABASE_URL")
REDIRECT_URI_LOGIN = os.getenv("REDIRECT_URI_LOGIN")
OPENAI_API_KEY = os.getenv("OPENAI-API-KEY")
FRONTEND_URL = os.getenv("FRONTEND_URL")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",")
