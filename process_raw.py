# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 19:22:54 2020

@author: Brian Glassman

Process the raw transactions:
    split - Split compound transactions into separate individual transactions
        ex. House payment may include both rent and utilities
    categorize - Assign a category to each transaction
    normalize - Normalize recurring transactions to avoid spikes
"""

#%% Temporary implementations that use the categorizations from Excel

def __read_python():
    from database import raw_input
    transactions = []
    transactions.extend(raw_input.parse('2018_cc.csv',
                                        raw_input.USAA_parser,
                                        account='Credit Card'))
    transactions.extend(raw_input.parse('2018_chk.csv',
                                        raw_input.USAA_parser,
                                        account='Checking'))
    return transactions
raw_transactions = __read_python()

def __read_raw_excel():
    from database.raw_input import excel_parser
    log = excel_parser.parse(accounts = ['Checking', 'Credit Card'])
    log.sort(key = lambda x: x.date)
    return log
raw_excel = __read_raw_excel()

def __read_cat_excel():
    from database.raw_input import excel_cat_parser
    log = excel_cat_parser.parse(accounts = ['Checking', 'Credit Card'])
    log.sort(key = lambda x: x.date)
    return log
cat_excel = __read_cat_excel()

# Ensure that both use the same index
# This means that index found from searching raw_excel can be used to find the
# corresponding entry in cat_excel
assert all(c.desc == r.desc for c,r in zip(cat_excel, raw_excel))

def __temp_split():
    pass

#%% Operators

# FIXME Think this should be part of categorize?
def split(raw):
    """Splits one compound transaction into multiple
    i.e. Apartment payment covers both rent and utilities"""
    return raw

def categorize(raw):
    """Converts an uncategorized RawTransaction to a categorized Transaction
    Takes in a RawTransaction, returns a Transaction"""
    from database.raw_input import Transaction
    excel = cat_excel[raw_excel.index(raw)]
    return Transaction(date = raw.date,
                       value = raw.value,
                       desc = raw.desc,
                       category = excel.category,
                       recurrence = excel.recurrence)

def normalize(raw):
    """Normalizes the recurrence of a Transaction, adjusting the recurrence
    duration and date as needed"""
    return raw

#%% Operate
processed_transactions = []
for raw in raw_transactions:
    processed = normalize(categorize(split(raw)))
    processed_transactions.append(processed)