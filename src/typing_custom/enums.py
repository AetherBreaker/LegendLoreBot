from enum import StrEnum, auto
from typing import Any

from disnake import Event


class CustomStrEnum(StrEnum):
  """
  Custom string enum that returns the member name as the value.
  """

  @staticmethod
  def _generate_next_value_(name, start, count, last_values) -> Any:
    """
    Return the member name.
    """
    return name


class CustomEvent(CustomStrEnum):
  on_character_created = auto()
  on_character_changed = auto()
  on_character_deleted = auto()
  on_guild_setting_changed = auto()
