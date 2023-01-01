from abc import ABC as _import_ABC
from abc import abstractmethod as _import_abstractmethod
import csv as _import_csv

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

    def _make_transaction(self, line):
        return line

if __name__ == "__main__":
    # This should fail because it's an ABC
    # TODO assert failure or whatever
    #bp = BaseParser("test", "not_a_file.csv")

    parser = USAAParser("USAA Credit Card", "cc.csv")
    print('\n'.join(str(x) for x in parser.transactions))
