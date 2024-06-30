# General imports
import os as _os
import json as _json


# Project imports
from .Handling import Item as LogItem


_basedir = _os.path.dirname(__file__)
_years = ['2023', '2024']
log_data_paths = [_os.path.join(_basedir, f'log_{year}.json') for year in _years]
log_validation_paths = [_os.path.join(_basedir, f'log_{year}_validation.json') for year in _years]

def load_log_data():
    from .Handling import handle
    raw = []
    for log_data_path in log_data_paths:
        with open(log_data_path, 'r') as f:
            raw.extend(_json.load(f))
    data = handle(raw)
    return data

def load_log_validation():
    validation: list[LogItem] = []
    for log_validation_path in log_validation_paths:
        with open(log_validation_path, 'r') as f:
            validation.extend(_json.load(f))
    return validation