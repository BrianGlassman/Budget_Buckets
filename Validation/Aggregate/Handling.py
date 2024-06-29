"""
Process the input data
"""

# General imports
from copy import deepcopy
from decimal import Decimal


# Project imports
from BaseLib import utils
from CategoryList import categories


def handle(log_data, date_ranges):
    # Prep the aggregate with date ranges and 0 totals
    data: list[dict] = deepcopy(date_ranges)
    for item in data:
        item['data'] = {cat: Decimal('0.00') for cat in categories}

    # Aggregate the log data
    for item in log_data:
        category = item['My Category']['My Category']
        date = utils.parse_date(item['Final']['Date'])
        for data_item in data:
            if data_item['start'] <= date <= data_item['end']:
                data_item['data'][category] += Decimal(item['Final']['Amount'])

    # Convert dates and amounts back to strings to match validation data
    for item in data:
        for key in ['start', 'end']:
            item[key] = utils.unparse_date(item[key])
        for key in categories:
            item['data'][key] = str(item['data'][key])
    
    return data