from typing import Callable

import numpy as np
import pandas as pd


def set_cleaner(analysis: 'str') -> Callable[[pd.DataFrame], pd.DataFrame]:
    """Set the appropriate data cleaner based on the analysis.

    Args:
        extension (str): Characterization analysis.

    Returns:
        Callable[[Path], pd.DataFrame]: Data cleaner function.
    """
    cleaners = {
        'asap': clean_asap,
        'dls-size': clean_dls_size,
        'fls-em': clean_fls,
        'fls-exc': clean_fls,
        'ftir': clean_ftir,
        'solid-uv': clean_solid_uv,
        'tga': clean_tga,
        'xrd': clean_xrd,
        'xrf': clean_xrf,
    }
    return cleaners.get(analysis)


def clean_asap(raw_data: pd.DataFrame) -> pd.DataFrame:
    clean_data = raw_data.iloc[28:, np.r_[16:20, 120:122]]
    clean_data.columns = [
        'relative_pressure_adsorption',
        'quantity_adsorbed',
        'relative_pressure_desorption',
        'quantity_desorbed',
        'pore_diameter',
        'log_diff_pore_volume',
    ]
    clean_data = clean_data.apply(pd.to_numeric)
    clean_data = clean_data.dropna(how='all')
    return clean_data


def clean_dls_size(raw_data: pd.DataFrame) -> pd.DataFrame:
    clean_data = raw_data.iloc[8:, 24:]
    clean_data = clean_data.apply(pd.to_numeric)
    clean_data.columns = [
        'particle_diameter',
        'size_per_surface',
        'size_per_volume',
        'size_per_number',
    ]
    return clean_data


def clean_fls(raw_data: pd.DataFrame) -> pd.DataFrame:
    clean_data = raw_data.iloc[21:].dropna(axis='columns')
    clean_data = clean_data.apply(pd.to_numeric)
    clean_data.columns = ['wavelength', 'intensity']
    return clean_data


def clean_ftir(raw_data: pd.DataFrame) -> pd.DataFrame:
    clean_data = raw_data.copy()
    clean_data.columns = ['wavenumber', 'transmittance']
    return clean_data


def clean_solid_uv(raw_data: pd.DataFrame) -> pd.DataFrame:
    clean_data = raw_data.copy()
    clean_data.columns = ['wavelength', 'absorbance']
    return clean_data


def clean_tga(raw_data: pd.DataFrame) -> pd.DataFrame:
    clean_data = raw_data.copy()
    clean_data = clean_data.drop(range(2))
    clean_data = clean_data.apply(pd.to_numeric)
    clean_data.columns = ['time', 'temperature', 'dta', 'tga']
    return clean_data


def clean_xrd(raw_data: pd.DataFrame) -> pd.DataFrame:
    clean_data = raw_data.copy()
    clean_data.columns = ['2theta', 'intensity']
    return clean_data


def clean_xrf(raw_data: pd.DataFrame) -> pd.DataFrame:
    clean_data = raw_data.copy()
    clean_data.columns = clean_data.iloc[0]
    clean_data = clean_data.drop(0)
    clean_data = clean_data.astype(
        {
            'result': 'float64',
            'detection_limit': 'float64',
            'intensity': 'float64',
            'w/o_normal': 'float64',
        }
    )
    return clean_data
