from pathlib import Path

import pandas as pd
import pytest

from mesil.process.datafile import DataFile

test_datafile_read_csv_data = [
    ('data/raw/fls-em/2023-05-15/DIC14.txt', 'fls-em'),
    ('data/raw/fls-exc/2023-04-19/DIC14.txt', 'fls-exc'),
    ('data/raw/ftir/2023-04-18/DIC14.CSV', 'ftir'),
    ('data/raw/solid-uv/2023-02-02/DIC3L.txt', 'solid-uv'),
    ('data/raw/tga/2023-05-08/DIC14.txt', 'tga'),
    ('data/raw/xrd/2023-04-14/DIC14.txt', 'xrd'),
    ('data/raw/xrf/2023-02-07/DIC3L.csv', 'xrf'),
]


class TestDataFile:
    def test_raise_error_file_not_found(self):
        with pytest.raises(FileNotFoundError, match='No such file .*'):
            DataFile(path='xpto.txt', analysis='tga')

    def test_raise_error_is_directory(self):
        with pytest.raises(
            ValueError, match='Attribute path should be a file, found dir .*'
        ):
            DataFile(path='mesil/', analysis='tga')

    def test_raise_error_extension_not_supported(self):
        with pytest.raises(
            ValueError, match='Extension .* not supported, try one of .*'
        ):
            DataFile(path='pyproject.toml', analysis='tga')

    def test_raise_error_analysis_not_supported(self):
        with pytest.raises(ValueError, match='.* is not a valid Analysis'):
            DataFile(path='data/raw/xrf/2023-02-07/DIC3L.csv', analysis='eds')

    def test_uppercase_analysis_validation(self):
        data_file = DataFile(
            path=test_datafile_read_csv_data[0][0], analysis='FLS-EM'
        )
        assert data_file.analysis == 'fls-em'

    @pytest.mark.parametrize('csv_path, analysis', test_datafile_read_csv_data)
    def test_datafile_read_csv(self, csv_path: str, analysis: str):
        data_file = DataFile(path=csv_path, analysis=analysis).read()
        assert isinstance(data_file.raw_data, pd.DataFrame)

    @pytest.mark.parametrize(
        'excel_path, analysis',
        [
            ('data/raw/asap/2023-04-19/DIC14.XLS', 'asap'),
            ('data/raw/dls-size/MC034_G0_A (1).xlsx', 'dls-size'),
        ],
    )
    def test_datafile_read_excel(self, excel_path: str, analysis: str):
        data_file = DataFile(
            path='data/raw/asap/2023-04-19/DIC14.XLS', analysis='asap'
        ).read()
        assert isinstance(data_file.raw_data, pd.DataFrame)

    def test_datafile_export_when_output_is_none(self):
        test_path = Path('data/raw/asap/2023-04-19/DIC14.XLS')
        data_file = (
            DataFile(path=test_path, analysis='asap')
            .read()
            .clean()
            .transform()
            .export()
        )
        assert Path(
            test_path.parent, 'processed', 'asap', 'DIC14.csv'
        ).exists()

    def test_datafile_export_when_output_is_passed(self, output='data'):
        test_path = Path('data/raw/asap/2023-04-19/DIC14.XLS')
        data_file = (
            DataFile(test_path, 'asap')
            .read()
            .clean()
            .transform()
            .export(output)
        )
        assert Path(output, 'processed', 'asap', 'DIC14.csv').exists()
