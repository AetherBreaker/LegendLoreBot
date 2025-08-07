from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema


class GenericMoney(int):
  @classmethod
  def __get_pydantic_core_schema__(cls, _, handler: GetCoreSchemaHandler) -> CoreSchema:
    return handler(int)
