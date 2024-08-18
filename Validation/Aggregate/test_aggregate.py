"""
Validates the "Aggregate" tabs in the Excel sheet
"""

# General imports


# Project imports
from Validation.Aggregate import load_aggregate_data as load_data, load_aggregate_validation as load_validation


# Logging
from BaseLib.logger import delegate_print as print


def print_diff(data: list[dict], validation: list[dict]):
    if len(data) != len(validation):
        print("Length mismatch")
        return
    
    def printer(indent: int, k, d, v):
        print(f"{'>>' * indent} {k} mismatched")
        print(f"{'>>' * indent}       Data: {repr(d[k])}")
        print(f"{'>>' * indent} Validation: {repr(v[k])}")
    
    for i, (d, v) in enumerate(zip(data, validation)):
        if d != v:
            print(f"Element {i} mismatched")
            print(f"      Data: {d}")
            print(f"Validation: {v}")

            k = 'start'
            if d[k] != v[k]: printer(1, k, d, v)
            k = 'end'
            if d[k] != v[k]: printer(1, k, d, v)
            dd = d['data'] ; vv = v['data']
            for k in dd.keys():
                if dd[k] != vv[k]:
                    printer(2, k, dd, vv)
            
            break


def test_aggregate_duplication():
    from Loading.ExcelToJSON.aggregate import xls_to_json
    xls_to_json()

    data = load_data()
    validation = load_validation()

    if data != validation:
        print_diff(data, validation)
        raise Exception("Validation Failed")
    
    print("Validation complete")

if __name__ == "__main__":
    test_aggregate_duplication()
