import pandas as pd
import pytest

from mesil.process.datafile import DataFile


@pytest.fixture(scope='function')
def data_file(datafile_args) -> pd.DataFrame:
    return DataFile(*datafile_args).read().clean().clean_data


@pytest.mark.parametrize(
    'datafile_args', [('data/raw/asap/2023-04-19/DIC14.XLS', 'asap')]
)
class TestASAP:
    def test_clean_asap_returns_correct_column_names(
        self, data_file: pd.DataFrame
    ):
        assert all(
            data_file.columns
            == [
                'relative_pressure_adsorption',
                'quantity_adsorbed',
                'relative_pressure_desorption',
                'quantity_desorbed',
                'pore_diameter',
                'log_diff_pore_volume',
            ]
        )

    def test_clean_asap_returns_correct_dtypes(self, data_file: pd.DataFrame):
        assert all(data_file.dtypes == 'float64')

    def test_clean_tga_nan_rows_should_be_false(self, data_file: pd.DataFrame):
        assert all(data_file.isnull().all(axis='columns') == False)


@pytest.mark.parametrize(
    'datafile_args',
    [
        ('data/raw/fls-em/2023-05-15/DIC14.txt', 'fls-em'),
        ('data/raw/fls-exc/2023-04-19/DIC14.txt', 'fls-exc'),
    ],
)
class TestFLS:
    def test_clean_fls_returns_correct_column_names(
        self, data_file: pd.DataFrame
    ):
        assert all(data_file.columns == ['wavelength', 'intensity'])

    def test_clean_fls_dtypes_should_be_float64(self, data_file: pd.DataFrame):
        assert all(data_file.dtypes == 'float64')

    def test_clean_fls_nan_columns_should_be_false(
        self, data_file: pd.DataFrame
    ):
        assert all(data_file.isnull().all() == False)


@pytest.mark.parametrize(
    'datafile_args', [('data/raw/ftir/2023-04-18/DIC14.CSV', 'ftir')]
)
class TestFTIR:
    def test_clean_ftir_returns_correct_column_names(
        self, data_file: pd.DataFrame
    ):
        assert all(data_file.columns == ['wavenumber', 'transmittance'])


@pytest.mark.parametrize(
    'datafile_args',
    [('data/raw/solid-uv/2023-02-02/DIC3L.txt', 'solid-uv')],
)
class TestSolidUV:
    def test_clean_solid_uv_returns_correct_column_names(
        self,
        data_file: pd.DataFrame,
    ):
        assert all(data_file.columns == ['wavelength', 'absorbance'])


@pytest.mark.parametrize(
    'datafile_args', [('data/raw/tga/2023-05-08/DIC14.txt', 'tga')]
)
class TestTGA:
    def test_clean_tga_returns_correct_column_names(
        self, data_file: pd.DataFrame
    ):
        assert all(data_file.columns == ['time', 'temperature', 'dta', 'tga'])

    def test_clean_tga_dtypes_should_be_float64(self, data_file: pd.DataFrame):
        assert all(data_file.dtypes == 'float64')


@pytest.mark.parametrize(
    'datafile_args', [('data/raw/xrd/2023-04-14/DIC14.txt', 'xrd')]
)
class TestXRD:
    def test_clean_xrd_returns_correct_column_names(
        self, data_file: pd.DataFrame
    ):
        assert all(data_file.columns == ['2theta', 'intensity'])


@pytest.mark.parametrize(
    'datafile_args', [('data/raw/xrf/2023-02-07/DIC3L.csv', 'xrf')]
)
class TestXRF:
    def test_clean_xrf_returns_correct_column_names(
        self, data_file: pd.DataFrame
    ):
        assert all(
            data_file.columns
            == [
                'component',
                'result',
                'unit',
                'detection_limit',
                'element_line',
                'intensity',
                'w/o_normal',
            ]
        )

    def test_clean_xrf_returns_correct_dtypes(self, data_file: pd.DataFrame):
        assert all(
            data_file.dtypes
            == [
                'object',
                'float64',
                'object',
                'float64',
                'object',
                'float64',
                'float64',
            ]
        )
