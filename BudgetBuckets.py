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
use_uncat = False # Whether to show uncategorized items
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

# Sort by date
sorted_transactions = sorted(categorized_transactions, key = lambda item: item.date)

# Track values
import datetime
import Record # TODO? Only needed for type-hinting, so probably a way to get rid of this import
class Tracker():
    cat_tracker: dict[str, dict[datetime.date, float | None]]
    dates: set[datetime.date]
    def __init__(self, dated_transactions: list[Record.CategorizedRecord]):
        # Note: dated_transactions must be sorted

        # Initialize the categorized tracker
        self.cat_tracker = {cat:{} for cat in Constants.categories}

        # Initialize the date map
        self.dates = set()

        # Setup the first day
        one_day = datetime.timedelta(days=1)
        i = 0 # Index within dated_transactions
        t = dated_transactions[i]
        date = t.date
        self.create_day(date)

        # Fill in the trackers
        while i < len(dated_transactions):
            # Add the transactions until one has a different (later) date
            while date == t.date:
                old_value = self.cat_tracker[t.category][date]
                if old_value is None:
                    new_value = t.value
                else:
                    new_value = old_value + t.value
                self.cat_tracker[t.category][date] = new_value

                i += 1
                if i == len(dated_transactions): break
                t = dated_transactions[i]
            if i == len(dated_transactions): break

            # Go to tomorrow
            date += one_day

            # Add days until the next transaction is reached
            while date < t.date:
                self.create_day(date)
                date += one_day
            self.create_day(date)

    def create_day(self, date: datetime.date) -> None:
        """Create a new date, with 0 for all category values"""
        if date in self.dates: raise RuntimeError(f"Date {date} already exists")
        
        self.dates.add(date)
        for tracker in self.cat_tracker.values():
            tracker[date] = None

    def get_category(self, key: str) -> dict[datetime.date, float | None]:
        """Gets the values across all days for a given category"""
        assert key in Constants.categories
        return self.cat_tracker[key]

    def get_date(self, key: datetime.date) -> dict[str, float | None]:
        """Gets the values across all categories for a given day"""
        assert type(key) is datetime.date
        ret = {}
        for cat, values in self.cat_tracker.items():
            ret[cat] = values[key]
        return ret

    def get(self, key: str | datetime.date) -> dict[datetime.date, float | None] | dict[str, float | None]:
        if key in Constants.categories:
            return self.get_category(key)
        elif type(key) is datetime.date:
            return self.get_date(key)
        else:
            raise ValueError(f"Unknown key: '{key}' of type '{type(key)}'")
tracker = Tracker(sorted_transactions)

#%% Display
from matplotlib import pyplot as plt

values = tracker.get_category("Food - nice")

fig, ax = plt.subplots()
ax.plot(values.keys(), values.values(), '.')
ax.grid(True)

plt.show()
