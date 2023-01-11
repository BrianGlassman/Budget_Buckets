from abc import ABC as _import_ABC
from abc import abstractmethod as _import_abstractmethod
import csv as _import_csv
import datetime as _import_datetime
from dateutil import parser as _import_date_parser

from Record import RawRecord

def _make_date(raw):
    # Ensure date is a consistent type to avoid many, many headaches
    # Can't use isinstance, because datetime.datetime is a subclass of datetime.date
    if type(raw) is _import_datetime.date:
        return raw
    elif isinstance(raw, _import_datetime.date):
        raise NotImplementedError("Don't know how to handle non-date datetimes yet")
    elif isinstance(raw, str):
        return _import_date_parser.parse(raw).date()
    else:
        raise TypeError("Unknown type: " + str(type(raw)))

class BaseParser(_import_ABC):
    transactions: list[RawRecord]
    def __init__(self, account, infile):
        assert account is not None, f"{self.__class__.__name__} parse method called without specifying account"
        self.account = account

        self.infile = infile

        super().__init__()

        self.transactions = self._parse()

    @_import_abstractmethod
    def _parse(self) -> list[RawRecord]: pass

class BaseUSAAParser(BaseParser):
    pass

class USAAParser(BaseUSAAParser):
    """
    Parser for handling csv output files from USAA.
    File has a header with fields:
    Date, Description, Original Description, Category, Amount, Status
    """
    # Somewhere (maybe around late 2022?) USAA changed the export format. This is for parsing things after that change
    def _parse(self):
        with open(self.infile, 'r') as f:
            return [self._make_transaction(line) for line in _import_csv.DictReader(f)]

    def _make_transaction(self, line) -> RawRecord:
        line = dict(line) # Copy so that it can be modified
        date = _make_date(line.pop('Date'))
        desc = line.pop('Description')
        value = float(line.pop('Amount'))
        # Anything left in the line is source-specific values
        return RawRecord(account = self.account, date = date, desc = desc, value = value, source_specific = line)
    
class OldUSAAParser(BaseUSAAParser):
    """
    Parser for handling csv output files from USAA.
    Files have no header, csv with lines of the form:
    [string status],,[string MM/DD/YYYY],,[string description],[string category],[float value]

    Note: value is -[float] for expenses, --[float] for income
    """
    # Somewhere (maybe around late 2022?) USAA changed the export format. This is for parsing things before that change

    _fieldnames = ['status', 'idk', 'date', 'custom_desc', 'auto_desc', 'auto_cat', 'value']

    def _parse(self):
        """Parse the file into transactions."""
        with open(self.infile, 'r') as f:
            return [self._make_transaction(line) for line in _import_csv.DictReader(f, self._fieldnames)]

    def _combine_desc(self, custom_desc: str, auto_desc: str) -> str:
        """Combines custom_desc and auto_desc
        Args:
            custom_desc (str): manually input description
            auto_desc (str): automatically generated description
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

    def _make_transaction(self, line) -> RawRecord:
        line = dict(line) # Copy so that it can be modified
        date = line.pop('date')
        desc = self._combine_desc(line.pop("custom_desc"), line.pop("auto_desc"))
        value = float(line.pop('value').replace('--', ''))
        # Anything left in the line is source-specific values
        return RawRecord(account = self.account, date = date, desc = desc, value = value, source_specific = line)

def run() -> list:
    """
    Parse all the data sources
    Returns a list of RawRecords
    """
    import os
    assert os.path.exists("Raw_Data"), "Raw_Data folder does not exist (Git ignores it)"

    transactions: list = []
    for parseCls, account, file in [
        (USAAParser, "Checking", "2021q4_chk.csv"),
        (USAAParser, "Checking", "2022_chk.csv"),
        (USAAParser, "Credit Card", "2021q4_cc.csv"),
        (USAAParser, "Credit Card", "2022_cc.csv"),
        (USAAParser, "M1", "M1_manual.csv"),
        (USAAParser, "FStocks", "Fidelity_Investment_manual.csv"),
        (USAAParser, "Roth IRA", "Fidelity_RothIRA_manual.csv"),
        (USAAParser, "Trad IRA", "Fidelity_TradIRA_manual.csv"),
        (USAAParser, "401(k)", "PrudentialEmpower_401k_manual.csv"),
        ]:
        file = os.path.join("Raw_Data", file)
        parser = parseCls(account, file)
        transactions.extend(parser.transactions)
    return transactions
