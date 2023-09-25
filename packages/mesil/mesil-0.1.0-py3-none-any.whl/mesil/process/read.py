import csv
from pathlib import Path
from typing import Callable, Optional, Union

import openpyxl
import pandas as pd
import xlrd


def get_delimiter(data_file: Path, bytes=22000) -> str:
    """Detect file delimiter in csv files.

    Args:
        data_file (Path): Path to file.
        bytes (int, optional): Bytes chunk to evaluate. Defaults to 22000.

    Returns:
        str: File delimiter.
    """
    sniffer = csv.Sniffer()
    data = open(data_file, 'r', encoding='latin1').read(bytes)
    delimiter = sniffer.sniff(data).delimiter
    return delimiter


def csv_reader(
    data_file: Union[Path, str], skip_rows: Optional[int] = None, engine=None
) -> pd.DataFrame:
    """Reads a csv file.

    Args:
        data_file (Path): Path to file.

    Returns:
        pd.DataFrame: Tabular data contained in the csv file.
    """
    delimiter = get_delimiter(data_file)
    return pd.read_csv(
        data_file,
        sep=delimiter,
        header=None,
        encoding='latin1',
        skiprows=skip_rows,
        engine=engine,
    )


def excel_reader(
    data_file: Path,
    skip_rows: Optional[int] = None,
    engine: str = 'xlrd',
) -> pd.DataFrame:
    """Reads a single-sheet excel file.

    Args:
        data_file (Path): Path to file.

    Returns:
        pd.DataFrame: Tabular data contained in the excel file.
    """
    if data_file.suffix.lower() == '.xls':
        wb = xlrd.open_workbook(data_file, encoding_override='iso-8859-1')
    elif data_file.suffix.lower() == '.xlsx':
        wb = openpyxl.load_workbook(data_file)
    return pd.read_excel(wb, skiprows=skip_rows, engine=engine)


def set_reader(extension: str) -> Callable[[Path], pd.DataFrame]:
    """Set the appropriate data reader based on the file extension.

    Args:
        extension (str): Data file extension.

    Returns:
        Callable[[Path], pd.DataFrame]: Data reader function.
    """
    readers = {
        '.csv': csv_reader,
        '.txt': csv_reader,
        '.xls': excel_reader,
        '.xlsx': excel_reader,
    }
    return readers.get(extension.lower())
