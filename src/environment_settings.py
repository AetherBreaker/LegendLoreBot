if __name__ == "__main__":
  from src.logging_config import configure_logging

  configure_logging()

import os
from logging import getLogger
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = getLogger(__name__)

os.environ.setdefault("PYDANTIC_ERRORS_INCLUDE_URL", "false")


class Settings(BaseSettings):
  model_config = SettingsConfigDict(
    env_file=Path.cwd() / ".env",
    env_file_encoding="utf-8",
    env_ignore_empty=True,
  )
