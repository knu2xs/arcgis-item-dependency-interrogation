__title__ = "arcgis-item-dependency-interrogation"
__version__ = "0.1.0.dev0"
__author__ = "Joel McCune (https://github.com/knu2xs)"

__license__ = "Apache 2.0"

__copyright__ = "Copyright 2026 by Joel McCune (https://github.com/knu2xs)"

# add specific imports below if you want to organize your code into modules, which is mostly what I do
from . import config as config
from . import utils
from ._main import example_function, ExampleObject

__all__ = ["config", "example_function", "ExampleObject", "utils"]
