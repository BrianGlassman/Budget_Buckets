from abc import ABC as _import_ABC
from abc import abstractmethod as _import_abstractmethod
import csv as _import_csv
import datetime as _import_datetime
from dateutil import parser as _import_date_parser
import os as _import_os

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
    def __init__(self, account: str, infile: str):
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

class CUParser(BaseParser):
    summary_desc = "Billing Hours Activity Through Amount Due"

    def __init__(self, account: str, infile: str, prefix: str, date: _import_datetime.date, ):
        if prefix[-1] != ' ':
            prefix = prefix + ' '
        self.prefix = prefix

        self.date = date

        super().__init__(account, infile)

    def _parse(self):
        """Parse the file into transactions."""        
        with open(self.infile, 'r') as f:
            lines = f.readlines()
        lines = [x.strip() for x in lines]

        checksum = 0
        fees = 0
        tuition = 0
        rent = 0
        insurance = 0
        for line in lines:
            words = line.split(' ')
            if self.summary_desc in line:
                # Summary row
                desc = ' '.join(words[0:-1])
                assert checksum == 0, "Multiple summary rows found?"
                checksum = float(words[-1].replace(',',''))
                assert desc == self.summary_desc, f"Summary desc is actually '{desc}'"
            else:
                # Data row
                desc = ' '.join(words[1:-1])
                value = float(words[-1].replace(',',''))
                if desc == "Family Housing Rent":
                    rent += value
                elif desc == "Student Health Insurance Plan":
                    insurance += value
                elif desc.endswith(" Fee") or " Fee " in desc:
                    fees += value
                elif "Tuition " in desc: 
                    tuition += value
                elif " PostPandemicTuit Cred" in desc:
                    tuition += value
                else:
                    raise NotImplementedError(f"No rule for '{desc}'")

        # Checksumming
        assert fees + tuition + rent + insurance == checksum

        transactions: list[RawRecord] = []
        if fees != 0:
            rec = RawRecord(self.account, self.date, self.prefix+"Fees", fees)
            transactions.append(rec)
        if tuition != 0:
            rec = RawRecord(self.account, self.date, self.prefix+"Tuition", tuition)
            transactions.append(rec)
        if rent != 0:
            rec = RawRecord(self.account, self.date, self.prefix+"Rent", rent)
            transactions.append(rec)
        if insurance != 0:
            rec = RawRecord(self.account, self.date, self.prefix+"Insurance", insurance)
            transactions.append(rec)
        
        return transactions

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
    for file, prefix, date in [
        ("CU_Fall2021.txt", "CU Fall 2021", "08/23/2021"),
        # ("CU_Spring2022.txt") "CU Spring 2022", "01/10/2022"),
        # ("CU_Summer2022.txt") "CU Summer 2022", "05/23/2022"),
        # ("CU_Fall2022.txt") "CU Fall 2022", "08/22/2022"),
        # ("CU_Spring2023.txt") "CU Spring 2023", "01/17/2023"),
        ]:
        file = os.path.join("Raw_Data", file)
        date = _import_date_parser.parse(date).date()
        parser = CUParser("CU Bills", file, prefix, date)
        transactions.extend(parser.transactions)
    return transactions
