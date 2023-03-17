import json as _import_json

from BaseLib.Constants import AccountSetup_file as _AccountSetup_file

with open(_AccountSetup_file) as _f:
    account_setup = _import_json.load(_f)
account_setup: dict[str, list[dict]]

accounts = list(account_setup.keys())