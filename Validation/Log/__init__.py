# General imports


# Project imports
from BaseLib.utils import json_load
from Loading.JSON import log_data_paths as data_paths, log_validation_paths as validation_paths
from .Handling import Item as LogItem


def load_log_data():
    from .Handling import handle
    raw = []
    for data_path in data_paths.values():
        raw.extend(json_load(data_path))
    data = handle(raw)
    return data

def load_log_validation():
    validation: list[LogItem] = []
    for validation_path in validation_paths.values():
        validation.extend(json_load(validation_path))
    return validation