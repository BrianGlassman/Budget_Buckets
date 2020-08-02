# -*- coding: utf-8 -*-
"""
Created on Sat Aug  1 16:32:23 2020

@author: Brian Glassman


#%%
Parses raw input files from banks, Venmo, etc.

TODO
    should parsers be functions or classes?
        Classes make it easier to group information and helper methods
"""

#%%
# TODO move to library
import datetime
import dateutil
from dataclasses import dataclass
@dataclass
class RawTransaction:
    """Transactions as read in from raw input files."""
    date: datetime.date
    value: float
    desc: str
    auto_cat: str
    account: str

    def __init__(self, date, value, desc=None, auto_cat=None, account=None):
        self.date = self.__make_date(date)
        self.value = float(value)
        self.desc = desc if desc is not None else ""
        self.auto_cat = auto_cat
        self.account = account

    def __post_init__(self):
        """Format fields correctly.

        Use dataclass post_init rather than redefining __init__ entirely
        to keep using the auto-generated repr and other methods"""

        # Ensure date is a consistent type to avoid many, many headaches
        assert isinstance(self.date, datetime.date), \
            f"Date field must be a datetime.date instance, got {type(self.date)}"

    def __make_date(self, raw):
        """Convert input to the appropriate type"""
        return dateutil.parser.parse(raw).date()

#%%
import csv
from abc import ABC

def parse(infile, parser, *args, **kwargs):
    """Run the provided parsing logic on the given file."""
    return parser.parse(infile, *args, **kwargs)

class USAA_parser(ABC):
    """Namespace for handling csv output files from USAA.

    Files have no header, csv with lines of the form:
    [string status],,[string MM/DD/YYYY],,[string description],[string category],[float value]

    Note: value is -[float] for expenses, --[float] for income
    """

    fieldnames = ['status', 'idk', 'date', 'custom_desc', 'auto_desc', 'auto_cat', 'value']

    @classmethod
    def parse(cls, infile, account):
        """Parse the line.

        Args:
            infile (file path): path to the input file to open
            account (string): the account to tag transactions as
        """
        assert account is not None, "USAA parser called without specifying account"
        with open(infile, 'r') as f:
            return [cls.make_transaction(line, account) for line in csv.DictReader(f, cls.fieldnames)]

    @classmethod
    def make_transaction(cls, line, account):
        """Convert a line from the input file into a RawTransaction object.

        Args:
            line (dict of strings): the line read in from the input file
            account (string): the account to tag transactions as
        Returns:
            raw_transaction object
        """
        desc = cls.get_desc(**line)
        value = cls.format_value(**line)
        return RawTransaction(date = line['date'],
                              desc = desc,
                              auto_cat = line['auto_cat'],
                              value = value,
                              account = account)

    @staticmethod
    def get_desc(custom_desc, auto_desc, **excess):
        """Combines custom_desc and auto_desc
        Args:
            custom_desc (str): manually input description
            auto_desc (str): automatically generated description
            **excess: unused fields from the input line
        Returns:
            one desc filled: return unchanged
            both filled: "[auto] --- [custom]"
            neither: empty string
        """
        if custom_desc and auto_desc:
            return f"{auto_desc} --- {custom_desc}"
        elif custom_desc and (not auto_desc): return custom_desc
        elif (not custom_desc) and auto_desc: return auto_desc
        elif (not custom_desc) and (not auto_desc): return ""
        else: raise RuntimeError # Shouldn't be possible

    @staticmethod
    def format_value(value, **excess):
        """Properly format the value
        Args:
            value (str): monetary value. Positive values may have "--" prefix
            **excess: unused fields from the input line
        Returns:
            value as a float
        """
        if value.startswith('--'):
            return float(value[2:])
        else:
            return float(value)


def venmo_parser():
    """
    Two line header of the form:
     Username,ID,Datetime,Type,Status,Note,From,To,Amount (total),Amount (fee),Funding Source,Destination,Beginning Balance,Ending Balance,Statement Period Venmo Fees,Year to Date Venmo Fees,Disclaimer
    [string],,,,,,,,,,,,$[float],,,,

    Data lines of the form:
    ,[int],[YYYY-MM-DDTHH:MM:SS],[string type],[string status],[string description],[string payer],[string payee],[+-] $[float],,[string funding source],,,,,,

    Four line footer of the form:
    ,,,,,,,,,,,,,$[float],,,
    ,,,,,,,,,,,,,,$[float],,
    ,,,,,,,,,,,,,,,$[float],
    ,,,,,,,,,,,,,,,,"[multi-line text disclaimer]"

    """

def cash_parser():
    pass