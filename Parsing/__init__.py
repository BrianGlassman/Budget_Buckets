from abc import ABC as _import_ABC
from abc import abstractmethod as _import_abstractmethod
import csv as _import_csv

from Record import Record

class BaseParser(_import_ABC):
    def __init__(self, account, infile):
        assert account is not None, f"{cls.__class__.__name__} parse method called without specifying account"
        self.account = account

        self.infile = infile

        super().__init__()

        self.transactions = self._parse()

    @_import_abstractmethod
    def _parse(self):
        pass
    
class USAAParser(BaseParser):
    """
    Parser for handling csv output files from USAA.
    Files have no header, csv with lines of the form:
    [string status],,[string MM/DD/YYYY],,[string description],[string category],[float value]

    Note: value is -[float] for expenses, --[float] for income
    """
    _fieldnames = ['status', 'idk', 'date', 'custom_desc', 'auto_desc', 'auto_cat', 'value']

    def _parse(self):
        """Parse the file into transactions.
        Args:
            infile (file path): path to the input file to open
        """
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

    def _make_transaction(self, line) -> Record:
        line = dict(line) # Copy so that it can be modified
        date = line.pop('date')
        desc = self._combine_desc(line.pop("custom_desc"), line.pop("auto_desc"))
        amt = float(line.pop('value').replace('--', ''))
        # Anything left in the line is source-specific values
        return Record(account = self.account, date = date, desc = desc, amt = amt, source_specific = line)

if __name__ == "__main__":
    # This should fail because it's an ABC
    # TODO assert failure or whatever
    #bp = BaseParser("test", "not_a_file.csv")

    parser = USAAParser("USAA Credit Card", "cc.csv")
    print('\n'.join(str(x) for x in parser.transactions))
