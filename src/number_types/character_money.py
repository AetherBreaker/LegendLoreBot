from pydantic import (
  GetCoreSchemaHandler,
)
from pydantic_core import CoreSchema


class FantasyCurrency(int):
  @classmethod
  def __get_pydantic_core_schema__(cls, _, handler: GetCoreSchemaHandler) -> CoreSchema:
    return handler(int)


class PlatinumPieces(FantasyCurrency):
  pass


class GoldPieces(FantasyCurrency):
  pass


class SilverPieces(FantasyCurrency):
  pass


class CopperPieces(FantasyCurrency):
  pass
