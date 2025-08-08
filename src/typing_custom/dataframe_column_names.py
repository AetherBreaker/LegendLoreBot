if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from enum import StrEnum
from logging import getLogger
from typing import Any

logger = getLogger(__name__)


class ColNameEnum(StrEnum):
  __exclude__ = []
  __init_include__ = []

  @classmethod
  def ordered_column_names(cls, *columns: str) -> list[str]:
    columns_list = [str(column) for column in columns]
    return [str(column) for column in cls if str(column) in columns_list]

  @classmethod
  def all_columns(cls) -> list[str]:
    return [
      str(column)
      for column in cls
      if str(column) not in cls.__exclude__ and not str(column).startswith("_")
    ]

  @classmethod
  def err_reporting_columns(cls) -> list[str]:
    """
    Return all columns that are not excluded and do not start with an underscore.
    This is used for error reporting.
    """
    return [
      "err_field_name",
      "err_reason",
      *[
        str(column)
        for column in cls
        if str(column) not in cls.__exclude__ and not str(column).startswith("_")
      ],
    ]

  @classmethod
  def init_columns(cls) -> list[str]:
    if not cls.__init_include__:
      return cls.all_columns()
    return [
      str(column)
      for column in cls
      if str(column) in cls.__init_include__ and not str(column).startswith("_")
    ]

  @classmethod
  def testing_columns(cls) -> list[str]:
    return [str(column) for column in cls if str(column) not in cls.__exclude__]

  @classmethod
  def true_all_columns(cls) -> list[str]:
    return [str(column) for column in cls]

  @staticmethod
  def _generate_next_value_(name, start, count, last_values) -> Any:
    """
    Return the member name.
    """
    return name
