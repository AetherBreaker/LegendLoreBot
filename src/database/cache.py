if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()


from asyncio import AbstractEventLoop, get_running_loop
from logging import getLogger

from aiologic import Lock
from environment_init_vars import GOOGLE_API_KEY_FILE, SETTINGS
from google.oauth2.service_account import Credentials
from gspread import Client, authorize
from gspread.http_client import BackOffHTTPClient
from pandas import DataFrame
from typing_custom.abc import SingletonType

logger = getLogger(__name__)

DEFAULT_SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]


class DatabaseCache(metaclass=SingletonType):
  _database_id = SETTINGS.database_id
  _guilds_tab_id = SETTINGS.database_guilds_id
  _users_tab_id = SETTINGS.database_users_id
  _characters_tab_id = SETTINGS.database_characters_id
  _creds = Credentials.from_service_account_file(GOOGLE_API_KEY_FILE, scopes=DEFAULT_SCOPES)

  reauth_interval = 2700

  def __init__(self) -> None:
    self._guild_cache: DataFrame
    self._user_cache: DataFrame
    self._character_cache: DataFrame

    self.loop = get_running_loop()

    self._db_write_lock = Lock()
    self._db_read_lock = Lock()

    self._client = None
    self._client_auth_time = None

  @property
  def client(self) -> Client:
    now = self.loop.time()
    if self._client_auth_time is None or ((self._client_auth_time + self.reauth_interval) < now):
      with self._db_write_lock:
        self._client = authorize(self._creds, http_client=BackOffHTTPClient)
        self._client_auth_time = self.loop.time()
    return self._client  # type: ignore

  async def _refresh_cache(self) -> None:
    client = self.client

    client.open_by_key(self._database_id)
