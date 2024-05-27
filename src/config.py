from dotenv import load_dotenv
import os

load_dotenv()

REAL_DATABASE_URL = os.environ.get("REAL_DATABASE_URL")
SECRET_AUTH = os.environ.get("SECRET_AUTH")
SECRET_MANAGER = os.environ.get("SECRET_MANAGER")
JWT_PUBLIC_KEY = os.environ.get("JWT_PUBLIC_KEY")
JWT_PRIVATE_KEY = os.environ.get("JWT_PRIVATE_KEY")