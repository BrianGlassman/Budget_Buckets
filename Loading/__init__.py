# General imports
import os as _os

# Project imports


years = ['2023', '2024']

_basedir = _os.path.join(_os.path.dirname(__file__), "JSON")

log_data_paths = {year:_os.path.join(_basedir, f"log_{year}.json") for year in years}
log_validation_paths = {year:_os.path.join(_basedir, f"log_{year}_validation.json") for year in years}

aggregate_validation_paths = {year:_os.path.join(_basedir, f"aggregate_{year}_validation.json") for year in years}

buckets_data_path = _os.path.join(_basedir, "buckets.json")
buckets_validation_path = _os.path.join(_basedir, "buckets_validation.json")
