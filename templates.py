# -*- coding: utf-8 -*-
"""
Created on Thu Sep 10 11:28:49 2020

@author: Brian Glassman
"""

import re

#TODO replace with named tuple or custom class so keys aren't just strings
#TODO save off as a file (JSON needs lots of formatting and custom re parser)

# Regex notes:
#   \*{11} matches exactly 11 asterisks
templates = [# Utilities / Rent
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
                 'new': [{'value': -1650, 'category': 'Rent', 'split': 30},
                         {'value': -40, 'category': 'Utilities', 'split': 30}]},

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
                 'new': {'desc': 'Spotify',
                         'category': 'Entertainment - Other', 'split': 30}},
             {#//Car note
                 'old': {'desc': re.compile('^HONDA PMT        8004489307 \*{11}'),
                         'value': -320},
                 'new': {'category': 'Car - Note', 'split': 30}},
             {#//Insurance
                 'old': {'desc': 'USAA P&amp;C INT     AUTOPAY    ***********1608'},
                 'new': {'category': 'Car/Rental Insurance', 'split': 30}},
            ]