import csv as _import_csv

import Root.Constants as _import_Constants
from Root.funcs import read_commented_csv as _import_read_commented_csv

todo_category = '*** TODO ***'

def _read_bucket_categories():
    lines = _import_read_commented_csv(_import_Constants.BucketInfo_file)
    lines = _import_csv.DictReader(lines)
    categories = [line['Category Name'] for line in lines]
    return categories
# Buckets are for expenses, so just use those names
expense_categories = tuple(_read_bucket_categories())

# Add the to-do category
assert todo_category not in expense_categories

income_categories = (
    'Parental Funds',
    'Loans',
    'Salary',
    'Income - Other',
)

internal_categories = (
    'CC Payments',
    'Internal Transfers',
)

categories = tuple(
    list(expense_categories) + 
    list(income_categories) +
    list(internal_categories)
)