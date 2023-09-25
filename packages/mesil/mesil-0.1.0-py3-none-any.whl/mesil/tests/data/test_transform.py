from pathlib import Path

import pandas as pd
import pytest

from mesil.process.datafile import DataFile


@pytest.fixture(scope='function')
def data_file(datafile_args) -> pd.DataFrame:
    return DataFile(*datafile_args).read().clean().transform()


@pytest.mark.parametrize(
    'datafile_args',
    [
        ('data/raw/fls-em/2023-05-15/DIC14.txt', 'fls-em'),
        ('data/raw/fls-exc/2023-04-19/DIC14.txt', 'fls-exc'),
        ('data/raw/ftir/2023-04-18/DIC14.CSV', 'ftir'),
        ('data/raw/solid-uv/2023-02-02/DIC3L.txt', 'solid-uv'),
        ('data/raw/xrd/2023-04-14/DIC14.txt', 'xrd'),
        ('data/raw/xrf/2023-02-07/DIC3L.csv', 'xrf'),
        ('data/raw/asap/2023-04-19/DIC14.XLS', 'asap'),
    ],
)
def test_transform_nothing_returns_the_same_data(data_file: DataFile):
    pd.testing.assert_frame_equal(
        data_file.processed_data, data_file.clean_data
    )


@pytest.mark.parametrize(
    'datafile_args', [('data/raw/tga/2023-05-08/DIC14.txt', 'tga')]
)
def test_transform_tga_reverse_transformation(data_file: DataFile):
    transformed_weight_column = data_file.processed_data['weight']
    original_tga_column = data_file.clean_data['tga']
    reverse_tranformed_tga_column = (
        transformed_weight_column * original_tga_column.iloc[0]
    ) / 100
    pd.testing.assert_series_equal(
        original_tga_column, reverse_tranformed_tga_column, check_names=False
    )
