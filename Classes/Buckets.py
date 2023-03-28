from BaseLib.funcs import read_flagged_csv
from BaseLib import Constants
from BaseLib import Categories

class Bucket:
    refill: float # Daily refill amount
    def __init__(self, name, max_value, monthly_refill):
        self.name = name
        self.max_value = max_value
        self.refill = monthly_refill / 30
        self.initial_value = max_value # TODO this should be set separately

#%% Define buckets

def _read_buckets() -> dict[Constants.CatType, Bucket]:
    data = read_flagged_csv(Constants.BucketInfo_file)
    # Only care about expenses
    lines = data['EXPENSES']

    bucket_info = {}
    for line in lines:
        category, max_s, monthly_s = line.split(',')
        assert category not in bucket_info
        # Convert string to float
        max_f = float(max_s)
        monthly_f = float(monthly_s)
        
        bucket = Bucket(name=category, max_value=max_f, monthly_refill=monthly_f)
        bucket_info[category] = bucket
    
    # Add the to-do category
    assert Categories.todo_category not in bucket_info
    bucket = Bucket(name=Categories.todo_category, max_value=0.0, monthly_refill=0.0)
    bucket_info[Categories.todo_category] = bucket

    return bucket_info
bucket_info = _read_buckets()
