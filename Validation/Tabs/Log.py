"""
Duplicates the "Log" tabs in the Excel sheet
"""

# General imports
import json


# Project imports
from CategoryList import categories


# Typing
Item = dict[str, dict[str, str]]


with open('Validation/Data/log_2024.json', 'r') as f:
    data: list[Item] = json.load(f)
with open('Validation/Data/log_2024_validation.json', 'r') as f:
    validation: list[Item] = json.load(f)

for item in data:
    # Handle override logic
    final = item['Final'] = {}
    for key, override in item['Override'].items():
        final[key] = override if override else item['Imported'][key]

    # Handle error logic
    item['E'] = {
        'E': '.' if (item['My Category']['My Category'] in categories) else 'E'
    }

    if item['E']['E'] == 'E':
        raise ValueError()

if data != validation:
    found = False
    for d, v in zip(data, validation):
        # Full-item match
        if d == v: continue

        # Make sure keys match
        if d.keys() != v.keys():
            found = True
            print(f"{d.keys()=}\n!=\n{v.keys()=}")
        else:
            # Find mismatched values
            for k in v.keys():
                if d[k] != v[k]:
                    found = True
                    print(f"{d[k]=} != {v[k]=}")
        
        # Avoid console spam, just show the first problem
        if found: break
    raise Exception("Validation failed")
print("Validation complete")
