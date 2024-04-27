# General imports
import csv
from decimal import Decimal
import json


# Project imports
from CategoryList import categories


# Typing
Item = dict[str, dict[str, str]]


def log_csv_to_json(filename, validation):
    print(filename)
    with open(filename, 'r') as f:
        raw_lines = list(csv.reader(f))

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
                amount = str(float(amount))
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

    # Output to file
    with open('Validation/Data/' + filename.replace('.csv', '.json'), 'w') as f:
        json.dump(data, f, indent=2)
    print("Export complete")

if __name__ == "__main__":
    for filename in ["log_2024.csv", "log_2024_validation.csv"]:
        validation = "validation" in filename
        log_csv_to_json(filename, validation)
