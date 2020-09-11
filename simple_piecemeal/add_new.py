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

# FIXME TEMP MOD TO TEST
raw_.pop(21)
raw_[20].value = -1690

#%% Check transactions against templates
found = []
not_found = []
for raw in raw_:
    template = raw.match_templates()
    if template is None:
        # No template matched
        not_found.append(raw)
    else:
        # Template matched, Transaction created
        found.extend(raw.apply_template(template))

print('\n'.join(str(x) for x in not_found))
