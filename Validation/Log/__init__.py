# General imports
import os as _os


# Project imports
from .Handling import handle as handle_log, Item as LogItem


_basedir = _os.path.dirname(__file__)
log_data_path = _os.path.join(_basedir, 'log_2024.json')
log_validation_path = _os.path.join(_basedir, 'log_2024_validation.json')