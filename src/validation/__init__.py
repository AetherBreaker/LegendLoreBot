if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from logging import getLogger
from typing import Any, Self

from pydantic import (
  BaseModel,
  ConfigDict,
  ModelWrapValidatorHandler,
  RootModel,
  SerializationInfo,
  SerializerFunctionWrapHandler,
  ValidationError,
  ValidationInfo,
  ValidatorFunctionWrapHandler,
  field_validator,
  model_serializer,
  model_validator,
)
from pydantic_core import from_json

logger = getLogger(__name__)


PYDANTIC_CONFIG = ConfigDict(
  populate_by_name=True,
  use_enum_values=True,
  validate_default=True,
  validate_assignment=True,
  coerce_numbers_to_str=True,
)


class CustomRootModel[T](RootModel[T]):
  model_config = PYDANTIC_CONFIG
  _dumping_json: bool = False

  # @model_serializer(mode="wrap", when_used="json")
  # def serialize_as_jsonstr(self, nxt: SerializerFunctionWrapHandler):
  #   if not self._dumping_json:
  #     self._dumping_json = True
  #     return self.model_dump_json()
  #   else:
  #     self._dumping_json = False
  #     return nxt(self)

  @model_validator(mode="wrap")
  @classmethod
  def validate_as_jsonstr(cls, data: Any, handler: ValidatorFunctionWrapHandler) -> Self:
    if isinstance(data, str):
      data = from_json(data)
    return handler(data)

  @model_serializer(mode="wrap", when_used="unless-none")
  def return_self(self, nxt: SerializerFunctionWrapHandler, info: SerializationInfo):
    if not info.mode_is_json():
      return self
    if not self._dumping_json:
      self._dumping_json = True
      return self.model_dump_json()
    else:
      self._dumping_json = False
      return nxt(self)


class CustomBaseModel(BaseModel):
  model_config = PYDANTIC_CONFIG

  @field_validator("*", mode="wrap", check_fields=False)
  @classmethod
  def log_failed_field_validations(cls, data: str, handler: ValidatorFunctionWrapHandler, info: ValidationInfo) -> Any:
    results = None

    try:
      results = handler(data)
    except ValidationError as e:
      raise e

    return data if results is None else results

  @model_validator(mode="wrap")
  @classmethod
  def log_failed_validation(cls, data: Any, handler: ModelWrapValidatorHandler[Self], info: ValidationInfo) -> Self:
    results = None
    try:
      results = handler(data)
    except ValidationError as e:
      raise e

    return data if results is None else results
