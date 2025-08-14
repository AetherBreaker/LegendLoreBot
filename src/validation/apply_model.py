if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from logging import getLogger

from numpy import nan
from pandas import DataFrame, Series, concat
from typing_custom.dataframe_column_names import ColNameEnum

from validation import CustomBaseModel

logger = getLogger(__name__)

NULL_VALUES = ["NULL", "", " ", float("nan"), nan]


def build_typed_dataframe(
  data: list[list[str | int | float | None]], columns: type[ColNameEnum], types_model: type[CustomBaseModel]
) -> DataFrame:
  # pad the data with columns of None to match the number of expected columns
  data = [[row[idx] if idx < len(row) else None for idx in range(len(columns.all_columns()))] for row in data]

  # initialize dataframe
  df = DataFrame(data, columns=columns.all_columns(), dtype=object)

  if not df.empty:
    # Ensure all None-like objects within the dataframe are replaced with None prior to validation
    df = df.astype(object)
    df = df.replace(NULL_VALUES, value=None)

    newly_typed_rows = []

    df.apply(
      apply_model,
      axis=1,
      types_model=types_model,
      typed_rows=newly_typed_rows,
    )

    df = concat(
      newly_typed_rows,
      axis=1,
    ).T

    # Ensure columns are in the order defined in their column names enumeration
    df = df[columns.all_columns()]

  df = df.set_index(
    columns.__index_items__,
    drop=False,
    verify_integrity=True,
  )

  return df


def apply_model(row: Series, types_model: type[CustomBaseModel], typed_rows: list[Series]) -> Series:
  model = types_model.model_validate(row.to_dict())

  model_dict = model.model_dump()

  typed_rows.append(Series(model_dict, name=row.name, dtype=object))

  return row
