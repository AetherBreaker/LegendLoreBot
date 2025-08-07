if __name__ == "__main__":
  from src.logging_config import configure_logging

  configure_logging()

import os
from logging import getLogger
from pathlib import Path
from typing import Annotated

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = getLogger(__name__)

os.environ.setdefault("PYDANTIC_ERRORS_INCLUDE_URL", "false")


class Settings(BaseSettings):
  model_config = SettingsConfigDict(
    env_file=Path.cwd() / ".env",
    env_file_encoding="utf-8",
    env_ignore_empty=True,
  )

  token: Annotated[str, Field(alias="TOKEN")]
  database_id: Annotated[str, Field(alias="DATABASE_ID")]
  database_guilds_id: Annotated[str, Field(alias="DATABASE_GUILDS_ID")]
  database_users_id: Annotated[str, Field(alias="DATABASE_USERS_ID")]
  database_characters_id: Annotated[str, Field(alias="DATABASE_CHARACTERS_ID")]

  database_refresh_interval: Annotated[int, Field(alias="DATABASE_REFRESH_INTERVAL")] = 3600
