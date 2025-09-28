if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

import os
from logging import getLogger
from pathlib import Path
from typing import Annotated
from uuid import getnode

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = getLogger(__name__)

os.environ.setdefault("PYDANTIC_ERRORS_INCLUDE_URL", "false")


class Settings(BaseSettings):
  model_config = SettingsConfigDict(
    env_file=Path.cwd() / ".env" if __debug__ else None,
    env_file_encoding="utf-8",
    env_ignore_empty=True,
  )

  token: Annotated[str, Field(alias="TOKEN")]
  google_api_key_data: Annotated[str, Field(alias="GOOGLE_API_KEY_DATA")]
  database_id: Annotated[str, Field(alias="DATABASE_ID")]
  database_guilds_id: Annotated[str, Field(alias="DATABASE_GUILDS_ID")]
  database_users_id: Annotated[str, Field(alias="DATABASE_USERS_ID")]
  database_characters_id: Annotated[str, Field(alias="DATABASE_CHARACTERS_ID")]

  database_refresh_interval: Annotated[int, Field(alias="DATABASE_REFRESH_INTERVAL")] = 3600
  database_write_interval: Annotated[int, Field(alias="DATABASE_WRITE_INTERVAL")] = 60

  uid_generator_seed: Annotated[int, Field(alias="UID_GENERATOR_SEED")] = getnode()
