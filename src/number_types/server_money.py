if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from logging import getLogger

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema

logger = getLogger(__name__)


class GenericMoney(int):
  @classmethod
  def __get_pydantic_core_schema__(cls, _, handler: GetCoreSchemaHandler) -> CoreSchema:
    return handler(int)
