# General imports
import os as _os


# Project imports
from .Handling import handle as handle_aggregate


_basedir = _os.path.dirname(__file__)
aggregate_validation_path = _os.path.join(_basedir, 'aggregate_2024_validation.json')


# Need validation (for now) to get the date ranges, so do loading in a weird way
_data = []
_validation = []
def load_aggregate():
    import datetime
    import json
    from BaseLib import utils
    from Validation.Log import load_log_data
    from .Handling import handle
    with open(aggregate_validation_path, 'r') as f:
        validation = json.load(f)

    # Get the date ranges from validation
    # FIXME will these just always be months?
    date_ranges: list[dict[str, datetime.date]] = [
        {k:utils.parse_date(item[k]) for k in ('start', 'end')}
        for item in validation
    ]
    
    log_data = load_log_data()
    data = handle(log_data, date_ranges)
    
    _data.extend(data)
    _validation.extend(validation)

def load_aggregate_data():
    if not _data:
        load_aggregate()
    return _data

def load_aggregate_validation():
    if not _validation:
        load_aggregate()
    return _validation
