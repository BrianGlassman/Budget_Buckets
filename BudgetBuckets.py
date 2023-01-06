#%% Parsing
import Parsing

transactions = []
for parser in [
    Parsing.USAAParser("Checking", "2022_chk.csv"),
    Parsing.USAAParser("Credit Card", "2022_cc.csv")
    ]:
    transactions.extend(parser.transactions)

#%% Categorizing
import Record
import Categorize
from Root import Constants

limit = -1 # Use -1 for all
use_uncat = True # Whether to show uncategorized items
use_cat = True # Whether to show categorized items

categorized_transactions = []
for baseRecord in transactions:
    match = Categorize.match_templates(baseRecord)
    if match is None:
        if use_uncat:
            category = '*** TODO ***'
        else:
            continue
    else:
        category = match['new']['category']
        assert category in Constants.categories, f"Bad category: {category}"
        if not use_cat:
            continue
    ct = Record.CategorizedRecord(baseRecord, category)
    categorized_transactions.append(ct)

    if len(categorized_transactions) == limit:
        break

#%% Display pre-processing

# Convert dates to datetime.date objects (just the date, no time)
import datetime
from dateutil import parser as date_parser

def _make_date(raw):
    # Ensure date is a consistent type to avoid many, many headaches
    # Can't use isinstance, because datetime.datetime is a subclass of datetime.date
    if type(raw) is datetime.date:
        return raw
    elif isinstance(raw, datetime.date):
        return raw.date()
    else:
        return date_parser.parse(raw).date()
for t in categorized_transactions:
    t.date = _make_date(t.date)
dated_transactions = categorized_transactions ; del categorized_transactions

# Sort by date
dated_transactions = sorted(dated_transactions, key = lambda item: item.date)

# Aggregate values per day
start = dated_transactions[0].date
stop = dated_transactions[-1].date
dates = []
values = []
for int_delta in range(0, (stop - start).days):
    timedelta = datetime.timedelta(days = int_delta)
    date = start + timedelta
    dates.append(date)
    value = 0
    for t in dated_transactions:
        if t.date == date:
            value += t.value
    values.append(value)

#%% Display
from matplotlib import pyplot as plt

fig, ax = plt.subplots()
ax.plot(dates, values, '.')
ax.grid(True)

plt.show()
