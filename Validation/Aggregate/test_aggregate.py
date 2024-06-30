"""
Validates the "Aggregate" tabs in the Excel sheet
"""

# General imports


# Project imports
from Validation.Aggregate import load_aggregate_data, load_aggregate_validation


def load():
    data = load_aggregate_data()
    validation = load_aggregate_validation()
    return data, validation

def print_diff(data, validation):
    # TODO make this actually useful
    print("data != validation")

def test_aggregate_duplication():
    data, validation = load()

    if data == validation:
        print_diff(data, validation)
    print("Validation complete")

if __name__ == "__main__":
    test_aggregate_duplication()
