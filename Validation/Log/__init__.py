# General imports
import os as _os


# Project imports
from BaseLib.utils import json_load
from .Handling import Item as LogItem


# Logging
from BaseLib.logger import delegate_print as print

_basedir = _os.path.dirname(__file__)
_years = ['2023', '2024']
log_data_paths = [_os.path.join(_basedir, f'log_{year}.json') for year in _years]
log_validation_paths = [_os.path.join(_basedir, f'log_{year}_validation.json') for year in _years]

def load_log_data():
    from .Handling import handle
    raw = []
    for log_data_path in log_data_paths:
        raw.extend(json_load(log_data_path))
    data = handle(raw)
    return data

def load_log_validation():
    validation: list[LogItem] = []
    for log_validation_path in log_validation_paths:
        validation.extend(json_load(log_validation_path))
    return validation