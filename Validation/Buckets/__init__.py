# General imports
import os as _os
import json as _json


# Project imports
from Validation.Buckets.Types import BucketsFull


_basedir = _os.path.dirname(__file__)
buckets_data_path = _os.path.join(_basedir, 'buckets.json')
buckets_validation_path = _os.path.join(_basedir, 'buckets_validation.json')

def load_buckets_data() -> BucketsFull:
    from Validation.Aggregate import load_aggregate_data
    from .Handling import handle
    with open(buckets_data_path, 'r') as f:
        data = handle(
            aggregate_data=load_aggregate_data(),
            data=_json.load(f),
        )
    return data

def load_buckets_validation() -> BucketsFull:
    from .Handling import handle_validation
    with open(buckets_validation_path, 'r') as f:
        raw_validation: dict = _json.load(f)
    return handle_validation(raw_validation)