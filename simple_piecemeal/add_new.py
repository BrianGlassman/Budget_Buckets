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

# Regex notes:
#   \*{11} matches exactly 11 asterisks
common = [# Utilities / Rent
          {#//Phone
           'desc':'SPRINT *WIRELESS         800-639-6111 KS',
           'category': 'Utilities', 'split': 30},
          {#//PECO
           'desc': re.compile('^PECOENERGY       UTIL_BIL   \*{11}'),
           'category': 'Utilities', 'split': 30},
          {#//PGW
           'desc': re.compile('^PGW WEBPAY       UTILITY    \*{11}'),
           'category': 'Utilities', 'split': 30},
          {#//Aritom water bill
           'desc': 'ARITOM PROPERTIES        610-353-4925 PA',
           'value': -40,
           'category': 'Utilities', 'split': 30},
          {#//Aritom rent
           'desc': 'ARITOM PROPERTIES        610-353-4925 PA',
           'value': -1650,
           'category': 'Rent', 'split': 30},
          {#//Aritom rent and water bill
           'desc': 'ARITOM PROPERTIES        610-353-4925 PA',
           'value': -1690,
           'category': 'Rent', 'split': 30},

          # Banking
          {#//CC Payments
           'desc': re.compile('^USAA CREDIT CARD PAYMENT*'),
           'category': 'CC Payments', 'split': 1},
          {#//Cash rewards credit
           'desc': 'CASH REWARDS CREDIT',
           'value': (0, 20),
           'category': 'Income - Other', 'split': 1},
          {#//Interest
           'desc': 'INTEREST PAID',
           'value': (0, 5),
           'category': 'Income - Other', 'split': 1},

          # Other
          {#//Grubhub
           'desc': re.compile('^PAYPAL \*GRUBHUBFOOD'),
           'category': 'Food - nice', 'split': 1},
          {#//Salary
           'desc': re.compile('^AGUSTAWESTLAND P DIRECT DEP \*{11}'),
           # TODO will need a smarter system to handle entries with different pay rates
           'value': (1902.79, 1902.81),
           'category': 'Salary', 'split': 14},
          {#//Spotify
           'desc': 'PAYPAL           INST XFER  ***********USAI',
           'value': -10.81,
           'category': 'Entertainment - Other', 'split': 30},
          {#//Car note
           'desc': re.compile('^HONDA PMT        8004489307 \*{11}'),
           'value': -320,
           'category': 'Car - Note', 'split': 30},
          {#//Insurance
           'desc': 'USAA P&amp;C INT     AUTOPAY    ***********1608',
           'category': 'Car/Rental Insurance', 'split': 30},
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

# Main function to check RawTransaction against a template
def template_check(raw):
    assert isinstance(raw, raw_input.RawTransaction)
    matched = None
    for template in common:
        match = True
        if 'desc' in template:
            match = match and _check_desc(raw, template)
        if 'value' in template:
            match = match and _check_value(raw, template)

        if match:
            # Template matched, stop searching
            matched = template
            break
    if matched is None:
        # No template matched
        return None
    else:
        # Template matched, apply it
        # TODO use alternate constructor once implemented
        return raw_input.Transaction(date = raw.date,
                                     value = raw.value,
                                     desc = raw.desc,
                                     category = template['category'],
                                     recurrence = template['split'])

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
