import os as _os


class ValidationSpec:
    basedir: str
    excel_path = 'Budget_Buckets.xlsm'

class SingleValidationSpec(ValidationSpec):
    data_path: str
    validation_path: str
    def __init__(self, basedir, tag):
        self.basedir = basedir
        self.data_path = _os.path.join(basedir, f"{tag}.json")
        self.validation_path = _os.path.join(basedir, f"{tag}_validation.json")

class YearlyValidationSpec(ValidationSpec):
    years = ['2023', '2024']
    data_paths: dict[str, str]
    validation_paths: dict[str, str]
    def __init__(self, basedir, tag):
        self.basedir = basedir
        self.data_paths = {year:_os.path.join(basedir, f"{tag}_{year}.json") for year in self.years}
        self.validation_paths = {year:_os.path.join(basedir, f"{tag}_{year}_validation.json") for year in self.years}
