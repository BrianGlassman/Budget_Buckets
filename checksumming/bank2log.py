# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 19:43:16 2020

@author: Brian Glassman
"""

infile = 'Jan 2018 Secured Credit.csv'
outfile = '2018_secured_credit.txt'

if __name__ == '__main__':

    """Script for converting from USAA output csv to the new log format
    NOTE: creates the "raw" log
    """

    # TODO move to library
    def str2datetime(date):
        import datetime
        return datetime.datetime.strptime(date, '%m/%d/%Y').date()

    import csv
    import json

    def format_raw(line):
        line['Date'] = str2datetime(line['Date'])
        # USAA saves positive values as "=--val", correct it
        line['Raw Amount'] = float(line['Raw Amount'].replace('--',''))
        return line

    # Keys that will be in the production-version log file
    transaction_keys = ('Status', 'Idk', 'Date', 'Custom Description',
                        'Auto Description', 'Auto Category', 'Raw Amount')
    n = len(transaction_keys)
    # Keys only used for these temporary versions
    temp_keys = ('_', '_', 'Split_raw', '_', 'My Category')

    #%% Read in transactions from file
    log = []
    with open(infile, 'r') as f:
        log = [format_raw(line) for line in csv.DictReader(f, fieldnames=transaction_keys)]

    #%% Create the JSON log

    # Sort chronologically (earliest at the top, latest at the bottom)
    log = sorted(log, key=lambda x: x['Date'])

    # Remove unneeded columns
    for num, transaction in enumerate(log):
        del transaction['Status'] # TODO will be needed once predictive stuff is in use
        del transaction['Idk'] # Venmo fills this column, but that will be taken care of separately
        transaction['Raw ID'] = num # Unique ID number for each transaction

    jstr = json.dumps(log, default=str, indent=2)

    print(jstr)

    json.dump(log, open(outfile, 'w'), indent=2, default=str)

    #%% NOTES ON LOG FORMAT
    """
    Save as a chronological list, rather than dictionary keyed by date
        Once read into memory, can pivot to dict keyed by date, category, ID,
        account, etc.
    """
