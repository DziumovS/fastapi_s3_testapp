import os
from pathlib import Path
from dotenv import load_dotenv


PATH_TO_ENV = Path(__file__).resolve().parent.parent.joinpath("public.env")
load_dotenv(PATH_TO_ENV)


DB_DRIVER = os.getenv("POSTGRES_DRIVER")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_NAME = os.getenv("POSTGRES_NAME")

DB_URL = f"{DB_DRIVER}://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_NAME}"

PRIVATE_SERVICE_URL = os.getenv("PRIVATE_API")
