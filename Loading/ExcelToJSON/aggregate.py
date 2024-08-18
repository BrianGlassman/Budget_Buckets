# General imports

# Project imports
from BaseLib.CategoryList import categories
from BaseLib.money import Money
from BaseLib.utils import format_cell_value, json_dump
from Loading.OpenExcel import aggregate_sheets as sheets
# from Loading import aggregate_data_paths as data_paths # Note: no user input for aggregate
from Loading import aggregate_validation_paths as validation_paths

# Logging
from BaseLib.logger import delegate_print as print

# Typing
Item = dict[str, dict[str, str | Money]]
Category = str

# Necessary information
log_starts = {'2023': '9/1/2023', '2024': '1/1/2024'}


def process_year(year: str):
    sheet = sheets[year]
    # Cell C1, the first month of the logged period
    log_start = log_starts[year]
    # Do some manipulating so it looks like the CSV version
    raw_lines = [[format_cell_value(value) for value in row] for row in sheet.values]
    
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
    print("<No user input for Aggregate>")
    validation = handle_data("input", raw_lines, True)

    # Save to file
    print("<No user input for Aggregate>")
    save_to_file("validation", validation, validation_paths[year])


def handle_data(tag: str, raw_lines: list, validation: bool):
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
    print(f"{tag.capitalize()} parsing complete")
    return data


def save_to_file(tag: str, contents, outfile):
    json_dump(outfile, contents, 2)
    print(f"{tag.capitalize()} export complete")
    

# Call it this instead of "main" to make imports easier
def xls_to_json():
    from Loading import years
    from Loading.ExcelToJSON import is_json_stale
    for year in years:
        # data_stale = is_json_stale(...) # Note: no user input for aggregate
        val_stale = is_json_stale(
            tag=f"{year} validation",
            script_path=__file__,
            json_path=validation_paths[year]
        )
        if val_stale:
            process_year(year)


if __name__ == "__main__":
    xls_to_json()
