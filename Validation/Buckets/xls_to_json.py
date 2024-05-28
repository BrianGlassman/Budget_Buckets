# General imports
import datetime
import openpyxl
import openpyxl.worksheet._read_only
import os
import json


# Project imports
from CategoryList import categories
from BaseLib.utils import unparse_date, safe_open
from . import Types


# Alias for convenience
categories_plus_total = categories + ['total']


def format_value(value) -> str:
    """Convert an openpyxl Cell value to a string the same as in a CSV"""
    if value is None:
        return ''
    elif isinstance(value, datetime.datetime):
        return unparse_date(value)
    else:
        return str(value)


def assert_blank(raw_columns, c):
    assert all(v == '' for v in raw_columns[c])
    return c + 1


def make_ValueCapacityCritical(data_cols: list[tuple[str, ...]]) -> Types.ValueCapacityCritical:
    header = [
        "Value",
        "Capacity",
        "Is Crit",
    ]
    # First row is header, rest is data and totals
    assert header == [col[0] for col in data_cols]
    data_cols = [col[1:] for col in data_cols]

    ret = Types.ValueCapacityCritical()
    ret.value = {cat:val for cat,val in zip(categories_plus_total, data_cols[0])}
    ret.capacity = {cat:val for cat,val in zip(categories_plus_total, data_cols[1])}
    ret.is_critical = {cat:val for cat,val in zip(categories, data_cols[2])}
    assert data_cols[2][len(categories)] == ''
    return ret


def make_ChangeSet(data_cols: list[tuple[str, ...]]) -> Types.ChangeSet:
    header = [
        "Val Diff",
        "Set Val",
        "Cap Diff",
        "Set Cap",
        "Is Crit",
    ]
    # First row is header, rest is data and totals
    assert header == [col[0] for col in data_cols]
    data_cols = [col[1:] for col in data_cols]

    ret = Types.ChangeSet()
    ret.value_delta = {cat:val for cat,val in zip(categories_plus_total, data_cols[0])}
    ret.value_set = {cat:val for cat,val in zip(categories_plus_total, data_cols[1])}
    ret.capacity_delta = {cat:val for cat,val in zip(categories_plus_total, data_cols[2])}
    ret.capacity_set = {cat:val for cat,val in zip(categories_plus_total, data_cols[3])}
    return ret


def xls_to_json(filename, sheet_name: str):
    wb = openpyxl.load_workbook(filename=filename, read_only=True, data_only=True)
    sheet = wb[sheet_name]
    assert isinstance(sheet, openpyxl.worksheet._read_only.ReadOnlyWorksheet)
    # Do some manipulating so it looks like the CSV version
    raw_rows = [[format_value(value) for value in row] for row in sheet.values]
    raw_columns = list(zip(*raw_rows))

    c = 0
    try:
        # Categories are in the first few columns
        c = handle_categories(raw_columns, c)

        # Blank column
        c = assert_blank(raw_columns, c)

        # Initial values are the next few columns
        c, initial = handle_initial(raw_columns, c)

        # Blank column
        c = assert_blank(raw_columns, c)

        # Repeating pattern of months and transitions with blanks between
        while True:
            c, month, month_data, transition_data = handle_month_and_transition(raw_columns, c)
            if c >= len(raw_columns): break # Last column won't exist to be blank, so exit early
            c = assert_blank(raw_columns, c)
    except Exception:
        print(f"Failed with c = {c}")
        raise


def handle_categories(raw_columns, c):
    """Does not return the category list, because it should match CategoryList.categories"""
    columns = raw_columns[c:c+4]
    rows = list(zip(*columns))
    c += 4

    # First two rows are blank
    assert all(all(v == '' for v in row) for row in rows[0:2])

    # Next row is header
    header = ('Dir', 'Broad', 'Specific', 'Key')
    assert rows[2] == header

    # TODO handle Broand and Specific columns, not just Key (category)

    # Fourth column, starting in the fourth row, is categories
    # Ensure that content AND order match
    excel_categories = [cat for cat in columns[3][3:] if cat != '']
    assert excel_categories == categories

    return c


def handle_initial(raw_columns: list[tuple[str, str, str]], c: int) -> tuple[int, Types.ValueCapacityCritical]:
    columns = raw_columns[c:c+3]
    rows = list(zip(*columns))
    c += 3

    # First two rows are meta
    assert rows[0] == ('WARNING: Approximate values', '', '')
    assert rows[1] == ('Result', '', '')

    # Remainder is data (1 for header 1 per category, 1 for totals)
    cat_data = [column[2:2+1+len(categories_plus_total)] for column in columns]
    ret = make_ValueCapacityCritical(cat_data)

    return c, ret


def handle_month_and_transition(raw_columns, c) -> tuple[int, Types.month, Types.MonthFull, Types.TransitionFull]:
    # 17 columns for the month
    month_columns = raw_columns[c:c+17]
    month, month_data = handle_month(month_columns)
    c += 17

    # Blank column
    c = assert_blank(raw_columns, c)

    # 11 columns for the transition
    transition_columns = raw_columns[c:c+11]
    transition_data = handle_transition(transition_columns)
    c += 11

    return c, month, month_data, transition_data


def handle_month(columns: list[tuple[str, ...]]) -> tuple[Types.month, Types.MonthFull]:
    rows: list[tuple[str, ...]] = list(zip(*columns))
    ret = Types.MonthFull()
    r = 0

    # First cell is the month itself
    # Rest of that row is blank
    month = rows[r][0]
    assert all(v=='' for v in rows[r][1:])
    r += 1

    # Second row is descriptions
    descriptions = (
        "Initial bucket value",
        "Transaction totals for this month",
        "Bucket value after transactions",
        "Bucket capacity",
        "Difference between bucket value and capacity",
        "Movement from buckets to slush fund",
        "Bucket values after removing slush funds",
        "Difference between bucket value and capacity after removing slush funds",
        "Which buckets are critical (fill first)",
        "Amount needed to fill critical buckets to full",
        "Bucket values after refilling critical buckets",
        "Amount needed to fill non-critical buckets to full",
        "NC To Fill, but limited by slush fund",
        "Bucket values after refilling non-critical buckets",
        "Final bucket values",
        "", ""
    )
    assert rows[r] == descriptions
    r += 1

    # Third row is header
    header = (
        "Start",
        "Transactions",
        "After T",
        "Capacity",
        "Cap Diff",
        "Slush",
        "Before Fill",
        "S Cap Diff",
        "Is Crit",
        "Crit To Fill",
        "Crit Filled",
        "NC To Fill",
        "Scaled",
        "NC Filled",
        "Final",
        "Unfilled",
        "% Filled",
    )
    assert rows[r] == header
    r += 1

    # Then data and totals
    ret.columns = {
        column_name: {
            cat:val for cat,val in zip(categories_plus_total, column[r:])
        }
        for column_name, column in zip(header, columns)
    }
    r += len(categories_plus_total)

    # Two blank rows
    assert all(all(v == '' for v in row) for row in rows[r:r+2])
    r += 2

    # Intermediate values
    # First row has header, then blank
    assert rows[r][0] == "Intermediate"
    assert all(v=='' for v in rows[r][1:])
    # Only one intermediate value
    key = "Slush After Crit"
    assert rows[r+1] == tuple(['']*10 + [key] + ['']*6)
    val = rows[r+2][10]
    assert rows[r+2] == tuple(['']*10 + [val] + ['']*6)
    ret.intermediate = {key:val}
    r += 3

    # Blank row
    assert all(v=='' for v in rows[r])
    r += 1

    # Error checks
    # First row only has header cell
    assert rows[r][0] == "Error Check"
    assert all(v=='' for v in rows[r][1:])
    keys = tuple(
        ["Available", "Internal"] + ['']*3 +
        ["Slush"] + ['']*3 +
        ["Crit To Fill", "Slush After Crit", "NC To Fill", "Scaled to Fill"] + [''] +
        ["Final"] + ['']*2
    )
    assert rows[r+1] == keys
    ret.error_checks = {}
    for key, val in zip(keys, rows[r+2]):
        if key == '':
            assert val == ''
        else:
            ret.error_checks[key] = val
    r += 3

    return month, ret


def handle_transition(columns: list[tuple[str, ...]]) -> Types.TransitionFull:
    rows: list[tuple[str, ...]] = list(zip(*columns))
    ret = Types.TransitionFull()
    r = 0

    # First row is blank
    assert all(v=='' for v in rows[r])
    r += 1

    # Second row is meta-header
    meta_header = tuple(
        ["Previous Month"] + ['']*2 +
        ["Changes"] + ['']*4 + 
        ["Result"] + ['']*2
    )
    assert rows[r] == meta_header
    r += 1
    
    # Then data and totals (add one for header)
    data_cols = [column[r:r+1+len(categories_plus_total)] for column in columns]
    ret.end_previous = make_ValueCapacityCritical(data_cols[:3])
    ret.changes = make_ChangeSet(data_cols[3:-3])
    ret.start_next = make_ValueCapacityCritical(data_cols[-3:])
    r += 1+len(categories_plus_total)

    # Two blank rows
    assert all(all(v == '' for v in row) for row in rows[r:r+2])
    r += 2

    # Intermediate values (none, so just empty rows)
    assert all(all(v == '' for v in row) for row in rows[r:r+3])
    r += 3

    # Blank row
    assert all(v=='' for v in rows[r])
    r += 1

    # Error checks
    # Only one used column
    assert rows[r+0] == tuple(['']*8 + ["Error Check"] + ['']*2)
    key = "Total"
    assert rows[r+1] == tuple(['']*8 + [key] + ['']*2)
    val = rows[r+2][8]
    assert rows[r+2] == tuple(['']*8 + [val] + ['']*2)
    ret.error_checks = {key:val}
    r += 3

    return ret


def save_to_file(contents, filename):
    # Output to file
    outfile = os.path.join(os.path.dirname(__file__), filename)
    with safe_open(outfile, 'w') as f:
        json.dump(contents, f, indent=2)
    print("Export complete")


if __name__ == "__main__":
    sheet_name = "Buckets"
    xls_to_json("Budget_Buckets.xlsm", sheet_name)
