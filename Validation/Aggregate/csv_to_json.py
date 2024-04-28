# General imports
import csv
from decimal import Decimal
import json
import os


# Project imports
from CategoryList import categories


# Typing
Item = dict[str, dict[str, str]]


def csv_to_json(filename):
    print(filename)
    with open(filename, 'r') as f:
        raw_lines = list(csv.reader(f))
    
    # First line is meta-header
    # FIXME don't hard-code date
    meta_header = ['Log Start', '', '1/1/2024']
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
    assert float(grand_total) == sum(float(v) for v in totals.values())
    print("Totals line as-expected")

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
        total = Decimal(raw_line[-1])
        assert total == sum(Decimal(v) for v in vals.values())
        item['data'] = vals
        data.append(item)
    print("Data parsing complete")

    # Output to file
    outfile = os.path.join(os.path.dirname(__file__), filename.replace('.csv', '.json'))
    with open(outfile, 'w') as f:
        json.dump(data, f, indent=2)
    print("Export complete")

if __name__ == "__main__":
    csv_to_json('aggregate_2024_validation.csv')
