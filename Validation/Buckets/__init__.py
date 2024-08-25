# General imports
import os as _os


# Project imports
from BaseLib.utils import json_load
from Loading import buckets_data_path as data_path, buckets_validation_path as validation_path
from Validation.Buckets.Types import BucketsFull


def load_buckets_data() -> BucketsFull:
    from Validation.Aggregate import load_aggregate_data
    from .Handling import handle
    data = handle(
        aggregate_data=load_aggregate_data(),
        data=json_load(data_path),
    )
    return data

def load_buckets_validation() -> BucketsFull:
    from .Handling import handle_validation
    raw_validation: dict = json_load(validation_path)
    return handle_validation(raw_validation)