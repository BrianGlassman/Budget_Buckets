"""
Validates the "Log" tabs in the Excel sheet
"""

# General imports


# Project imports
from Validation.Log import load_log_data, load_log_validation


# Logging
from BaseLib.logger import delegate_print as print

def load():
    data = load_log_data()
    validation = load_log_validation()
    return data, validation

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
                    print(f"d[{k}]={d[k]}\n!=\nv[{k}]={v[k]}")
                    found = True
                    break
        
        # Avoid console spam, just show the first problem
        if found: break

def test_log_duplication():
    from Validation import is_json_stale
    from . import spec
    from .xls_to_json import xls_to_json
    for year in spec.years:
        if (is_json_stale(spec.excel_path, spec.export_script_path, spec.data_paths[year])
            or
            is_json_stale(spec.excel_path, spec.export_script_path, spec.validation_paths[year])
            ):
            xls_to_json(year)

    data, validation = load()

    if data != validation:
        print_diff(data, validation)
        raise Exception("Validation failed")
    
    print("Validation complete")

if __name__ == "__main__":
    test_log_duplication()
