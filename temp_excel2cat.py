# -*- coding: utf-8 -*-
"""
Created on Sun Jun 28 14:29:34 2020

@author: Brian Glassman
"""

"""Script for applying categories from my original Excel file to the new logs
Purely for testing and rapid development, shouldn't be used in final version
Note: creates the "categorized" log"""

import datetime

from temp_excel2log import logfile

#%% Read in the raw log
import json

def datetime_parser(dct):
    """Custom JSON decoder to convert str(datetime) back to datetime object
    Modified from:
    https://stackoverflow.com/questions/8793448/how-to-convert-to-a-python-datetime-object-with-json-loads
    """
    if 'Date' in dct:
        dct['Date'] = datetime.date.fromisoformat(dct['Date'])
    return dct

raw_log = json.load(open(logfile, 'r'), object_hook=datetime_parser)

#%% Split based on day, do other stuff

def get_desc(raw):
    c = raw['Custom Description']
    a = raw['Auto Description']
    if c and a:
        return f"c: a"
    elif c and (not a):
        return c
    elif (not c) and a:
        return a
    elif (not c) and (not a):
        return ""
    else:
        raise ValueError

today = None
log = {}
cell = None
recurring = [] # List of recurring transactions to apply to new days
    # Each item is a list of the form [mod_id, count] where count is the remaining
    # number of days to apply the recurrence
for mod_id, raw_trans in enumerate(raw_log):
    # TODO for now, mod_id = raw_id
    # Production version will include splitting transactions and shifting start times, which will change mod_id

    # Split off the temp data that's used in these temporary versions
    temp = raw_trans.pop('temp')

    # Rename fields for later convenience (also avoid pass-by-reference)
    trans = {'date': raw_trans['Date'], # transaction date
             'value': raw_trans['Raw Amount'], # transaction value, negative for expenses, positive for income
             'desc': get_desc(raw_trans), # transaction description
             'raw_id': raw_trans['Raw ID'], # ID of parent object from raw log, to preserve backwards traceability
             'mod_id': mod_id, # unique ID within the modded log, to store link information in files
                            # Also used to link recurring transactions
             'category': '?', # transaction category (gets filled in below)
             'recurrence': '?', # How to apply recurrence (gets filled in below)
                 # "None" means this is a one-time transaction, to be applied immediately
                 # Lower case is applied without shifting
                 # Upper case normalizes
                 # d/D = days
                 # m/M = months
                 # y/Y = years
             }

    # Make new cell(s), if necessary
    new_date = trans['date']
    while (today is None) or (today < new_date):
        if today is None:
            today = new_date
        else:
            today = today + datetime.timedelta(days=1) # Increment date for new cell
        cell = {"single": [], "new_recurring": [], "recurring": []}
        log[today] = cell
        for rec_list in recurring:
            # Apply each recurring transaction and decrement the counter
            cell['recurring'].append(rec_list[0])
            rec_list[1] -= 1
        # Remove recurring transactions that have been completed
        recurring = [x for x in recurring if x[1] > 0]

    # Apply category
    trans['category'] = temp['My Category']

    # Apply recurrence
    if temp['Split_raw'] == 1:
        # Single transaction
        trans['recurrence'] = None
        cell['single'].append(trans)
    else:
        # Recurring transaction
        # Have to do some fuzzy logic, this won't be in production
        rec = temp['Split_raw']
        # NOTE: initial count is reduced by one to account for first instance
        if rec == 14:
            # Salary
            rec = '14d' # Apply over 14 days, don't normalize
            recurring.append([mod_id, 13])
        elif 28 <= rec <= 31:
            # Monthly
            rec = '1m' # Apply over 1 month, don't normalize
            recurring.append([mod_id, 29])
        elif 365 <= rec <= 366:
            # Yearly
            rec = '1y' # Apply over 1 year, don't normalize
            recurring.append([mod_id, 364])

        trans['recurrence'] = rec
        cell['new_recurring'].append(trans)

#%% Create the JSON log
import json

# Convert all keys to strings
json_log = {str(k):v for k,v in log.items()}

jstr = json.dumps(json_log, default=str, indent=2)

print(jstr)

json.dump(json_log, open('mod_log.txt', 'w'), indent=2, default=str)

#%% NOTES ON LOG FORMAT
"""
Save as a dict ordered by date
    Easier to handle recurring events this way
"""
