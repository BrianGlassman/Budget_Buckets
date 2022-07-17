# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 19:43:08 2020

@author: Brian Glassman
"""

#%% Create log from Excel
from database.raw_input import excel_parser
excel_log = excel_parser.parse()
excel_log.sort(key = lambda x: x.date)

print(excel_log[0])

#%% Create log from Python
from a import transactions as python_log
python_log.sort(key = lambda x: x.date)

#%% Compare the logs
results = [p in excel_log for p in python_log]
print(results.index(False))
