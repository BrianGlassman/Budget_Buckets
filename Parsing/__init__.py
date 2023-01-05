from abc import ABC as _import_ABC
from abc import abstractmethod as _import_abstractmethod
import csv as _import_csv

from Record import RawRecord

class BaseParser(_import_ABC):
    def __init__(self, account, infile):
        assert account is not None, f"{cls.__class__.__name__} parse method called without specifying account"
        self.account = account

        self.infile = infile

        super().__init__()

        self.transactions = self._parse()

    @_import_abstractmethod
    def _parse(self): pass

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
        date = line.pop('Date')
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
