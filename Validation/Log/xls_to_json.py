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


def xls_to_json(filename, sheet_name: str):
    wb = openpyxl.load_workbook(filename=filename, read_only=True, data_only=True)
    sheet = wb[sheet_name]
    assert isinstance(sheet, openpyxl.worksheet._read_only.ReadOnlyWorksheet)
    # Do some manipulating so it looks like the CSV version
    raw_lines = [[format_value(value) for value in row] for row in sheet.values]

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
    data = handle_data(raw_lines, section_header_template, False)
    validation = handle_data(raw_lines, section_header_template, True)

    # Save to file
    base_filename = sheet_name.replace(' ', '_').lower()
    save_to_file(data, base_filename + ".json")
    save_to_file(validation, base_filename + "_validation.json")


def handle_data(raw_lines: list, section_header_template, validation: bool):
    # Note: including empty Overrides/Comments
    data = []
    for raw_line in raw_lines[2:]:
        item: Item = {}
        item['Imported'] = {k:v for k,v in zip(section_header_template, raw_line[0:])}
        item['Account'] = {'Account': raw_line[6]}
        item['Override'] = {k:v for k,v in zip(section_header_template, raw_line[7:])}
        if validation:
            item['Final'] = {k:v for k,v in zip(section_header_template, raw_line[13:])}
        for i,key in enumerate(['My Category', 'E', 'Comment']):
            if key == 'E' and not validation:
                continue
            item[key] = {key: raw_line[19+i]}

        # Enforce consistent amount formatting
        for key in ['Imported', 'Override', 'Final']:
            if key not in item: continue
            amount = item[key]['Amount']
            amount = amount.replace('$', '').replace(',', '')
            if amount == '':
                assert key == 'Override'
            else:
                amount = str(Decimal(amount).quantize(Decimal('0.01')))
            item[key]['Amount'] = amount
        
        # Enforce consistent category capitalization
        category = item['My Category']['My Category']
        for cat in categories:
            if category.lower() == cat.lower() and category != cat:
                # Same category, just wrong capitalization
                item['My Category']['My Category'] = cat
                break
        
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
    for year in ['2023', '2024']:
        print(year)
        xls_to_json("Budget_Buckets.xlsm", f"Log {year}")
