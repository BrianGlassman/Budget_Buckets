from abc import ABC as _import_ABC
from abc import abstractmethod as _import_abstractmethod
import csv as _import_csv
import datetime as _import_datetime
from dateutil import parser as _import_date_parser
import os as _import_os

if __name__ == "__main__":
    import sys
    path = _import_os.path.dirname(__file__)
    path = _import_os.path.dirname(path)
    sys.path.append(path)

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
    fields: list[str]
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
    fields = 'Date,Description,Original Description,Category,Amount,Status'.split(',')
    # Somewhere (maybe around late 2022?) USAA changed the export format. This is for parsing things after that change
    def _parse(self):
        with open(self.infile, 'r') as f:
            fields = f.readline().strip().split(',')
            if fields != self.fields:
                print(fields)
                print('does not match expected')
                print(self.fields)
                raise RuntimeError("Header mismatch")
            return [self._make_transaction(line) for line in _import_csv.DictReader(f, fieldnames=fields)]

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

class FirstBankParser(USAAParser):
    # Only PDF downloads available, so I made a CSV that looks like the USAA CSV
    pass

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
            def __init__(self, name: str, value: float = 0.0, date: _import_datetime.date|None = None):
                self.name = name
                self.value = value
                self.date = date

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

        prev_balance = 0
        final_balance = 0

        # Aggregate charges for each term
        fees = Charge('Fees')
        tuition = Charge('Tuition')
        rent = Charge('Rent')
        insurance = Charge('Insurance')
        meals = Charge('Meal Plan')
        supplies = Charge('Supplies')
        parking = Charge('Parking')
        costs = [fees, tuition, rent, insurance, meals, supplies, parking]

        # Keep transfers un-aggregated for comparing with other accounts
        loans = []
        payments = []
        refunds = []
        def transfers() -> list[Charge]:
            return loans + payments + refunds

        # Parse
        for line in lines:
            words = line.split(' ')
            if self.summary_desc in line:
                # Summary row
                desc = ' '.join(words[0:-1])
                final_balance = float(words[-1].replace(',',''))
                final_balance = -final_balance # Negate to match costs
                assert desc == self.summary_desc, f"Summary desc is actually '{desc}'"
            elif len(words) == 3 and  "PREVIOUS BALANCE" in line:
                # Changes the checksum, but is not a transaction
                prev_balance = float(words[-1].replace(',',''))
                prev_balance = -prev_balance # Negate to match costs
            else:
                # Data row
                date = _import_date_parser.parse(words[0]).date()
                desc = ' '.join(words[1:-1])
                value = float(words[-1].replace(',',''))
                # Use NEGATIVE of value:
                # CU calls it positive when I owe them money, I want that to be an expense (negative)
                value = -value
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
                    loans.append(Charge("Loans", value, date=date))
                elif desc in (
                    "Internet Check Payment",
                    "Internet Check Payment - PP"):
                    payments.append(Charge("Payments", value, date=date))
                elif desc in (
                    "Refund",
                    "Refund-Federal Aid"):
                    refunds.append(Charge("Refunds", value, date=date))
                else:
                    raise NotImplementedError(f"No rule for '{desc}'")
        
        # Checksumming
        bill_sum = round(prev_balance + sum(costs) + sum(transfers()), 2)
        balance = round(final_balance, 2)
        assert bill_sum == balance, f"${bill_sum:0,.2f} != ${balance:0,.2f}"

        transactions: list[RawRecord] = []
        # Pretend all the costs took place on the first day of the term
        for item in costs:
            if item.value != 0:
                rec = RawRecord(self.account, self.date, self.prefix+item.name, item.value)
                transactions.append(rec)
        # Use the real date for transfers to make comparison with other accounts easier
        for item in transfers():
            assert item.value != 0
            assert item.date is not None
            rec = RawRecord(self.account, item.date, self.prefix+item.name, item.value)
            transactions.append(rec)
        
        return transactions

def parse_file(parseCls, account: str, filepath: str):
    parser = parseCls(account, filepath)
    parser: BaseParser
    return parser.transactions

def run() -> list[RawRecord]:
    """
    Parse all the data sources
    Returns a list of RawRecords
    """
    assert _import_os.path.exists("Raw_Data"), "Raw_Data folder does not exist (Git ignores it)"

    transactions: list[RawRecord] = []
    for parseCls, account, file in [
        (USAAParser, "Checking", "2021q4_chk.csv"),
        (USAAParser, "Checking", "2022_chk.csv"),
        (USAAParser, "Checking", "2023_chk.csv"),
        (USAAParser, "Credit Card", "2021q4_cc.csv"),
        (USAAParser, "Credit Card", "2022_cc.csv"),
        (USAAParser, "Credit Card", "2023_cc.csv"),
        (USAAParser, "M1", "M1_manual.csv"),
        (USAAParser, "FStocks", "Fidelity_Investment_manual.csv"),
        (USAAParser, "Roth IRA", "Fidelity_RothIRA_manual.csv"),
        (USAAParser, "Trad IRA", "Fidelity_TradIRA_manual.csv"),
        (USAAParser, "401(k)", "PrudentialEmpower_401k_manual.csv"),
        (FirstBankParser, "529", "529.csv"),
        ]:
        file = _import_os.path.join("Raw_Data", file)
        transactions.extend(parse_file(parseCls=parseCls, account=account, filepath=file))
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
        file = _import_os.path.join("Raw_Data", file)
        date = _import_date_parser.parse(date).date()
        try:
            parser = CUParser("CU Bills", file, prefix, date)
        except Exception:
            print(file)
            raise
        transactions.extend(parser.transactions)
    return transactions

if __name__ == "__main__":
    run()