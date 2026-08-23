from dataclasses import dataclass, field
from typing import List

import pandas as pd


@dataclass
class CsvSettings:
    encoding: str = "utf-8"
    separator: str = ","
    decimal_separator: str = "."
    first_row_has_header: bool = True


@dataclass
class ColumnSettings:
    source_name: str
    import_column: bool = True
    result_name: str = ""
    data_type: str = "string"
    datetime_format: str = ""


@dataclass
class ImportSettings:
    csv: CsvSettings = field(default_factory=CsvSettings)
    columns: List[ColumnSettings] = field(default_factory=list)


def import_csv(filename: str, settings: ImportSettings) -> pd.DataFrame:
    """Read a CSV file and apply the column settings selected by the user."""
    dataframe = pd.read_csv(
        filename,
        encoding=settings.csv.encoding,
        sep=settings.csv.separator,
        decimal=settings.csv.decimal_separator,
        header=0 if settings.csv.first_row_has_header else None,
    )

    if not settings.csv.first_row_has_header:
        dataframe.columns = [f"Column{index + 1}" for index in range(len(dataframe.columns))]

    return apply_column_settings(dataframe, settings.columns)


def apply_column_settings(
    dataframe: pd.DataFrame, columns: List[ColumnSettings]
) -> pd.DataFrame:
    """Apply column selection, names and types to an already read DataFrame."""
    selected_columns = [column for column in columns if column.import_column]

    dataframe = dataframe[[column.source_name for column in selected_columns]].copy()

    for column in selected_columns:
        series = dataframe[column.source_name]

        if column.data_type == "string":
            series = series.astype("string")
        elif column.data_type == "integer":
            series = pd.to_numeric(series).astype("Int64")
        elif column.data_type == "float":
            series = pd.to_numeric(series).astype(float)
        elif column.data_type == "boolean":
            series = series.astype("boolean")
        elif column.data_type == "datetime":
            date_format = column.datetime_format or None
            series = pd.to_datetime(series, format=date_format, exact=False)

        dataframe[column.source_name] = series

    dataframe.columns = [column.result_name or column.source_name for column in selected_columns]
    return dataframe
