# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 13:26:53 2020

@author: Brian Glassman
"""


# from database.raw_input import RawTransaction # TODO change when it moves to library
from database import raw_input

# Read in raw data from various input files
transactions = []
transactions.extend(raw_input.parse('2018_cc.csv',
                                    raw_input.USAA_parser,
                                    account='Credit Card'))
transactions.extend(raw_input.parse('2018_chk.csv',
                                    raw_input.USAA_parser,
                                    account='Checking'))

# Sort chronologically
transactions.sort(key = lambda x: x.date)