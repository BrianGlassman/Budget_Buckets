# General imports

# Project imports
from BaseLib.utils import json_load
from Loading import log_data_paths as data_paths, log_validation_paths as validation_paths
from PreProcessLogs import Item as LogItem, pre_process
from Categorize import categorize


def load_log_data():
    raw = []
    for data_path in data_paths.values():
        raw.extend(json_load(data_path))
    data = pre_process(raw)
    data = categorize(data)
    return data

def load_log_validation():
    validation: list[LogItem] = []
    for validation_path in validation_paths.values():
        validation.extend(json_load(validation_path))
    return validation