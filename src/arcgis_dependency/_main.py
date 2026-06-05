"""Main module for arcgis_dependency package."""

from typing import Union
from pathlib import Path

import pandas as pd

from .utils import get_logger

# configure module logging, the same logger as the package-level logger
logger = get_logger("arcgis_dependency", level="DEBUG", add_stream_handler=False)
    