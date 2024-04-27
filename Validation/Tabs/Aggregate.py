"""
Validates the "Aggregate" tabs in the Excel sheet
"""

# General imports
import datetime
import json


# Project imports
from BaseLib import utils
from Validation.Handling.Log import handle as handle_log
from Validation.Handling.Aggregate import handle


# Typing
Item = dict[str, dict[str, str]]


with open('Validation/Data/aggregate_2024_validation.json', 'r') as f:
    validation = json.load(f)

# Get the date ranges from validation
# FIXME will these just always be months?
date_ranges: list[dict[str, datetime.date]] = [
    {k:utils.parse_date(item[k]) for k in ('start', 'end')}
    for item in validation
]

with open('Validation/Data/log_2024.json', 'r') as f:
    data = handle(handle_log(json.load(f)), date_ranges)


assert data == validation
print("Validation complete")