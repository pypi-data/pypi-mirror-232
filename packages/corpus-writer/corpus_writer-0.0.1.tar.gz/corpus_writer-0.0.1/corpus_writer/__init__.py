__version__ = "0.0.1"

from .logger import LOG_FILE, file_logging, setup_logging
from .writer import DecisionFile

setup_logging()
file_logging()
