# General imports
import os as _os


# Project imports
from BaseLib.utils import json_load
from Validation.Buckets.Types import BucketsFull


_basedir = _os.path.dirname(__file__)
buckets_data_path = _os.path.join(_basedir, 'buckets.json')
buckets_validation_path = _os.path.join(_basedir, 'buckets_validation.json')

def load_buckets_data() -> BucketsFull:
    from Validation.Aggregate import load_aggregate_data
    from .Handling import handle
    data = handle(
        aggregate_data=load_aggregate_data(),
        data=json_load(buckets_data_path),
    )
    return data

def load_buckets_validation() -> BucketsFull:
    from .Handling import handle_validation
    raw_validation: dict = json_load(buckets_validation_path)
    return handle_validation(raw_validation)