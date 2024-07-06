# General imports
import os as _os


# Project imports
from Validation import SingleValidationSpec as _Spec
from BaseLib.utils import json_load
from Validation.Buckets.Types import BucketsFull


spec = _Spec(
    basedir=_os.path.dirname(__file__),
    tag="buckets",
)

def load_buckets_data() -> BucketsFull:
    from Validation.Aggregate import load_aggregate_data
    from .Handling import handle
    data = handle(
        aggregate_data=load_aggregate_data(),
        data=json_load(spec.data_path),
    )
    return data

def load_buckets_validation() -> BucketsFull:
    from .Handling import handle_validation
    raw_validation: dict = json_load(spec.validation_path)
    return handle_validation(raw_validation)