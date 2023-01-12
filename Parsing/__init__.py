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
        date = _make_date(line.pop('Date'))
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

        class Charge:
            def __init__(self, name: str, value: float = 0.0):
                self.name = name
                self.value = value

            def add(self, other) -> None:
                self.value += other

            def __add__(self, other) -> float:
                if isinstance(other, (int, float)):
                    return self.value + other
                elif isinstance(other, Charge):
                    return self.value + other.value
                else:
                    raise NotImplementedError(type(other))

            def __radd__(self, other) -> float:
                return self + other

            def __round__(self, *args, **kwargs):
                return self.value.__round__(*args, **kwargs)

        checksum = Charge('checksum')
        loans = Charge('Loans')
        fees = Charge('Fees')
        tuition = Charge('Tuition')
        rent = Charge('Rent')
        insurance = Charge('Insurance')
        meals = Charge('Meal Plan')
        supplies = Charge('Supplies')
        parking = Charge('Parking')
        costs = [fees, tuition, rent, insurance, meals, supplies, parking]
        for line in lines:
            words = line.split(' ')
            if self.summary_desc in line:
                # Summary row
                desc = ' '.join(words[0:-1])
                checksum.add(float(words[-1].replace(',','')))
                assert desc == self.summary_desc, f"Summary desc is actually '{desc}'"
            elif len(words) == 3 and  "PREVIOUS BALANCE" in line:
                # Changes the checksum, but is not a transaction
                value = float(words[-1].replace(',',''))
                checksum.add(-value)
            else:
                # Data row
                desc = ' '.join(words[1:-1])
                value = float(words[-1].replace(',',''))
                if desc in  ("Family Housing Rent", "GFH Security Deposit"):
                    rent.add(value)
                elif desc == "Student Health Insurance Plan":
                    insurance.add(value)
                elif desc.endswith(" Fee") or " Fee " in desc:
                    fees.add(value)
                elif "Tuition " in desc: 
                    tuition.add(value)
                elif " PostPandemicTuit Cred" in desc:
                    tuition.add(value)
                elif desc == "Housing Block Meal Plan":
                    meals.add(value)
                elif desc == "Bookstore Supply Charges":
                    supplies.add(value)
                elif desc == "Finance Charge":
                    assert value < 1, "Unexpectedly large finance charge"
                    supplies.add(value)
                elif desc == "Parking Permit":
                    parking.add(value)
                elif 'Direct Unsubsidized Loan' in desc:
                    loans.add(-value)
                elif desc in (
                    "Internet Check Payment",
                    "Internet Check Payment - PP",
                    "Refund",
                    "Refund-Federal Aid"):
                    # Changes the checksum, but is not a transaction
                    checksum.add(-value)
                else:
                    raise NotImplementedError(f"No rule for '{desc}'")
        
        # Checksumming
        assert round(sum(costs), 2) == round(checksum + loans, 2), f"{sum(costs)} != {checksum + loans}"

        transactions: list[RawRecord] = []
        for item in costs + [loans]:
            if item.value != 0:
                rec = RawRecord(self.account, self.date, self.prefix+item.name, item.value)
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
        ('CU_2021-08-10_bill.txt',   'CU Fall 2021', '08/23/2021'),
        ('CU_2021-10-12_bill.txt',   'CU Fall 2021', '08/23/2021'),
        ('CU_2022-01-11_bill.txt', 'CU Spring 2022', '01/10/2022'),
        ('CU_2022-02-08_bill.txt', 'CU Spring 2022', '01/10/2022'),
        ('CU_2022-06-08_bill.txt', 'CU Summer 2022', '05/23/2022'),
        ('CU_2022-08-09_bill.txt',   'CU Fall 2022', '08/22/2022'),
        ('CU_2022-09-13_bill.txt',   'CU Fall 2022', '08/22/2022'),
        ('CU_2022-10-11_bill.txt',   'CU Fall 2022', '08/22/2022'),
        ('CU_2022-11-08_bill.txt',   'CU Fall 2022', '08/22/2022'),
        ('CU_2022-12-13_bill.txt',   'CU Fall 2022', '08/22/2022'),
        ('CU_2023-01-10_bill.txt', 'CU Spring 2023', '01/17/2023')
        ]:
        # TODO may want to combine charges from all bills in a single term (i.e. tuition and refund)
        file = os.path.join("Raw_Data", file)
        date = _import_date_parser.parse(date).date()
        try:
            parser = CUParser("CU Bills", file, prefix, date)
        except Exception:
            print(file)
            raise
        transactions.extend(parser.transactions)
    return transactions
