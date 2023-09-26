import os
from importlib.metadata import version
from pathlib import Path

__version__ = version("bobifi")

DATADIR = Path(os.path.abspath(os.path.dirname(__file__))) / "data"
