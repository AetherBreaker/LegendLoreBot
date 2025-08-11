if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from enum import StrEnum
from logging import getLogger
from typing import Any, Self

from typing_custom import CharacterUID, GuildID, UserID

logger = getLogger(__name__)


class ColNameEnum(StrEnum):
  __exclude__: list[str] = []
  __init_include__: list[str] = []
  __index_items__: list[str] = []

  @classmethod
  def ordered_column_names(cls, *columns: str) -> list[str]:
    columns_list = [str(column) for column in columns]
    return [str(column) for column in cls if str(column) in columns_list]

  @classmethod
  def all_columns(cls) -> list[str]:
    return [str(column) for column in cls if str(column) not in cls.__exclude__ and not str(column).startswith("_")]

  @classmethod
  def err_reporting_columns(cls) -> list[str]:
    """
    Return all columns that are not excluded and do not start with an underscore.
    This is used for error reporting.
    """
    return [
      "err_field_name",
      "err_reason",
      *[str(column) for column in cls if str(column) not in cls.__exclude__ and not str(column).startswith("_")],
    ]

  @classmethod
  def init_columns(cls) -> list[str]:
    if not cls.__init_include__:
      return cls.all_columns()
    return [str(column) for column in cls if str(column) in cls.__init_include__ and not str(column).startswith("_")]

  @classmethod
  def testing_columns(cls) -> list[str]:
    return [str(column) for column in cls if str(column) not in cls.__exclude__]

  @classmethod
  def true_all_columns(cls) -> list[str]:
    return [str(column) for column in cls]

  @classmethod
  def get_enum_index(cls, value: Self) -> int:
    return list(cls).index(value)

  @staticmethod
  def _generate_next_value_(name, start, count, last_values) -> Any:
    """
    Return the member name.
    """
    return name


class DatabaseGuildsColumns(ColNameEnum):
  __index_items__ = ["guild_id"]

  guild_id = "guild_id"
  guild_name = "guild_name"


type DatabaseGuildsIndex = GuildID


class DatabaseUsersColumns(ColNameEnum):
  __index_items__ = ["user_id", "guild_id"]

  user_id = "user_id"
  guild_id = "guild_id"
  user_name = "user_name"
  server_money = "server_money"


type DatabaseUsersIndex = tuple[UserID, GuildID]


class DatabaseCharactersColumns(ColNameEnum):
  __index_items__ = ["character_uid", "user_id", "guild_id"]

  character_uid = "character_uid"
  user_id = "user_id"
  guild_id = "guild_id"
  character_name = "character_name"
  milestones = "milestones"
  mythic_trials = "mythic_trials"
  money_pp = "money_pp"
  money_gp = "money_gp"
  money_sp = "money_sp"
  money_cp = "money_cp"
  downtime_stockpiled = "downtime_stockpiled"


type DatabaseCharactersIndex = tuple[CharacterUID, UserID, GuildID] | tuple[UserID, GuildID] | CharacterUID
