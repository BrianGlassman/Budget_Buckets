import datetime as _import_datetime
import os as _import_os

one_day = _import_datetime.timedelta(days=1)

CatType = str

# Collect file paths in one place so that other things can reference them
# (namely, the Build script)
AutoTemplates_file = _import_os.path.join('Handlers', 'Categorize', 'AutoTemplates.json')
Templates_file = _import_os.path.join('Handlers', 'Categorize', 'Templates.json')
ManualAccountHandling_file = _import_os.path.join('Handlers', 'Categorize', 'ManualAccountHandling.json')
BucketInfo_file = _import_os.path.join('BaseLib', 'BucketInfo.csv')
AccountSetup_file = _import_os.path.join('BaseLib', 'AccountSetup.json')
todo_file = 'TODO.txt'
readme_file = 'README.md'
filepaths = [
    AutoTemplates_file,
    Templates_file,
    ManualAccountHandling_file,
    BucketInfo_file,
    AccountSetup_file,
    todo_file,
    readme_file,
]
for _filepath in filepaths:
    assert _import_os.path.isfile(_filepath), _filepath
