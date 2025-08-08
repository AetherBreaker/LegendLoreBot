if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from logging import getLogger

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema

logger = getLogger(__name__)


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
