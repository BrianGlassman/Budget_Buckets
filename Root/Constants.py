import datetime as _import_datetime
import os as _import_os
import json as _import_json

one_day = _import_datetime.timedelta(days=1)

CatType = str

# Collect file paths in one place so that other things can reference them
# (namely, the Build script)
AutoTemplates_file = _import_os.path.join('Categorize', 'AutoTemplates.json')
Templates_file = _import_os.path.join('Categorize', 'Templates.json')
ManualAccountHandling_file = _import_os.path.join('Categorize', 'ManualAccountHandling.json')
Constants_file = _import_os.path.join('Root', 'Constants.py')
BucketInfo_file = _import_os.path.join('Root', 'BucketInfo.csv')
AccountSetup_file = _import_os.path.join('Root', 'AccountSetup.json')
todo_file = 'TODO.txt'
readme_file = 'README.md'
filepaths = [
    AutoTemplates_file,
    Templates_file,
    ManualAccountHandling_file,
    Constants_file,
    BucketInfo_file,
    AccountSetup_file,
    todo_file,
    readme_file,
]

with open(AccountSetup_file) as _f:
    account_setup = _import_json.load(_f)
account_setup: dict[str, list[dict]]

accounts = list(account_setup.keys())