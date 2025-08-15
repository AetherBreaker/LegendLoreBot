if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from asyncio import get_running_loop, sleep
from collections.abc import Sequence
from copy import deepcopy
from logging import getLogger
from typing import Any, Optional

from aiologic import Lock
from aiorwlock import RWLock
from environment_init_vars import GOOGLE_API_KEY_FILE, SETTINGS
from google.oauth2.service_account import Credentials
from gspread import Client, authorize
from gspread.http_client import BackOffHTTPClient
from gspread.utils import DateTimeOption, Dimension, ValueInputOption, ValueRenderOption
from pandas import DataFrame, MultiIndex, Series
from typing_custom import CharacterUID, ValueRange, ValuesBatchUpdateBody
from typing_custom.abc import SingletonType
from typing_custom.dataframe_column_names import (
  ColNameEnum,
  DatabaseCharactersColumns,
  DatabaseCharactersIndex,
  DatabaseGuildsColumns,
  DatabaseGuildsIndex,
  DatabaseUsersColumns,
  DatabaseUsersIndex,
)
from validation import CustomBaseModel
from validation.apply_model import build_typed_dataframe
from validation.models.db_entries import CharacterDBEntryModel, GuildDBEntryModel, UserDBEntryModel

logger = getLogger(__name__)


DEFAULT_SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]


class DatabaseCache(metaclass=SingletonType):
  _database_id = SETTINGS.database_id
  _tab_id_guilds = SETTINGS.database_guilds_id
  _tab_id_users = SETTINGS.database_users_id
  _tab_id_characters = SETTINGS.database_characters_id
  _creds = Credentials.from_service_account_file(GOOGLE_API_KEY_FILE, scopes=DEFAULT_SCOPES)

  _guilds_tab_range = f"Guilds!R2C1:C{len(DatabaseGuildsColumns.all_columns())}"
  _users_tab_range = f"Users!R2C1:C{len(DatabaseUsersColumns.all_columns())}"
  _characters_tab_range = f"Characters!R2C1:C{len(DatabaseCharactersColumns.all_columns())}"

  _guilds_range_format_single = "Guilds!{cell}"
  _users_range_format_single = "Users!{cell}"
  _characters_range_format_single = "Characters!{cell}"

  _guilds_range_format = "Guilds!{start}:{end}"
  _users_range_format = "Users!{start}:{end}"
  _characters_range_format = "Characters!{start}:{end}"

  _db_write_body_base = ValuesBatchUpdateBody(
    valueInputOption=ValueInputOption.raw,
    includeValuesInResponse=False,
    responseValueRenderOption=ValueRenderOption.unformatted,
    responseDateTimeRenderOption=DateTimeOption.formatted_string,
    data=[],
  )

  reauth_interval = 2700
  api_call_min_interval = 1.1

  def __init__(self) -> None:
    self.guilds: CacheViewGuilds
    self.users: CacheViewUsers
    self.characters: CacheViewCharacters

    self.loop = get_running_loop()

    self._read_write_lock = RWLock()
    # self._read_write_lock = RWLock(fast=True)

    self._api_write_lock = Lock()
    self._update_queue_lock = Lock()

    self._client = None
    self._client_last_auth_time = None

    self._api_last_call_time = None

    self._update_body: Optional[ValuesBatchUpdateBody] = None

    self.update_db_header()

  @property
  def client(self) -> Client:
    now = self.loop.time()
    if self._client_last_auth_time is None or ((self._client_last_auth_time + self.reauth_interval) < now):
      self._client = authorize(self._creds, http_client=BackOffHTTPClient)
      self._client_last_auth_time = self.loop.time()
    return self._client  # type: ignore

  @property
  def queued_updates(self) -> list[ValueRange]:
    if self._update_body is None:
      self._update_body = deepcopy(self._db_write_body_base)
    return self._update_body["data"]

  async def queue_db_api_update(self, value: ValueRange) -> None:
    async with self._update_queue_lock:
      if self._update_body is None:
        self._update_body = deepcopy(self._db_write_body_base)
      self._update_body["data"].append(value)

  def update_db_header(self) -> None:
    body = deepcopy(self._db_write_body_base)

    body["data"].append(
      ValueRange(
        range=self._guilds_range_format.format(start="R1C1", end=f"R1C{len(DatabaseGuildsColumns.all_columns())}"),
        majorDimension=Dimension.rows,
        values=[DatabaseGuildsColumns.all_columns()],  # type: ignore
      )
    )
    body["data"].append(
      ValueRange(
        range=self._users_range_format.format(start="R1C1", end=f"R1C{len(DatabaseUsersColumns.all_columns())}"),
        majorDimension=Dimension.rows,
        values=[DatabaseUsersColumns.all_columns()],  # type: ignore
      )
    )
    body["data"].append(
      ValueRange(
        range=self._characters_range_format.format(start="R1C1", end=f"R1C{len(DatabaseCharactersColumns.all_columns())}"),
        majorDimension=Dimension.rows,
        values=[DatabaseCharactersColumns.all_columns()],  # type: ignore
      )
    )

    cols_body = {
      "requests": [
        {
          "updateSheetProperties": {
            "properties": {
              "sheetId": self._tab_id_guilds,
              "gridProperties": {"columnCount": len(DatabaseGuildsColumns.all_columns())},
            },
            "fields": "gridProperties/columnCount",
          }
        },
        {
          "updateSheetProperties": {
            "properties": {
              "sheetId": self._tab_id_users,
              "gridProperties": {"columnCount": len(DatabaseUsersColumns.all_columns())},
            },
            "fields": "gridProperties/columnCount",
          }
        },
        {
          "updateSheetProperties": {
            "properties": {
              "sheetId": self._tab_id_characters,
              "gridProperties": {"columnCount": len(DatabaseCharactersColumns.all_columns())},
            },
            "fields": "gridProperties/columnCount",
          }
        },
      ]
    }

    self.client.http_client.batch_update(self._database_id, cols_body)

    self.client.http_client.values_batch_update(id=self._database_id, body=body)

    # sheet = self.client.open_by_key(self._database_id)
    # worksheet = sheet.sheet1

    # worksheet.add_cols()

  def check_database_format(self) -> bool:
    """Checks whether the database spreadsheet matches the expected formatting."""
    ...  # TODO

  def initialize_blank_database(self) -> None:
    """
    Assuming the database is a blank newly created spreadsheet,
    initializes it with the required tabs and headers.
    """
    ...  # TODO

  async def wait_for_api(self) -> None:
    if self._api_last_call_time is None:
      self._api_last_call_time = self.loop.time()
      return

    delta = self.loop.time() - self._api_last_call_time
    if delta >= self.api_call_min_interval:
      self._api_last_call_time = self.loop.time()
      return

    await sleep(self.api_call_min_interval - delta)
    self._api_last_call_time = self.loop.time()
    return

  async def refresh_cache(self) -> None:
    async with self._api_write_lock, self._read_write_lock.writer_lock:
      await self.wait_for_api()

      result = self.client.http_client.values_batch_get(
        id=self._database_id,
        ranges=[self._guilds_tab_range, self._users_tab_range, self._characters_tab_range],
        params={
          "majorDimension": Dimension.rows,
          "valueRenderOption": ValueRenderOption.unformatted,
          "dateTimeRenderOption": DateTimeOption.formatted_string,
        },
      )

      try:
        guilds_data: list[list[str | int | float]] = result["valueRanges"][0]["values"]
        self.guilds = CacheViewGuilds(
          raw_data=guilds_data, columns=DatabaseGuildsColumns, types_model=GuildDBEntryModel, cache_core=self
        )
      except KeyError:
        self.guilds = CacheViewGuilds(raw_data=[], columns=DatabaseGuildsColumns, types_model=GuildDBEntryModel, cache_core=self)
      try:
        users_data: list[list[str | int | float]] = result["valueRanges"][1]["values"]
        self.users = CacheViewUsers(
          raw_data=users_data, columns=DatabaseUsersColumns, types_model=UserDBEntryModel, cache_core=self
        )
      except KeyError:
        self.users = CacheViewUsers(raw_data=[], columns=DatabaseUsersColumns, types_model=UserDBEntryModel, cache_core=self)
      try:
        characters_data: list[list[str | int | float]] = result["valueRanges"][2]["values"]
        self.characters = CacheViewCharacters(
          raw_data=characters_data,
          columns=DatabaseCharactersColumns,
          types_model=CharacterDBEntryModel,
          cache_core=self,
        )
      except KeyError:
        self.characters = CacheViewCharacters(
          raw_data=[], columns=DatabaseCharactersColumns, types_model=CharacterDBEntryModel, cache_core=self
        )

  async def submit_queued_writes_to_pool(self) -> None:
    if not self.queued_updates:
      return

    await self.loop.run_in_executor(None, self._api_write)

  def _api_write(self):
    with self._api_write_lock, self._update_queue_lock:
      self.client.http_client.values_batch_update(
        id=self._database_id,
        body=self._update_body,
      )

      self._update_body = None  # Reset the update body after writing


class CacheViewBase[ModelT: CustomBaseModel]:
  _range_format: str
  _range_format_single: str

  def __init__(
    self,
    raw_data: list[list[str | int | float]],
    columns: type[ColNameEnum],
    types_model: type[ModelT],
    cache_core: DatabaseCache,
  ) -> None:
    self._cache = build_typed_dataframe(data=raw_data, columns=columns, types_model=types_model)  # type: ignore
    self._cache_index = columns.__index_items__
    self._columns = columns
    self._core = cache_core
    self._model = types_model

  async def __aenter__(self) -> DataFrame:
    await self._core._read_write_lock.reader_lock.acquire()
    return self._cache

  async def __aexit__(self, exc_type, exc_value, traceback) -> None:
    self._core._read_write_lock.reader_lock.release()

  async def read_typed_row(self, index) -> ModelT:
    async with self._core._read_write_lock.reader_lock:
      row = self._cache[*index if isinstance(index, tuple) else index]
      return self._model.model_construct(**row)

  async def process_index(self, index) -> int:
    # default process index. Assume single index
    async with self._core._read_write_lock.reader_lock:
      # locate the row number of index
      row_number = self._cache.index.get_loc(index)

    if isinstance(row_number, slice):
      row_number = int(row_number.stop - row_number.start)
    if (not isinstance(row_number, int)) or (0 < row_number < 1):
      raise IndexError("Index provided is either a partial index, or otherwise fails to return a single row")

    return row_number

  async def write_value(self, index, column, value: Any) -> None:
    row_number = await self.process_index(index)

    async with self._core._read_write_lock.writer_lock:
      self._cache.at[index, column] = value

    row_number += 2  # add one to account for gsheets header

    # get column index

    await self._core.queue_db_api_update(
      ValueRange(
        range=self._range_format_single.format(cell=f"R{row_number}C{self._columns.get_enum_index(column) + 1}"),
        majorDimension=Dimension.rows,
        values=[[value]],
      )
    )

  async def update_row(self, index, values: Sequence[Any] | ModelT) -> None:
    row_number = await self.process_index(index)

    if isinstance(values, self._model):
      row = Series(values.model_dump(), dtype=object)
      sheets_row = Series(values.model_dump(mode="json"), dtype=object)
    elif isinstance(values, Sequence):
      row = Series(values, dtype=object, index=self._columns.all_columns())
      sheets_row = row.copy()
    else:
      raise TypeError(f"{type(values)} does not match the expected type of Sequence[Any] or {self._model}")

    async with self._core._read_write_lock.writer_lock:
      self._cache.loc[index, :] = row

    row_number += 2  # add one to account for gsheets header

    # get column index

    update_data = ValueRange(
      range=self._range_format.format(start=f"R{row_number}C1", end=f"C{len(self._columns)}"),
      majorDimension=Dimension.rows,
      values=[sheets_row.tolist()],
    )

    await self._core.queue_db_api_update(update_data)

  async def append_row(self, values: ModelT) -> None:
    index = (
      tuple(getattr(values, col) for col in self._cache_index)
      if len(self._cache_index) > 1
      else getattr(values, self._cache_index[0])
    )

    row = Series(values.model_dump(), dtype=object)
    sheets_row = Series(values.model_dump(mode="json"), dtype=object)

    async with self._core._read_write_lock.writer_lock:
      self._cache.loc[index, :] = row

    await self._core.queue_db_api_update(
      ValueRange(
        range=self._range_format.format(start=f"R{len(self._cache) + 1}C1", end=f"C{len(self._columns)}"),
        majorDimension=Dimension.rows,
        values=[sheets_row.tolist()],
      )
    )

  async def check_exist(self, index) -> bool:
    async with self._core._read_write_lock.reader_lock:
      return index in self._cache.index


class CacheViewGuilds(CacheViewBase[GuildDBEntryModel]):
  _range_format_single = "Guilds!{cell}}"
  _range_format = "Guilds!{start}:{end}"

  async def read_typed_row(self, index: DatabaseGuildsIndex) -> GuildDBEntryModel:
    return await super().read_typed_row(index)

  async def process_index(self, index: DatabaseGuildsIndex) -> int:
    return await super().process_index(index)

  async def write_value(self, index: DatabaseGuildsIndex, column: DatabaseGuildsColumns, value: Any) -> None:
    return await super().write_value(index, column, value)

  async def update_row(self, index: DatabaseGuildsIndex, values: Sequence[Any] | GuildDBEntryModel) -> None:
    return await super().update_row(index, values)

  async def append_row(self, values: GuildDBEntryModel) -> None:
    return await super().append_row(values)

  async def check_exist(self, index: DatabaseGuildsIndex) -> bool:
    return await super().check_exist(index)


class CacheViewUsers(CacheViewBase[UserDBEntryModel]):
  _range_format_single = "Users!{cell}}"
  _range_format = "Users!{start}:{end}"

  async def read_typed_row(self, index: DatabaseUsersIndex) -> UserDBEntryModel:
    return await super().read_typed_row(index)

  async def process_index(self, index: DatabaseUsersIndex) -> int:
    dex: MultiIndex = self._cache.index  # type: ignore

    async with self._core._read_write_lock.reader_lock:
      # locate the row number of index
      row_number = dex.get_locs(index)

    if isinstance(row_number, slice):
      row_number = int(row_number.stop - row_number.start)
    if (not isinstance(row_number, int)) or (0 < row_number < 1):
      raise IndexError("Index provided is either a partial index, or otherwise fails to return a single row")

    return row_number

  async def write_value(self, index: DatabaseUsersIndex, column: DatabaseUsersColumns, value: Any) -> None:
    return await super().write_value(index, column, value)

  async def update_row(self, index: DatabaseUsersIndex, values: Sequence[Any] | UserDBEntryModel) -> None:
    return await super().update_row(index, values)

  async def append_row(self, values: UserDBEntryModel) -> None:
    return await super().append_row(values)

  async def check_exist(self, index: DatabaseUsersIndex) -> bool:
    return await super().check_exist(index)


class CacheViewCharacters(CacheViewBase[CharacterDBEntryModel]):
  _range_format_single = "Characters!{cell}"
  _range_format = "Characters!{start}:{end}"

  async def read_typed_row(self, index: DatabaseCharactersIndex) -> CharacterDBEntryModel:
    return await super().read_typed_row(index)

  async def process_index(self, index: DatabaseCharactersIndex) -> int:
    dex: MultiIndex = self._cache.index  # type: ignore

    if isinstance(index, Sequence) and len(index) == 2:
      index_seq = [slice(None), *index]
    elif not isinstance(index, Sequence) or len(index) == 1:
      index_seq = [index] + ([slice(None)] * (dex.nlevels - 1))
    else:
      index_seq = index

    async with self._core._read_write_lock.reader_lock:
      # locate the row number of index
      row_number = dex.get_locs(index_seq)

    if isinstance(row_number, slice):
      row_number = int(row_number.stop - row_number.start)

    elif len(row_number) == 1:
      row_number = int(row_number[0])

    if (not isinstance(row_number, int)) or (0 < row_number < 1):
      raise IndexError("Index provided is either a partial index, or otherwise fails to return a single row")

    return row_number

  async def write_value(self, index: DatabaseCharactersIndex, column: DatabaseCharactersColumns, value: Any) -> None:
    return await super().write_value(index, column, value)

  async def update_row(self, index: DatabaseCharactersIndex, values: Sequence[Any] | CharacterDBEntryModel) -> None:
    return await super().update_row(index, values)

  async def append_row(self, values: CharacterDBEntryModel) -> None:
    return await super().append_row(values)

  async def check_exist(self, index: CharacterUID) -> bool:
    async with self._core._read_write_lock.reader_lock:
      char_uids = self._cache.index.levels[0]  # type: ignore

      return index in char_uids
