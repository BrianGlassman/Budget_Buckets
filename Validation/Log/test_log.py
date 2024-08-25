"""
Validates the "Log" tabs in the Excel sheet
"""

# General imports


# Project imports
from Validation.Log import load_log_data as load_data, load_log_validation as load_validation


# Logging
from BaseLib.logger import delegate_print as print


def print_diff(data, validation):
    """Print differences in a useful way"""
    found = False
    for d, v in zip(data, validation):
        # Full-item match
        if d == v: continue

        # Make sure keys match
        if d.keys() != v.keys():
            found = True
            print(f"\n{d.keys()=}\n!=\n{v.keys()=}")
        else:
            # Find mismatched values
            for k in v.keys():
                if d[k] != v[k]:
                    print(f"\nd[{k}]={d[k]}\n!=\nv[{k}]={v[k]}")
                    found = True
                    break
        
        # Avoid console spam, just show the first problem
        if found: break

def test_log_duplication():
    from Loading.ExcelToJSON.log import xls_to_json as log_to_json
    log_to_json()

    data = load_data()
    validation = load_validation()

    if data != validation:
        print_diff(data, validation)
        raise Exception("Validation failed")
    
    print("Validation complete")

if __name__ == "__main__":
    test_log_duplication()
