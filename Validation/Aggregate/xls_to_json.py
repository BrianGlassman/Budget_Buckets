# General imports
import datetime
import openpyxl
import openpyxl.worksheet._read_only


# Project imports
from Validation.Aggregate import spec
from CategoryList import categories
from BaseLib.money import Money
from BaseLib.utils import unparse_date, json_dump


# Logging
from BaseLib.logger import delegate_print as print

# Typing
Item = dict[str, dict[str, str | Money]]
Category = str

# Necessary information
log_starts = {'2023': '9/1/2023', '2024': '1/1/2024'}

def format_value(value) -> str:
    """Convert an openpyxl Cell value to a string the same as in a CSV"""
    if value is None:
        return ''
    elif isinstance(value, datetime.datetime):
        return unparse_date(value)
    else:
        return str(value)


def _xls_to_json(year: str):
    # Cell C1, the first month of the logged period
    log_start = log_starts[year]
    sheet_name = f"Aggregate {year}"
    wb = openpyxl.load_workbook(filename=spec.excel_path, read_only=True, data_only=True)
    sheet = wb[sheet_name]
    assert isinstance(sheet, openpyxl.worksheet._read_only.ReadOnlyWorksheet)
    # Do some manipulating so it looks like the CSV version
    raw_lines = [[format_value(value) for value in row] for row in sheet.values]
    
    # First line is meta-header
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
    totals = {k:Money.from_dollars(v) for k,v in zip(categories, totals_line[2:-1])}
    grand_total = Money.from_dollars(totals_line[-1])
    assert grand_total == sum(totals.values())
    print("Totals line as-expected")

    # Remaining lines are data
    validation = handle_data(raw_lines, True)

    # Save to file
    save_to_file(validation, spec.validation_paths[year])


def handle_data(raw_lines: list, validation: bool):
    assert validation, "No non-validation data for Aggregate"

    # Remaining lines are data
    data = [] # [{start: date, end: date, data: {category: value}}]
    for raw_line in raw_lines[2:-1]:
        item = {}
        item['start'], item['end'] = raw_line[0:2]
        vals: dict[Category, Money] = {}
        for category, amount in zip(categories, raw_line[2:-1]):
            # Enforce consistent amount formatting
            vals[category] = Money.from_dollars(amount)
        total = Money.from_dollars(raw_line[-1])
        assert total == sum(vals.values())
        item['data'] = vals
        data.append(item)
    print("Data parsing complete")
    return data


def save_to_file(contents, outfile):
    json_dump(outfile, contents, 2)
    print("Export complete")


def xls_to_json():
    from Validation import is_json_stale
    # No data JSON, only validation
    # FIXME, actually, uses Log data
    for year in spec.years:
        print(year)
        if is_json_stale(
            spec.excel_path,
            spec.export_script_path,
            spec.validation_paths[year]
        ):
            # FIXME don't hard-code date
            _xls_to_json(year)

if __name__ == "__main__":
    xls_to_json()

