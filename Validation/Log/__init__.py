# General imports
import os as _os
import json as _json


# Project imports
from .Handling import Item as LogItem


_basedir = _os.path.dirname(__file__)
log_data_path = _os.path.join(_basedir, 'log_2024.json')
log_validation_path = _os.path.join(_basedir, 'log_2024_validation.json')

def load_log_data():
    from .Handling import handle
    with open(log_data_path, 'r') as f:
        data = handle(_json.load(f))
    return data

def load_log_validation():
    with open(log_validation_path, 'r') as f:
        validation: list[LogItem] = _json.load(f)
    return validation