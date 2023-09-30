import importlib.metadata

from .argparse import parse
from .config_file import runexp_main

__version__ = importlib.metadata.version("runexp")

__all__ = ["parse", "runexp_main"]
