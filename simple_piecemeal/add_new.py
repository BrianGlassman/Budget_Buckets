# -*- coding: utf-8 -*-
"""
Created on Sat Aug 29 18:42:46 2020

@author: Brian Glassman

SIMPLE script to add new transactions to Excel file
DOES:
WILL:
    Read in csv files from USAA
    Apply category and recurrence to common transactions
    Write to Excel file
DOES NOT AND WILL NOT:
    Check if already existing
"""

#%% Imports

import re

import raw_input

#%% Read in raw transactions
raw_ = []
raw_.extend(raw_input.parse(r"D:\Users\Brian\Downloads\cc.csv",
                            raw_input.USAA_parser,
                            account='Credit Card'))
raw_.extend(raw_input.parse(r"D:\Users\Brian\Downloads\chk.csv",
                            raw_input.USAA_parser,
                            account='Checking'))

#%% Define common templates
#TODO replace with named tuple or custom class so keys aren't just strings
#TODO functionality to add/modify the description (i.e. Spotify)
#TODO splitting (i.e. Aritom into rent and utilities)
#TODO save off as a file (JSON needs lots of formatting and custom re parser)

# Regex notes:
#   \*{11} matches exactly 11 asterisks
common = [# Utilities / Rent
          {#//Phone
           'old': {'desc':'SPRINT *WIRELESS         800-639-6111 KS'},
           'new': {'category': 'Utilities', 'split': 30}},
          {#//PECO
           'old': {'desc': re.compile('^PECOENERGY       UTIL_BIL   \*{11}')},
           'new': {'category': 'Utilities', 'split': 30}},
          {#//PGW
           'old': {'desc': re.compile('^PGW WEBPAY       UTILITY    \*{11}')},
           'new': {'category': 'Utilities', 'split': 30}},
          {#//Aritom water bill
           'old': {'desc': 'ARITOM PROPERTIES        610-353-4925 PA',
                   'value': -40},
           'new': {'category': 'Utilities', 'split': 30}},
          {#//Aritom rent
           'old': {'desc': 'ARITOM PROPERTIES        610-353-4925 PA',
                   'value': -1650},
           'new': {'category': 'Rent', 'split': 30}},
          {#//Aritom rent and water bill
           'old': {'desc': 'ARITOM PROPERTIES        610-353-4925 PA',
                   'value': -1690},
           'new': {'category': 'Rent', 'split': 30}},

          # Banking
          {#//CC Payments
           'old': {'desc': re.compile('^USAA CREDIT CARD PAYMENT*')},
           'new': {'category': 'CC Payments', 'split': 1}},
          {#//Cash rewards credit
           'old': {'desc': 'CASH REWARDS CREDIT',
                   'value': (0, 20)},
           'new': {'category': 'Income - Other', 'split': 1}},
          {#//Interest
           'old': {'desc': 'INTEREST PAID',
                   'value': (0, 5)},
           'new': {'category': 'Income - Other', 'split': 1}},

          # Other
          {#//Grubhub
           'old': {'desc': re.compile('^PAYPAL \*GRUBHUBFOOD')},
           'new': {'category': 'Food - nice', 'split': 1}},
          {#//Salary
           'old': {'desc': re.compile('^AGUSTAWESTLAND P DIRECT DEP \*{11}'),
                   # TODO add entries for other pay rates, with dates
                   'value': (1902.79, 1902.81)},
           'new': {'category': 'Salary', 'split': 14}},
          {#//Spotify
           'old': {'desc': 'PAYPAL           INST XFER  ***********USAI',
                   'value': -10.81},
           'new': {'category': 'Entertainment - Other', 'split': 30}},
          {#//Car note
           'old': {'desc': re.compile('^HONDA PMT        8004489307 \*{11}'),
                   'value': -320},
           'new': {'category': 'Car - Note', 'split': 30}},
          {#//Insurance
           'old': {'desc': 'USAA P&amp;C INT     AUTOPAY    ***********1608'},
           'new': {'category': 'Car/Rental Insurance', 'split': 30}},
          ]

# Helper functions to check different fields
def _check_desc(transaction, template):
    """Assumes that template contains a desc field"""
    mask = template['desc']
    desc = transaction.desc
    if isinstance(mask, re.Pattern):
        # Regex matching (None if no match found)
        return mask.search(desc) is not None
    elif isinstance(mask, str):
        # Exact string matching
        return desc == mask
    else:
        raise NotImplementedError("Unknown mask type")
def _check_value(transaction, template):
    """Assumes that template contains a value field"""
    mask = template['value']
    val = transaction.value
    if isinstance(mask, (int, float)):
        # Exact value matching
        return val == mask
    else:
        # Range matching
        assert len(mask) == 2
        assert mask[0] < mask[1]
        return mask[0] <= val <= mask[1]
_checker = {'desc': _check_desc,
            'value': _check_value,
            }

# Main function to check RawTransaction against a template
def template_check(raw):
    #TODO more automaticish, given old/new are separate dicts
    assert isinstance(raw, raw_input.RawTransaction)
    matched = None
    # Check the transaction against all templates in order
    for template in common:
        old = template['old']
        new = template['new']
        match = True
        for key in old:
            # Run the checker for each field that has a pattern
            match = match and _checker[key](raw, old)
            if not matched: break # Exit loop if any pattern fails

        if match:
            # Template matched, stop searching
            matched = new
            break
    if matched is None:
        # No template matched
        return None
    else:
        # Template matched, apply it
        # TODO use alternate constructor once implemented
        #   Or some other smart way of converting RawTransaction to Transaction
        d = raw.to_dict()
        d.update(new)
        # Keep only keys that are used for Transaction
        d = {k:v for k,v in d.items() if k in raw_input.Transaction.fields()}
        return raw_input.Transaction(**d)

#%% Check transactions against templates
found = []
not_found = []
for raw in raw_:
    trans = template_check(raw)
    if trans is None:
        # No template matched
        not_found.append(raw)
    else:
        # Template matched, Transaction created
        found.append(trans)

print('\n'.join(str(x) for x in not_found))
