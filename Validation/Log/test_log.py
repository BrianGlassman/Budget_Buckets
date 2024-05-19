"""
Validates the "Log" tabs in the Excel sheet
"""

# General imports
import json


# Project imports
from Validation.Log import load_log_data, laod_log_validation


def load():
    data = load_log_data()
    validation = laod_log_validation()
    return data, validation

def test_log_duplication():
    data, validation = load()

    if data != validation:
        print_diff(data, validation)
        raise Exception("Validation failed")
    
    print("Validation complete")

def print_diff(data, validation):
    """Print differences in a useful way"""
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
