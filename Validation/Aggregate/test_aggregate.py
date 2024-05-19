"""
Validates the "Aggregate" tabs in the Excel sheet
"""

# General imports
import datetime
import json


# Project imports
from BaseLib import utils
from Validation.Log import load_log_data
from Validation.Aggregate import handle_aggregate, aggregate_validation_path


def load():
    with open(aggregate_validation_path, 'r') as f:
        validation = json.load(f)

    # Get the date ranges from validation
    # FIXME will these just always be months?
    date_ranges: list[dict[str, datetime.date]] = [
        {k:utils.parse_date(item[k]) for k in ('start', 'end')}
        for item in validation
    ]
    
    log_data = load_log_data()
    data = handle_aggregate(log_data, date_ranges)
    
    return data, validation

def test_aggregate_duplication():
    data, validation = load()

    assert data == validation
    print("Validation complete")
