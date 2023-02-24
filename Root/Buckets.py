# Path shenanigans for relative import when running directly
if __name__ == "__main__":
    import os, sys
    path = os.path.dirname(__file__)
    path = os.path.dirname(path)
    sys.path.append(path)

from Root import Constants as _import_Constants

class Bucket:
    def __init__(self, name, max_value, monthly_refill):
        self.name = name
        self.max_value = max_value
        self.refill = monthly_refill / 30
#%% Define buckets
todo_category = '*** TODO ***'

def _read_buckets() -> tuple[dict[_import_Constants.CatType, Bucket], tuple[_import_Constants.CatType]]:
    with open(_import_Constants.BucketInfo_file, 'r', newline='') as f:
        lines = [line.strip() for line in f.readlines()]
    lines = [line for line in lines if line] # Remove empty lines
    lines = [line for line in lines if not line.startswith('#')] # Remove comment lines

    bucket_info = {}
    for line in lines[1:]:
        category, max_s, monthly_s = line.split(',')
        assert category not in bucket_info
        max_f = float(max_s)
        monthly_f = float(monthly_s)
        bucket = Bucket(name=category, max_value=max_f, monthly_refill=monthly_f)
        bucket_info[category] = bucket
    
    # Get the category names
    expense_categories = tuple(bucket_info.keys())

    # Add the to-do category
    assert todo_category not in bucket_info
    bucket = Bucket(name=todo_category, max_value=0.0, monthly_refill=0.0)
    bucket_info[todo_category] = bucket

    return bucket_info, expense_categories
bucket_info, expense_categories = _read_buckets()

income_categories = (
    # Income
    'Parental Funds',
    'Loans',
    'Salary',
    'Income - Other',
)

internal_categories = (
    # Internal
    'CC Payments',
    'Internal Transfers',
)

categories = tuple(
    list(expense_categories) + 
    list(income_categories) +
    list(internal_categories)
)

del_category = 'DELETE' # Flag to delete this transaction (keep in raw data for checksumming against sources)
categories_inclTodo = tuple(list(categories) + [todo_category])
