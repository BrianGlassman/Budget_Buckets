# General imports
from decimal import Decimal
import datetime
import openpyxl
import openpyxl.worksheet._read_only
import os
import json


# Project imports
from CategoryList import categories
from BaseLib.utils import unparse_date, safe_open


# Typing
Item = dict[str, dict[str, str]]


def format_value(value) -> str:
    """Convert an openpyxl Cell value to a string the same as in a CSV"""
    if value is None:
        return ''
    elif isinstance(value, datetime.datetime):
        return unparse_date(value)
    else:
        return str(value)


def xls_to_json(filename, sheet_name: str, log_start: str):
    """
    log_start: Cell C1, the first month of the logged period
    """
    wb = openpyxl.load_workbook(filename=filename, read_only=True, data_only=True)
    sheet = wb[sheet_name]
    assert isinstance(sheet, openpyxl.worksheet._read_only.ReadOnlyWorksheet)
    # Do some manipulating so it looks like the CSV version
    raw_lines = [[format_value(value) for value in row] for row in sheet.values]
    
    # First line is meta-header
    # FIXME don't hard-code date
    meta_header = ['Log Start', '', log_start]
    meta_header += [''] * (len(raw_lines[0]) - len(meta_header))
    assert raw_lines[0] == meta_header
    print("Meta-header as-expected")

    # Second line is true header
    # Ensure category order is as-expected
    header = raw_lines[1]
    assert header[0:2] == ['Start', 'End']
    assert header[2:-1] == categories, [f'{h}!={c}' for h, c in zip(header[2:], categories) if h!=c]
    assert header[-1] == 'Total'
    print("Header as-expected")

    # Last line is Totals
    totals_line = raw_lines[-1]
    assert totals_line[0] == ''
    assert totals_line[1] == 'Total'
    totals = {k:v for k,v in zip(categories, totals_line[2:-1])}
    grand_total = totals_line[-1]
    # FIXME use money type
    assert round(float(grand_total), 2) == round(sum(float(v) for v in totals.values()), 2)
    print("Totals line as-expected")

    # Remaining lines are data
    validation = handle_data(raw_lines, True)

    # Save to file
    base_filename = sheet_name.replace(' ', '_').lower()
    save_to_file(validation, base_filename + "_validation.json")


def handle_data(raw_lines: list, validation: bool):
    assert validation, "No non-validation data for Aggregate"

    # Remaining lines are data
    data = [] # [{start: date, end: date, data: {category: value}}]
    for raw_line in raw_lines[2:-1]:
        item = {}
        item['start'], item['end'] = raw_line[0:2]
        vals = {}
        for k,v in zip(categories, raw_line[2:-1]):
            # Enforce consistent amount formatting
            v = v.replace('$', '').replace(',', '')
            if v == '':
                assert k == 'Override'
            else:
                v = str(Decimal(v).quantize(Decimal('0.01')))
            vals[k] = v
        total = Decimal(raw_line[-1]).quantize(Decimal('0.01'))
        assert total == sum(Decimal(v) for v in vals.values())
        item['data'] = vals
        data.append(item)
    print("Data parsing complete")
    return data


def save_to_file(contents, filename):
    # Output to file
    outfile = os.path.join(os.path.dirname(__file__), filename)
    with safe_open(outfile, 'w') as f:
        json.dump(contents, f, indent=2)
    print("Export complete")


if __name__ == "__main__":
    for year, log_start in [('2023', '9/1/2023'), ('2024', '1/1/2024')]:
        print(year)
        xls_to_json("Budget_Buckets.xlsm", f"Aggregate {year}", log_start=log_start)
