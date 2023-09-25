from typing import Any, Dict, Optional

import matplotlib.pyplot as plt
import pandas as pd
from numpy import ScalarType
from numpy.typing import ArrayLike

from mesil.data.select import get_selector
from mesil.plotting.customize import axes_from_style_sheet, customizer


def xy_plotter(
    x: ArrayLike,
    y: ArrayLike,
    ax: Optional[plt.Axes] = None,
    params: Dict[str, Any] = dict(),
) -> plt.Axes:
    """Plot y versus x graphs as lines and/or markers.

    Args:
        ax (plt.Axes): Axes element, which will contain figure elements.
        xdata (npt.ArrayLike): Horizontal axis data, can be n-dimensional.
        ydata (npt.ArrayLike): Vertical axis data, can be n-dimensional.
        params (typing.Dict[str, Any]): Parameters to customize the plot.

    Returns:
        plot (plt.Axes): Axes containing plotted figure elements.
    """
    if not ax:
        ax = plt.gca()
    ax.plot(x, y, **params)
    return ax


def custom_xy_plotter(
    data: pd.DataFrame,
    analysis: str,
    ax: Optional[plt.Axes] = None,
    style_sheet: Optional[str] = 'default',
    params: Dict[str, Any] = dict(),
) -> plt.Axes:
    if not ax and style_sheet:
        ax = axes_from_style_sheet(style_sheet)
    customizer(analysis)
    selector = get_selector(analysis)(data)
    return xy_plotter(**selector, ax=ax, params=params)
