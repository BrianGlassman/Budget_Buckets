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

from database import raw_input

#%% Read in raw transactions
raw_ = []
raw_.extend(raw_input.parse(r"D:\Users\Brian\Downloads\cc.csv",
                            raw_input.USAA_parser,
                            account='Credit Card'))
raw_.extend(raw_input.parse(r"D:\Users\Brian\Downloads\chk.csv",
                            raw_input.USAA_parser,
                            account='Checking'))

#%% Check transactions against templates
found = {} # dict of {raw_ index: [Transactions(s)]}
not_found = {} # dict of {raw_ index: [Transactions(s)]}
for idx, raw in enumerate(raw_):
    template = raw.match_templates()
    if template is None:
        # No template matched
        not_found[idx] = [raw]
    else:
        # Template matched, Transaction created
        found[idx] = raw.apply_template(template)

#%% Output in a way that's easy to copy to Excel

columns = ['Status', 'idk', 'Date', 'Custome Description', 'Auto Description',
            'USAA Category', 'Raw Amount', 'Amount', 'Abs Amt',
            'Split_raw', 'Split_apply', 'My Category', 'Account']

out = []
# Do not found first so that when I paste into Excel the new and old
# transactions are separated
for t_list in not_found.values():
    t = t_list[0]
    desc = t.desc
    if '---' in desc:
        c_desc, a_desc = desc.split(' --- ')
    else:
        c_desc = ''
        a_desc = desc
    line = ['posted', '', t.date, c_desc, a_desc,
            t.auto_cat, t.value, '', '',
            '', '', '', t.account]
    out.append(line)
for idx, t_list in found.items():
    r = raw_[idx]
    for t in t_list:
        desc = t.desc
        if '---' in desc:
            c_desc, a_desc = desc.split(' --- ')
        else:
            c_desc = ''
            a_desc = desc
        line = ['posted', '', t.date, c_desc, a_desc,
                r.auto_cat, t.value, '', '',
                t.recurrence, '', t.category, r.account]
        out.append(line)

print('\n'.join(','.join(str(x) for x in line) for line in out))
