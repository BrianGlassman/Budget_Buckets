import datetime as _import_datetime
import os as _import_os

# Path shenanigans for relative import when running directly
if __name__ == "__main__":
    import os, sys
    path = os.path.dirname(__file__)
    path = os.path.dirname(path)
    sys.path.append(path)

from Root import funcs as _import_funcs

one_day = _import_datetime.timedelta(days=1)

CatType = str

# Collect file paths in one place so that other things can reference them
# (namely, the Build script)
AutoTemplates_file = _import_os.path.join('Categorize', 'AutoTemplates.json')
Templates_file = _import_os.path.join('Categorize', 'Templates.json')
ManualAccountHandling_file = _import_os.path.join('Categorize', 'ManualAccountHandling.json')
ParseSettings_file = _import_os.path.join('Parsing', 'ParseSettings.csv')
Constants_file = _import_os.path.join('Root', 'Constants.py')
BucketInfo_file = _import_os.path.join('Root', 'BucketInfo.csv')
Accounts_file = _import_os.path.join('Root', 'Accounts.csv')
todo_file = 'TODO.txt'
readme_file = 'README.md'
filepaths = [
    AutoTemplates_file,
    Templates_file,
    ManualAccountHandling_file,
    ParseSettings_file,
    Constants_file,
    BucketInfo_file,
    Accounts_file,
    todo_file,
    readme_file,
]

accounts = _import_funcs.read_commented_csv(Accounts_file)