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

logger = getLogger(__name__)


class CustomRootModel(RootModel):
  model_config = ConfigDict(
    populate_by_name=True,
    use_enum_values=True,
    validate_default=True,
    validate_assignment=True,
    coerce_numbers_to_str=True,
  )
  _dumping_json: bool = False

  @model_serializer(mode="wrap", when_used="json")
  def serialize_as_jsonstr(self, nxt: SerializerFunctionWrapHandler, info: SerializationInfo):
    if not self._dumping_json:
      self._dumping_json = True
      return self.model_dump_json()
    else:
      self._dumping_json = False
      return nxt(self)


class CustomBaseModel(BaseModel):
  model_config = ConfigDict(
    populate_by_name=True,
    use_enum_values=True,
    validate_default=True,
    validate_assignment=True,
    coerce_numbers_to_str=True,
  )

  @field_validator("*", mode="wrap", check_fields=False)
  @classmethod
  def log_failed_field_validations(cls, data: str, handler: ValidatorFunctionWrapHandler, info: ValidationInfo) -> Any:
    results = None

    try:
      results = handler(data)
    except ValidationError as e:
      exc_type, exc_val, exc_tb = type(e), e, e.__traceback__

      raise e

    return data if results is None else results

  @model_validator(mode="wrap")
  @classmethod
  def log_failed_validation(cls, data: Any, handler: ModelWrapValidatorHandler[Self], info: ValidationInfo) -> Self:
    results = None
    try:
      results = handler(data)
    except ValidationError as e:
      exc_type, exc_val, exc_tb = type(e), e, e.__traceback__

      raise e

    return data if results is None else results
