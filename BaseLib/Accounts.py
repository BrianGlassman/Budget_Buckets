import json as _import_json

from BaseLib.Constants import AccountSetup_file as _AccountSetup_file

with open(_AccountSetup_file) as _f:
    account_setup = _import_json.load(_f)
account_setup: dict[str, list[dict]]

accounts = list(account_setup.keys())

starting_balances = {act:0 for act in accounts}
starting_balances: dict[str, float] # {account: balance}
starting_balances.update({
    # Investment accounts aren't actually correct, but I don't want to account for market changes
    '401(k)': 33261.21,
    'M1': 1183.73,
    'Checking': 37237.66, # 2021/08/30 statement
    'FStocks': 17879.89,
    'Credit Card': -(220.92 # Balance as of 2021/09/17 (end of statement)
        - (1150.17 + 283.90 + 54.41) # Payments and Credits in September
        + (8.14+32.62+79.44+109.89+126.82+54.41+14.71+60.12+30+55.96+40+7.95+10.27+160.94+17.38+32.33)), # Charges in September
})
# TODO pretty sure Credit Card is wrong, but I need to think of a better way of dealing with the mid-month statement cycle
