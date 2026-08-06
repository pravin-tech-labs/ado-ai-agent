from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "ADO AI Agent")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    log_console_level: str = os.getenv("LOG_CONSOLE_LEVEL", "INFO")
    log_file_level: str = os.getenv("LOG_FILE_LEVEL", "DEBUG")
    log_file: str = os.getenv("LOG_FILE", "logs/ado-ai-agent.log")
    environment: str = os.getenv("ENVIRONMENT", "Development")

settings = Settings()