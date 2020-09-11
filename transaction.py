# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 15:54:20 2020

@author: Brian Glassman

Class definitions for different types of transactions
"""

#%% Imports
import datetime
import dateutil
import dataclasses
# from dataclasses import dataclass
import re # Needed for isinstance check

from templates import templates

#%% RawTransactions
@dataclasses.dataclass
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

    def __make_date(self, raw):
        """Convert input to the appropriate type"""

        # Ensure date is a consistent type to avoid many, many headaches
        # Can't use isinstance, because datetime.datetime is a subclass of datetime.date
        if type(raw) is datetime.date:
            return raw
        elif isinstance(raw, datetime.date):
            return raw.date()
        else:
            return dateutil.parser.parse(raw).date()

    def to_dict(self):
        """Return a dictionary of the contained values"""
        return self.__dict__

    # Helper functions to check different fields
    def __check_desc(self, pattern):
        """Assumes that pattern contains a desc field"""
        mask = pattern['desc']
        desc = self.desc
        if isinstance(mask, re.Pattern):
            # Regex matching (None if no match found)
            return mask.search(desc) is not None
        elif isinstance(mask, str):
            # Exact string matching
            return desc == mask
        else:
            raise NotImplementedError("Unknown mask type")
    def __check_value(self, pattern):
        """Assumes that pattern contains a value field"""
        mask = pattern['value']
        if isinstance(mask, (int, float)):
            # Exact value matching
            return self.value == mask
        else:
            # Range matching
            assert len(mask) == 2
            assert mask[0] < mask[1]
            return mask[0] <= self.value <= mask[1]

    # Mapping from field name to helper function
    _checker = {'desc': __check_desc,
                'value': __check_value,
                }

    def match_templates(self):
        """Check self against the common templates. Return whichever template
        matches, or None if no match"""

        matched = None
        # Check the transaction against all templates in order
        for template in templates:
            old = template['old']
            match = True
            for key in old:
                # Run the checker for each field that has a pattern
                match = match and self._checker[key](self, old)
                if not match: break # Exit loop if any pattern fails

            if match:
                # Template matched, stop searching
                matched = template
                break
        return matched

    def apply_template(self, template):
        """Convert self from RawTransaction to one or more Transactions as
        specified by the template"""

        new = template['new']
        if isinstance(new, dict):
            # One-to-one conversion, make a list for iterating
            new = [new]
        else:
            # Assume one-to-many conversion, already a list
            pass

        ret = []
        for n in new:
            # TODO use alternate constructor once implemented
            #   Or some other smart way of converting RawTransaction to Transaction
            # Deep copy n to avoid changing the base common templates
            n = dict(n)
            n['recurrence'] = n.pop('split')

            d = self.to_dict()
            d.update(n)
            # Keep only keys that are used for Transaction
            d = {k:v for k,v in d.items() if k in Transaction.fields()}
            ret.append(Transaction(**d))
        return ret

def test_checker():
    #TODO test splitting transaction
    #TODO test trivial cases
    #TODO test value range matching
    return True

def test_RawTransaction():
    # TODO
    # date as string
    # date as datetime.datetime
    # date as datetime.date
    # empty description
	# value as int
	# value as float
	# value as negative int
	# value as negative float
    # value as string like "##.##" <-- normal case float
    # value as string like "##" <-- normal case int
    # value as string like "-##.####" <-- normal case negative float
    # value as string like "-##" <-- normal case negative int
    # value as string like "$##.##"
    # should NOT test any weirder values. That's the parser's job to take care of
    return True

#%% Transaction

@dataclasses.dataclass
class Transaction:
    """Transactions as used internally (has been split, categorized, etc.)"""

    date: datetime.date
    value: float
    desc: str
    category: str
    recurrence: str
    # TODO add raw_id and mod_id

    # TODO alternate constructor for creating Transaction out of RawTransaction

    def __init__(self, date, value, desc=None, category=None, recurrence=None):
        self.date = self.__make_date(date)
        self.value = float(value)
        self.desc = desc if desc is not None else ""
        self.category = category
        self.recurrence = recurrence

    def __make_date(self, raw):
        """Convert input to the appropriate type"""

        # Ensure date is a consistent type to avoid many, many headaches
        # Can't use isinstance, because datetime.datetime is a subclass of datetime.date
        if type(raw) is datetime.date:
            return raw
        elif isinstance(raw, datetime.date):
            return raw.date()
        else:
            return dateutil.parser.parse(raw).date()

    @staticmethod
    def fields():
        """Return a list of field names as strings"""
        return [x.name for x in dataclasses.fields(Transaction)]
