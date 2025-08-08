if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from logging import getLogger

from pydantic import BaseModel, ConfigDict

logger = getLogger(__name__)


class CustomBaseModel(BaseModel):
  model_config = ConfigDict(
    populate_by_name=True,
    use_enum_values=True,
    validate_default=True,
    validate_assignment=True,
    coerce_numbers_to_str=True,
  )
