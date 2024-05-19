# General imports
import os as _os


# Project imports
from .Handling import handle as handle_aggregate


_basedir = _os.path.dirname(__file__)
aggregate_validation_path = _os.path.join(_basedir, 'aggregate_2024_validation.json')