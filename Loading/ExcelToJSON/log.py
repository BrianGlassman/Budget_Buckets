# General imports

# Project imports
from BaseLib.CategoryList import categories
from BaseLib.money import Money
from BaseLib.utils import format_cell_value, json_dump
from Loading.OpenExcel import log_sheets as sheets
from Loading.JSON import log_data_paths as data_paths
from Loading.JSON import log_validation_paths as validation_paths

# Logging
from BaseLib.logger import delegate_print as print

# Typing
Item = dict[str, dict[str, str | Money | None]]


def process_year(year: str):
    sheet = sheets[year]

    # Do some manipulating so it looks like the CSV version
    raw_lines = [[format_cell_value(value) for value in row] for row in sheet.values]

    # First line is meta-header
    meta_header = (
        ['Imported - Untouched from base'] + ['']*5 +
        ['Account'] +
        ['Override - Changes from base'] + ['']*5 +
        ['Final - Values with overrides, to be used for calculation'] + ['']*5 +
        ['My Category', 'E', 'Comment']
    )
    assert raw_lines[0] == meta_header
    print("Meta-header as-expected")

    # Second line is section headers
    section_header_template = ["Date", "Description", "Original Description", "Category", "Amount", "Status"]
    section_headers = (
        [x+'_i' for x in section_header_template] +
        ['Account'] +
        [x+'_o' for x in section_header_template] +
        section_header_template +
        ['My Category', 'E', 'Comment']
    )
    assert raw_lines[1] == section_headers
    print("Section headers as-expected")

    # Remaining lines are data
    data = handle_data("user input", raw_lines, section_header_template, is_validation=False)
    validation = handle_data("validation", raw_lines, section_header_template, is_validation=True)

    # Save to file
    save_to_file("user input", data, data_paths[year])
    save_to_file("validation", validation, validation_paths[year])


def handle_data(tag: str, raw_lines: list, section_header_template, is_validation: bool):
    # Note: including empty Overrides/Comments
    data = []
    for raw_line in raw_lines[2:]:
        item: Item = {}
        item['Imported'] = {k:v for k,v in zip(section_header_template, raw_line[0:])}
        item['Account'] = {'Account': raw_line[6]}
        item['Override'] = {k:v for k,v in zip(section_header_template, raw_line[7:])}
        if is_validation:
            item['Final'] = {k:v for k,v in zip(section_header_template, raw_line[13:])}
        for i,key in enumerate(['My Category', 'E', 'Comment']):
            if key == 'E' and not is_validation:
                continue
            item[key] = {key: raw_line[19+i]}

        # Enforce consistent amount formatting
        for key in ['Imported', 'Override', 'Final']:
            if key not in item: continue
            amount = item[key]['Amount']
            assert isinstance(amount, str)
            if amount == '':
                assert key == 'Override'
                amount = None
            else:
                amount = Money.from_dollars(amount)
            item[key]['Amount'] = amount
        
        # Enforce consistent category capitalization
        category = item['My Category']['My Category']
        assert isinstance(category, str)
        for cat in categories:
            if category.lower() == cat.lower() and category != cat:
                # Same category, just wrong capitalization
                item['My Category']['My Category'] = cat
                break
        
        data.append(item)
    print(f"{tag.capitalize()} parsing complete")
    return data


def save_to_file(tag: str, contents, outfile):
    json_dump(outfile, contents, 2)
    print(f"{tag.capitalize()} export complete")


# Call it this instead of "main" to make imports easier
def xls_to_json():
    from Loading import years
    from Loading import is_json_stale
    for year in years:
        # Check both to avoid confusing printouts
        data_stale = is_json_stale(
            tag=f"{year} input",
            script_path=__file__,
            json_path=data_paths[year]
        )
        val_stale = is_json_stale(
            tag=f"{year} validation",
            script_path=__file__,
            json_path=validation_paths[year]
        )
        if data_stale or val_stale:
            process_year(year)


if __name__ == "__main__":
    xls_to_json()
