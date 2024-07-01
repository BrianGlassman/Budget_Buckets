"""
Validates the "Buckets" tabs in the Excel sheet
"""

# General imports


# Project imports
from Validation.Buckets import load_buckets_data, load_buckets_validation


def load():
    data = load_buckets_data()
    validation = load_buckets_validation()

    # FIXME temporarily just looking at the first month
    from Validation.Buckets import BucketsFull
    key = '9/1/2023'
    validation = BucketsFull(
        initial=validation.initial,
        months={key: validation.months[key]},
        transitions={key: validation.transitions[key]},
    )

    return data, validation

def print_diff(data, validation):
    for key in ['initial', 'months', 'transitions']:
        if getattr(data, key) == getattr(validation, key):
            print(f"{key} matched")
        else:
            print(f"{key} MISMATCHED")
            if key == 'months':
                d = list(data.months.values())[0]
                v = list(validation.months.values())[0]
                for key in ['columns', 'intermediate', 'error_checks']:
                    if getattr(d, key) == getattr(v, key):
                        print(f"\t{key} matched")
                    else:
                        print(f"\t{key} MISMATCHED")
                        if key == 'columns':
                            if d.columns.keys() != v.columns.keys():
                                print("\t\tMISMATCHED column keys")
                            if d.columns.values() != v.columns.values():
                                print("\t\tMISMATCHED column values")

                                dd = list(d.columns.values())
                                vv = list(v.columns.values())
                                pass
                        else:
                            print("\t\tD:", getattr(d, key))
                            print("\t\tV:", getattr(v, key))


    # print("      Data:", data.asdict())
    # print("Validation:", validation.asdict())
    pass # FIXME this is just so I have somewhere for breakpoints

def test_buckets_duplication():
    data, validation = load()

    if data != validation:
        print_diff(data, validation)
        raise Exception("Validation failed")
    
    print("Validation complete")

if __name__ == "__main__":
    test_buckets_duplication()
