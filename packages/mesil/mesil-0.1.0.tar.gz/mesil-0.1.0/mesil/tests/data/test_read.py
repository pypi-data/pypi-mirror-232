from pathlib import Path

import pandas as pd
import pytest

from mesil.process.read import csv_reader, excel_reader, get_delimiter

test_csv_reader_data = [
    ('data/raw/fls-em/2023-05-15/DIC14.txt', None),
    ('data/raw/fls-exc/2023-04-19/DIC14.txt', None),
    ('data/raw/ftir/2023-04-18/DIC14.CSV', None),
    ('data/raw/solid-uv/2023-02-02/DIC3L.txt', None),
    ('data/raw/tga/2023-05-08/DIC14.txt', 31),
    ('data/raw/xrd/2023-04-14/DIC14.txt', None),
    ('data/raw/xrf/2023-02-07/DIC3L.csv', None),
]

test_get_delimiter_data = [
    ('data/raw/fls-em/2023-05-15/DIC14.txt', ','),
    ('data/raw/fls-exc/2023-04-19/DIC14.txt', ','),
    ('data/raw/ftir/2023-04-18/DIC14.CSV', ','),
    ('data/raw/solid-uv/2023-02-02/DIC3L.txt', '\t'),
    ('data/raw/tga/2023-05-08/DIC14.txt', '\t'),
    ('data/raw/xrd/2023-04-14/DIC14.txt', ','),
    ('data/raw/xrf/2023-02-07/DIC3L.csv', ','),
]


@pytest.mark.parametrize('csv_path, expected', test_get_delimiter_data)
def test_get_delimiter(csv_path, expected):
    assert get_delimiter(csv_path) == expected


@pytest.mark.parametrize('csv_path, skip_rows', test_csv_reader_data)
def test_csv_reader(csv_path, skip_rows):
    data = csv_reader(csv_path, skip_rows=skip_rows)

    assert isinstance(data, pd.DataFrame)


@pytest.mark.parametrize(
    'excel_path, engine',
    [
        (Path('data/raw/asap/2023-04-19/DIC14.XLS'), 'xlrd'),
        (Path('data/raw/dls-size/MC034_G0_A (1).xlsx'), 'openpyxl'),
    ],
)
def test_excel_reader(excel_path: str, engine: str):
    data = excel_reader(excel_path, engine=engine)
    assert isinstance(data, pd.DataFrame)
