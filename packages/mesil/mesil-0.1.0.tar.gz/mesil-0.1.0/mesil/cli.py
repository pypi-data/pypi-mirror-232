import importlib.metadata
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.progress import (
    Progress,
    TextColumn,
    TimeRemainingColumn,
    MofNCompleteColumn,
    BarColumn,
)

from mesil.process.analysis import infer_analysis
from mesil.process.datafile import (
    SUPPORTED_EXTENSIONS,
    Analysis,
    DataFile,
)

typer.rich_utils.STYLE_HELPTEXT = ""
def docstr_callback():
    """
    Process and plot scientific data from various analyses (equipment specific).\n
    \b
    - [green](asap)[/green] Surface Area and Porosity: [purple]Micromeritics ASAP 2020[/purple] 
    - [green](fls-em, fls-exc)[/green] Fluorescence Spectroscopy: [purple]Edinburgh FLS980[/purple] 
    - [green](ftir)[/green] Infrared Spectroscopy: [purple]Varian 600 FTIR[/purple] 
    - [green](tga)[/green] Thermogravimetric: [purple]Shimadzu DTG-60/60H[/purple] 
    - [green](xrd)[/green] X-Ray diffraction: [purple]Rigaku Miniflex II[/purple] 
    - [green](xrf)[/green] X-Ray fluorescence: [purple]Rigaku Supermini 200[/purple] 
    """


app = typer.Typer(rich_markup_mode='rich', callback=docstr_callback)


def version_callback(value: bool):
    if value:
        version = importlib.metadata.version('mesil')
        typer.echo(f'mesil {version}')
        raise typer.Exit()


@app.callback(invoke_without_command=False)
def version(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option(
            '--version', callback=version_callback, help='Show current version'
        ),
    ] = False,
):
    pass


@app.command()
def process(
    path: Annotated[
        Path,
        typer.Argument(
            help='[green]File or directory[/green] with data :file_folder:.',
            show_default='Current directory',
            exists=True,
        ),
    ] = Path.cwd(),
    analysis: Annotated[
        Analysis,
        typer.Argument(
            help='[red]Analysis[/red] to process :microscope:.',
            show_default='Infer from `dir_or_file`',
            case_sensitive=False,
        ),
    ] = Analysis.infer,
    output: Annotated[
        Path,
        typer.Option(
            '--output',
            '-o',
            help='[blue]Export[/blue] results in the given output path :file_folder:.',
            show_default=False,
        ),
    ] = '',
):
    """
    Process analysis data from a file or multiple files in a directory.

    If --output is passed, data will be exported in the provided path,
    otherwise in dir_or_file.
    """
    console = Console()

    if path.is_file():
        infered_analysis = (
            infer_analysis(path) if analysis == 'infer' else analysis
        )
        data_file = DataFile(path=path, analysis=infered_analysis)
        data_file.read().clean().transform().export(output=output)
        console.log(f'[green bold]✅ Success![/] Exported {data_file._output}')
        return

    with Progress(
        TextColumn('[progress.description]{task.description}'),
        BarColumn(),
        MofNCompleteColumn(),
        TimeRemainingColumn()
    ) as progress:
        glob = [p for p in path.glob('**/*') if p.suffix.lower() in SUPPORTED_EXTENSIONS]
        total_processed = 0
        for file in progress.track(glob, description='Processing data...'):
            if file.suffix.lower() in SUPPORTED_EXTENSIONS:
                infered_analysis = (
                    infer_analysis(file) if analysis == 'infer' else analysis
                )
                data_file = DataFile(path=file, analysis=infered_analysis)
                data_file.read().clean().transform().export(output=output)
                total_processed += 1

    console.print(
        f'[green bold]✅ Success![/] Processed {total_processed} files'
    )


@app.command()
def plot():
    ...
