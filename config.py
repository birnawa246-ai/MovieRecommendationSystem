import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')
INSTANCE_DIR = BASE_DIR / 'instance'
INSTANCE_DIR.mkdir(exist_ok=True)

def database_url():
    return os.getenv('DATABASE_URL', f"sqlite:///{INSTANCE_DIR / 'cinematch.db'}")

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-this-secret-in-production')
    SQLALCHEMY_DATABASE_URI = database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TMDB_API_KEY = os.getenv('TMDB_API_KEY', '')
    TMDB_IMAGE_BASE = 'https://image.tmdb.org/t/p/w500'
