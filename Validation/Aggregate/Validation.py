"""
Validates the "Aggregate" tabs in the Excel sheet
"""

# General imports
import datetime
import json
import os


# Project imports
from BaseLib import utils
from Validation.Log import handle_log, log_data_path
from .Handling import handle


# Typing
Item = dict[str, dict[str, str]]


basedir = os.path.dirname(__file__)
with open(os.path.join(basedir, 'aggregate_2024_validation.json'), 'r') as f:
    validation = json.load(f)

# Get the date ranges from validation
# FIXME will these just always be months?
date_ranges: list[dict[str, datetime.date]] = [
    {k:utils.parse_date(item[k]) for k in ('start', 'end')}
    for item in validation
]

with open(log_data_path, 'r') as f:
    data = handle(handle_log(json.load(f)), date_ranges)


assert data == validation
print("Validation complete")