import os

class Settings():
    DATABASE_URL = os.getenv("DATABASE_URL")
    DB_NAME = os.getenv("DB_NAME")
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    REDIS_HOST = os.getenv("REDIS_HOST")
    REDIS_PORT = int(os.getenv("REDIS_PORT"))  # Default to 6379 if not set
    GF_SECURITY_ADMIN_PASSWORD = os.getenv("GF_SECURITY_ADMIN_PASSWORD")

   


print(f"==========================endvs {Settings.DATABASE_URL} ")
