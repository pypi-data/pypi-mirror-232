from pathlib import Path

from mesil.process.datafile import SUPPORTED_ANALYSES


def infer_analysis(path: Path):
    return next(iter(set(SUPPORTED_ANALYSES).intersection(path.parts)))
