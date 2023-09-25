from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Union

import matplotlib.pyplot as plt
from process.datafile import PathLike


def axes_from_style_sheet(style_sheet: PathLike) -> plt.Axes:
    """Generates a style sheet's based axes.

    Args:
        style_sheet (PathLike): Style sheet's path.

    Returns:
        plt.Axes: Customized axes.
    """
    plt.style.use(style_sheet)
    return plt.axes()


def default_customization(ax: plt.Axes, analysis: str) -> plt.Axes:
    params = get_analysis_default_parameters(analysis)()
    ax.set_xlim(params['xlim'])
    ax.set_xlabel(params['xlabel'])
    ax.set_ylabel(params['ylabel'])
    return ax


def get_analysis_default_parameters(
    analysis: str,
) -> Dict[str, Any]:
    parameter_generators = {
        'asap-bjh': asap_bjh_parameters,
        'asap-bet': asap_bet_parameters,
        'fls-em': fls_em_parameters,
        'fls-exc': fls_exc_parameters,
        'ftir': ftir_parameters,
        'solid-uv': solid_uv_parameters,
        'tga': tga_parameters,
        'xrd': xrd_parameters,
    }
    parameters = parameter_generators.get(analysis)
    return parameters


@dataclass
class PlotParameters(ABC):
    xcolumn: Union[str, int]
    ycolumn: Union[str, int]
    xlim: tuple
    xlabel: str
    ylabel: str
    
    

def asap_bet_parameters() -> Dict[str, Any]:
    return dict(
        xlim=(0, 1),
        xlabel=r'Relative Pressure (P/P_{0})',
        ylabel=r'Quantity Adsorbed (cm^{3}/g STP)',
    )


def asap_bjh_parameters() -> Dict[str, Any]:
    return dict(
        xlim=(2, 10),
        xlabel=r'Pore diamater (nm)',
        ylabel=r'dV/dlog(D) Pore Volume (cm^{3}/g)',
    )


def fls_em_parameters() -> Dict[str, Any]:
    return dict(
        xlim=(450, 750), xlabel=r'Wavelength (nm)', ylabel=r'Intensity (a.u.)'
    )


def fls_exc_parameters() -> Dict[str, Any]:
    return dict(
        xlim=(250, 575), xlabel=r'Wavelength (nm)', ylabel=r'Intensity (a.u.)'
    )


def ftir_parameters() -> Dict[str, Any]:
    return dict(
        xlim=(4000, 500),
        xlabel=r'Wavenumber (cm$^{-1}$)',
        ylabel=r'Transmittance (%)',
    )


def solid_uv_parameters() -> Dict[str, Any]:
    return dict(
        xlim=(200, 800), xlabel=r'Wavelength (nm)', ylabel=r'Absorbance (a.u.)'
    )


def tga_parameters() -> Dict[str, Any]:
    return dict(
        xlim=(30, 600), xlabel=r'Temperature ($^\circ$C)', ylabel=r'Weight (%)'
    )


def xrd_parameters() -> Dict[str, Any]:
    return dict(
        xlim=(1.2, 6.0),
        xlabel=r'2{\theta} (degrees)',
        ylabel=r'Intensity (a.u.)',
    )
