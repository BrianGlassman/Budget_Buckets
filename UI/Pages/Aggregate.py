"""
Duplicates the "Aggregate" tabs in the Excel sheet
"""

# General imports
import csv
import dash
import datetime
from functools import partial


# Project imports
from CategoryList import categories


# Styling
style={'border': '1px solid grey'}


# General aliases
Row = partial(dash.html.Tr, style=style)
Header = partial(dash.html.Th, style=style)
Data = partial(dash.html.Td, style=style)


def load_data(log: list[dict[str, str]], date_ranges: list[tuple[str, str]]):
    """Generate aggregate data from the log data"""
    data = {date_range: {c:[] for c in categories} for date_range in date_ranges}

    # Map date objects (for comparison) to main dict
    mapper = {}
    for (start, stop), dct in data.items():
        start = datetime.datetime.strptime(start, '%m/%d/%Y').date()
        stop = datetime.datetime.strptime(stop, '%m/%d/%Y').date()
        mapper[(start, stop)] = dct
    
    # Add each item to the appropriate list
    # First two lines are header
    for line in log[2:]:
        date = datetime.datetime.strptime(line['Date'], '%m/%d/%Y').date()
        for (start, stop), dct in mapper.items():
            dct: dict[str, list]
            if start <= date <= stop:
                category = line['Category']
                dct[category].append(line['Amount'])

    # {(start, end): {category: value}}


def load_validation():
    """Get the validation data from the static file"""
    with open('aggregate_2024_validation.csv') as f:
        lines = list(csv.reader(f))
    
    # Remove empty lines
    lines = [line for line in lines if line]

    # Line 0 is ["Log Start", , date]
    # Line 1 is [Start, End, *categories, Total]
    # Check that category order is as-expected
    header = lines[1]
    assert header[0] == 'Start'
    assert header[1] == 'End'
    assert header[-1] == 'Total'
    assert header[2:-1] == categories, [f'{h}!={c}' for h, c in zip(header[2:], categories) if h!=c]

    # Last line is Totals
    line = lines[-1]
    assert line[0] == ''
    assert line[1] == 'Total'
    totals = {k:v for k,v in zip(categories, line[2:-1])}
    grand_total = line[-1]
    assert float(grand_total) == sum(float(v) for v in totals.values())

    # Remaining lines are data
    data = {} # {(start, end): {category: value}}
    for line in lines[2:-1]:
        start = line[0]
        end = line[1]
        vals = {k:v for k,v in zip(categories, line[2:-1])}
        total = line[-1]
        raise NotImplementedError("replace this line")
        assert money_equal(float(total), sum(float(v) for v in vals.values()))
        data[(start, end)] = vals
    
    return data
    
if __name__ == "__main__":
    validation = load_validation()
    from .Log import load_data as load_log
    log = load_log()
    data = load_data(log, list(validation.keys()))
