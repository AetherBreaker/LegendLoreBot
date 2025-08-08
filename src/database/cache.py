if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()


from logging import getLogger

from environment_init_vars import GOOGLE_API_KEY_FILE, SETTINGS
from gspread import service_account
from gspread.http_client import BackOffHTTPClient
from pandas import DataFrame
from typing_custom.abc import SingletonType

logger = getLogger(__name__)

SERVICE_ACCOUNT = service_account(filename=GOOGLE_API_KEY_FILE, http_client=BackOffHTTPClient)


class DatabaseCache(metaclass=SingletonType):
  _guilds_tab_id = SETTINGS.database_guilds_id
  _users_tab_id = SETTINGS.database_users_id
  _characters_tab_id = SETTINGS.database_characters_id

  def __init__(self) -> None:
    self._guild_cache: DataFrame
    self._user_cache: DataFrame
    self._character_cache: DataFrame

  async def refresh_cache(self) -> None: ...
