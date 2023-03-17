import csv as _import_csv

import BaseLib.Constants as _import_Constants
from BaseLib.funcs import read_flagged_csv as _import_read_flagged_csv

todo_category = '*** TODO ***'
del_category = 'DELETE' # Flag to delete this transaction (keep in raw data for checksumming against sources)

def _read_bucket_names():
    data = _import_read_flagged_csv(_import_Constants.BucketInfo_file)
    header = data.pop('HEADER')[0]
    fieldnames = header.split(',')

    expense_categories = None
    income_categories = None
    internal_categories = None
    def _helper(categories: list[str]) -> tuple[_import_Constants.CatType]:
        return tuple(categories)

    for flag, lines in data.items():
        lines = _import_csv.DictReader(lines, fieldnames=fieldnames)
        categories = [line['Category Name'] for line in lines]
        assert isinstance(categories, list)
        assert all(isinstance(c, _import_Constants.CatType) for c in categories)
        categories: list[str]
        if flag == 'EXPENSES':
            expense_categories = _helper(categories)
        elif flag == 'INCOME':
            income_categories = _helper(categories)
        elif flag == 'INTERNAL':
            internal_categories = _helper(categories)
    
    # Make PyLance happy
    assert expense_categories is not None
    assert income_categories is not None
    assert internal_categories is not None
    
    return expense_categories, income_categories, internal_categories
expense_categories, income_categories, internal_categories = _read_bucket_names()

# All possible categories, including the todo and delete flags
categories = tuple(
    list(expense_categories) + 
    list(income_categories) +
    list(internal_categories) +
    [todo_category, del_category]
)
