# General imports
import csv
import dash
import datetime
from functools import partial
from typing import Any


# Project imports
from CategoryList import categories
categories = [c.lower() for c in categories] # I got some capitalization wrong when making the log


# Styling
style={'border': '1px solid grey'}


# General aliases
Row = partial(dash.html.Tr, style=style)
Header = partial(dash.html.Th, style=style)
Data = partial(dash.html.Td, style=style)


def format_money(val: str) -> str:
    """Copy Excel's money formatting"""
    return "${:,.2f}".format(float(val)).replace('$-', '-$')

def create_table(data: list[dict]):
    # Headers
    super_header = Row([Header(col) for col in data[0].values()])
    sub_header = Row([Header(col) for col in data[1].values()])

    # Body
    body = [
        Row([Data(cell) for cell in row.values()])
        for row in data[2:]
    ]

    table = dash.html.Table([
        super_header,
        sub_header,
        *body],
        style={'border-spacing': '0', 'border-collapse': 'collapse'}
    )
    return table


def load_data():
    """Load the data, apply override logic, and parse strings"""
    with open('log_2024.csv') as f:
        lines = list(csv.reader(f))

    # Get keys/idx for "real" data (only what would exist in production)
    extra_keys = ["Account", "My Category", "Comment"]
    keys = [val for val in lines[1]]
    idxs = [i for i, key in enumerate(keys) if key.endswith(('_i', '_o')) or key in extra_keys]

    # Copy the headers
    # Line 0 is imported/override/final
    # Line 1 is the actual headers
    # Lines 2+ are data
    data = [{keys[i]:line[i] for i in range(len(keys))} for line in lines[0:2]]

    # Copy only the real data
    for line in lines[2:]:
        data.append({
            keys[i]:(line[i].strip() if i in idxs else '') for i in range(len(line))
        })
    
    # Handle override logic
    override_keys = [key for key in keys if key.endswith('_o')]
    for line in data[2:]:
        for key in override_keys:
            override = line[key]
            imported = line[key.replace('_o', '_i')]
            line[key.replace('_o', '')] = override if override else imported
            
    # Handle error logic
    for line in data[2:]:
        if line['My Category'].lower() in categories:
            line['E'] = '.'
        else:
            line['E'] = 'E'
    
    def parse_line(line: dict[str, Any]):
        new_line = {}
        for k, v in line.items():
            # Empty string to None
            if v == '':
                v = None
            # Dates to datetime.date
            elif k.startswith('Date'):
                v = datetime.datetime.strptime(v, '%m/%d/%Y').date()
            # Amounts to floats
            elif k.startswith('Amount'):
                v = float(v)

            new_line[k] = v
        return new_line
    data = data[0:2] + [parse_line(line) for line in data[2:]]
    
    return data

def format_data(data: list[dict]):
    """Applies formatting to match the validation data"""
    data = data.copy()

    def unparse_line(line: dict[str, Any]):
        new_line = {}
        for k, v in line.items():
            # None to empty string
            if v is None:
                v = ''
            # datetime.date to dates
            elif k.startswith('Date'):
                v = v.strftime('%#m/%#d/%Y') # Note: may have to be "#" on Windows and "-" on Unix
            # floats to amounts (Amount_i and Amount_o are formatted differently than Amount)
            elif k == 'Amount':
                v = format_money(v)
            elif k in ('Amount_i', 'Amount_o'):
                v = str(v) if v % 1 != 0 else f"{v:.0f}"
                
            new_line[k] = v
        return new_line
    data = data[0:2] + [unparse_line(line) for line in data[2:]]

    return data

def load_validation():
    with open('log_2024_validation.csv') as f:
        lines = list(csv.reader(f))
    
    # Copy the headers and contents
    # Line 0 is imported/override/final
    # Line 1 is the actual headers
    # Lines 2+ are data
    keys = [val for val in lines[1]]
    data = [{keys[i]:line[i].strip() for i in range(len(keys))} for line in lines]

    # Check for the "." in the error-check column
    for line in data[2:]:
        assert line['E'] == '.', line['E']

    return data

def check(data: list[dict], validation: list[dict]):
    for d_line, v_line in zip(data[2:], validation[2:]):
        assert d_line == v_line, [f'{k}: {d}!={v}' for (k, d), v in zip(d_line.items(), v_line.values()) if d != v]

if __name__ == "__main__":
    data = load_data()
    validation = load_validation()
    check(format_data(data), validation)


    # Create the app
    app = dash.Dash(__name__)
    table = create_table(format_data(data))
    app.layout = dash.html.Div(table)
    app.run(debug=True)
