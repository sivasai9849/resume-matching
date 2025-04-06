import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

basedir = os.path.abspath(os.path.dirname(__file__))

ENVIRONMENT = os.getenv(key="ENVIRONMENT", default="DEVELOP")

if ENVIRONMENT == "DEVELOP":
    # Load environment variables from the .env file
    load_dotenv()


class Settings(BaseSettings):
    # App config
    APP_NAME: str = "API Analysis Service"
    APP_ENV: str = "develop"

    # Logging setting
    DATE_FMT: str = "%Y-%m-%d %H:%M:%S"
    LOG_DIR: str = f"{basedir}/logs/api.log"
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    USE_AZURE_OPENAI: bool = os.getenv("USE_AZURE_OPENAI", "false").lower() == "true"
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15")
    AZURE_OPENAI_API_BASE: str = os.getenv("AZURE_OPENAI_API_BASE", "")
    AZURE_OPENAI_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")


settings = Settings()
