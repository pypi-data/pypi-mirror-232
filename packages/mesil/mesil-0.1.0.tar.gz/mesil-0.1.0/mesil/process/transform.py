from typing import Callable

import pandas as pd


def set_transformer(analysis: str) -> Callable[[pd.DataFrame], pd.DataFrame]:
    """Set the appropriate data transformer function based on the analysis.

    Args:
        analysis (str): Characterization analysis.

    Returns:
        Callable[[Path], pd.DataFrame]: Data cleaner function.
    """
    transformers = {
        'tga': transform_tga,
    }
    return transformers.get(analysis, transform_nothing)


def transform_tga(data: pd.DataFrame) -> pd.DataFrame:
    copy = data.copy()
    copy['weight'] = (copy['tga'] / copy['tga'].iloc[0]) * 100
    return copy


def transform_nothing(data: pd.DataFrame) -> pd.DataFrame:
    return data
