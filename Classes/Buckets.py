from Root.funcs import read_commented_csv
from Root import Constants as _import_Constants
from Root import Categories as _import_Categories

class Bucket:
    def __init__(self, name, max_value, monthly_refill):
        self.name = name
        self.max_value = max_value
        self.refill = monthly_refill / 30
#%% Define buckets

def _read_buckets() -> tuple[dict[_import_Constants.CatType, Bucket], tuple[_import_Constants.CatType]]:
    lines = read_commented_csv(_import_Constants.BucketInfo_file)

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
    assert _import_Categories.todo_category not in bucket_info
    bucket = Bucket(name=_import_Categories.todo_category, max_value=0.0, monthly_refill=0.0)
    bucket_info[_import_Categories.todo_category] = bucket

    return bucket_info, expense_categories
bucket_info, expense_categories = _read_buckets()


del_category = 'DELETE' # Flag to delete this transaction (keep in raw data for checksumming against sources)
categories_inclTodo = tuple(list(categories) + [_import_Categories.todo_category])
