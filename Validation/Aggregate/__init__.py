# General imports
import os as _os


# Project imports
from .Handling import handle as handle_aggregate


_basedir = _os.path.dirname(__file__)
_years = ['2023', '2024']
aggregate_validation_paths = [_os.path.join(_basedir, f'aggregate_{year}_validation.json') for year in _years]


# Need validation (for now) to get the date ranges, so do loading in a weird way
_data = []
_validation = []
def load_aggregate():
    import datetime
    import json
    from BaseLib import utils
    from Validation.Log import load_log_data
    from .Handling import handle
    validation = []
    for aggregate_validation_path in aggregate_validation_paths:
        with open(aggregate_validation_path, 'r') as f:
            validation.extend(json.load(f))

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
