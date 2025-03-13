import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

#load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    #API keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    #Database settings
    FIRESTORE_PROJECT_ID: str = os.getenv("FIRESTORE_PROJECT_ID", "")

    #Application settings
    APP_NAME: str = "Creador de artículos para blog"
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "False").lower() == "true"

    #Blog generation settings
    DEFAULT_BLOG_LENGTH: int = 2500
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gemini")

    class Config:
        env_file = ".env" #Specifies the location of the environment variable file.

#Create global settings object: This line creates a global instance of the Settings class. This allows access my configuration settings from anywhere in my application by importing the settings object.
settings = Settings()