import logging
from pathlib import Path

import pandas as pd
from matplotlib import pyplot as plt

from mesil.config import Settings
from mesil.data.files import filter_extensions
from mesil.data.metadata import (
    get_analysis,
    get_fluorescence_type,
    get_synthesis_code,
)
from mesil.plotting.customize import FLS_xlim
from mesil.plotting.plotters import custom_xy_plotter


def main(
    data_folder: Path = Settings().paths.data.processed,
    plot_root=Settings().paths.figures,
):
    data_to_plot = [
        datafile
        for datafile in filter_extensions(data_folder, extensions=['.csv'])
    ]

    for datafile in data_to_plot:
        data = pd.read_csv(datafile, header=None)
        analysis = get_analysis(datafile)

        custom_xy_plotter(data=data, analysis=analysis)
        logging.info(f'Plotting {datafile} -> {output_path}')

        output_path = (
            plot_root
            / get_synthesis_code(datafile)
            / f'{analysis}-{datafile.stem}.png'
        )

        plt.savefig(output_path, dpi=300)

    logging.info('SUCCESS: plotted all files!')


if __name__ == '__main__':
    main()
