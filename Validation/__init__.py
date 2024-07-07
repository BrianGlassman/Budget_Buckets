import datetime as _datetime
import os as _os


# Logging
from BaseLib.logger import delegate_print as print

class ValidationSpec:
    basedir: str
    excel_path = 'Budget_Buckets.xlsm'
    export_script_path: str

class SingleValidationSpec(ValidationSpec):
    data_path: str
    validation_path: str
    def __init__(self, basedir, tag):
        self.basedir = basedir
        self.data_path = _os.path.join(basedir, f"{tag}.json")
        self.validation_path = _os.path.join(basedir, f"{tag}_validation.json")
        self.export_script_path = _os.path.join(basedir, "xls_to_json.py")

class YearlyValidationSpec(ValidationSpec):
    years = ['2023', '2024']
    data_paths: dict[str, str]
    validation_paths: dict[str, str]
    def __init__(self, basedir, tag):
        self.basedir = basedir
        self.data_paths = {year:_os.path.join(basedir, f"{tag}_{year}.json") for year in self.years}
        self.validation_paths = {year:_os.path.join(basedir, f"{tag}_{year}_validation.json") for year in self.years}
        self.export_script_path = _os.path.join(basedir, "xls_to_json.py")


def is_json_stale(excel_path: str, script_path: str, json_path: str):
    """Returns True if the JSON is older than the Excel file or conversion script, False if it's newer"""
    excel_mtime = _os.path.getmtime(excel_path)
    script_mtime = _os.path.getmtime(script_path)
    json_mtime = _os.path.getmtime(json_path)

    if (excel_diff := excel_mtime - json_mtime) > 0 or (script_diff := script_mtime - json_mtime) > 0:
        diff = _datetime.timedelta(seconds=max(excel_diff, script_diff))
        print(f"JSON out of date by {diff}. Converting.")
        return True
    else:
        print(f"Re-using existing JSON from {_datetime.datetime.fromtimestamp(json_mtime).strftime("%D %H:%M:%S")}.")
        return False
