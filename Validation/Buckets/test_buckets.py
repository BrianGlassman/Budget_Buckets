"""
Validates the "Buckets" tabs in the Excel sheet
"""

# General imports


# Project imports
from Validation.Buckets import load_buckets_data, load_buckets_validation, Types


# Logging
from BaseLib.logger import delegate_print as print

def load():
    data = load_buckets_data()
    validation = load_buckets_validation()

    return data, validation

def print_VCC_diff(indent, data: Types.ValueCapacityCritical, validation: Types.ValueCapacityCritical):
    if data.value != validation.value:
        print(f"{indent}value MISMATCH")
    if data.capacity != validation.capacity:
        print(f"{indent}capacity MISMATCH")
    if data.is_critical != validation.is_critical:
        print(f"{indent}is_critical MISMATCH")

def print_diff(data: Types.BucketsFull, validation: Types.BucketsFull):
    if data.initial != validation.initial:
        print("initial MISMATCHED")
    
    assert data.months.keys() == data.transitions.keys()
    assert validation.months.keys() == validation.transitions.keys()

    for k in data.months.keys():
        if (d := data.months[k]) != (v := validation.months[k]):
            print(f"Month {k} MISMATCH")
            break
        if (d := data.transitions[k]) != (v := validation.transitions[k]):
            print(f"Transition after {k} MISMATCH")
            if d.end_previous != v.end_previous:
                print("\tend_previous MISMATCH")
                print_VCC_diff('\t'*2, d.end_previous, v.end_previous)
            if d.changes != v.changes:
                print("\tchanges MISMATCH")
            if d.start_next != v.start_next:
                print("\tstart_next MISMATCH")
                print_VCC_diff('\t'*2, d.start_next, v.start_next)
            if d.error_checks != v.error_checks:
                print("\terror_checks MISMATCH")
            break

def test_buckets_duplication():
    from Loading.ExcelToJSON.log import xls_to_json
    xls_to_json()
    
    data, validation = load()

    if data != validation:
        print_diff(data, validation)
        raise Exception("Validation failed")
    
    print("Validation complete")

if __name__ == "__main__":
    test_buckets_duplication()
