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
def _read_buckets() -> dict[_import_Constants.CatType, Bucket]:
    with open(_import_Constants.BucketInfo_file, 'r', newline='') as f:
        lines = [line.strip() for line in f.readlines()]
    lines = [line for line in lines if line] # Remove empty lines
    lines = [line for line in lines if not line.startswith('#')] # Remove comment lines

    # Add the to-do category
    lines.append(f'{_import_Constants.todo_category},0,0')

    bucket_info = {}
    for line in lines[1:]:
        category, max_s, monthly_s = line.split(',')
        max_f = float(max_s)
        monthly_f = float(monthly_s)
        bucket = Bucket(name=category, max_value=max_f, monthly_refill=monthly_f)
        assert category not in bucket_info
        bucket_info[category] = bucket
    return bucket_info
bucket_info = _read_buckets()
