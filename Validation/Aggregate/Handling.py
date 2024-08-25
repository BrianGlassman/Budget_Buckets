"""
Process the input data
"""

# General imports
from copy import deepcopy
from decimal import Decimal


# Project imports
from BaseLib import utils
from BaseLib.money import Money
from CategoryList import categories


def handle(log_data, date_ranges):
    # Prep the aggregate with date ranges and 0 totals
    data: list[dict] = deepcopy(date_ranges)
    for item in data:
        item['data'] = {cat: Money(0, 0) for cat in categories}

    # Aggregate the log data
    for item in log_data:
        category = item['My Category']['My Category']
        if category == '': continue
        date = utils.parse_date(item['Final']['Date'])
        for data_item in data:
            if data_item['start'] <= date <= data_item['end']:
                data_item['data'][category] += item['Final']['Amount']
                break
        else:
            raise RuntimeError(f"Couldn't find a date range to aggregate with: {item}")

    # Convert dates and amounts back to strings to match validation data
    for item in data:
        for key in ['start', 'end']:
            item[key] = utils.unparse_date(item[key])
    
    return data