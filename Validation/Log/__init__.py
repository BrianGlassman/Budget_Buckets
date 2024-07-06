# General imports
import os as _os


# Project imports
from Validation import YearlyValidationSpec as _Spec
from BaseLib.utils import json_load
from .Handling import Item as LogItem


spec = _Spec(
    basedir=_os.path.dirname(__file__),
    tag="log",
)

def load_log_data():
    from .Handling import handle
    raw = []
    for data_path in spec.data_paths.values():
        raw.extend(json_load(data_path))
    data = handle(raw)
    return data

def load_log_validation():
    validation: list[LogItem] = []
    for validation_path in spec.validation_paths.values():
        validation.extend(json_load(validation_path))
    return validation