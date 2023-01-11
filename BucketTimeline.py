from matplotlib import pyplot as plt
from matplotlib.transforms import Bbox

import Record

#%% Parsing
import Parsing

transactions: list[Record.RawRecord]
transactions = Parsing.run()

#%% Categorizing
import Categorize
from Root import Constants

limit = -1 # Use -1 for all
use_uncat = False # Whether to show uncategorized items
use_cat = True # Whether to show categorized items

categorized_transactions = Categorize.run(
    transactions=transactions, limit=limit, use_uncat=use_uncat, use_cat=use_cat, use_internal=False)

categorized_transactions = [x for x in categorized_transactions if
    x.category not in ('401k',) # Not relevant
    and
    x.category not in Constants.income_categories # Not really a bucket
    ]

#%% Display pre-processing

# Sort by date
sorted_transactions = sorted(categorized_transactions, key = lambda item: item.date)

# Track values
import datetime
import Record # TODO? Only needed for type-hinting, so probably a way to get rid of this import

class BaseTracker():
    _cat_tracker: dict[str, dict[datetime.date, float | None]]

    def __init__(self, dated_transactions: list[Record.CategorizedRecord]): pass

    def get_category(self, key: str) -> dict[datetime.date, float | None]:
        """Gets the values across all days for a given category"""
        assert key in Constants.categories_inclTodo
        return self._cat_tracker[key]

    def get_date(self, key: datetime.date) -> dict[str, float | None]:
        """Gets the values across all categories for a given day"""
        assert type(key) is datetime.date
        ret = {}
        for cat, values in self._cat_tracker.items():
            ret[cat] = values[key]
        return ret

    def get(self, key: str | datetime.date) -> dict[datetime.date, float | None] | dict[str, float | None]:
        if isinstance(key, str):
            return self.get_category(key)
        elif type(key) is datetime.date:
            return self.get_date(key)
        else:
            raise ValueError(f"Unknown key: '{key}' of type '{type(key)}'")

    @property
    def categories(self):
        return self._cat_tracker.keys()

class DeltaTracker(BaseTracker):
    def __init__(self, dated_transactions: list[Record.CategorizedRecord]):
        # Note: dated_transactions must be sorted

        # Initialize the categorized tracker
        self._cat_tracker = {cat:{} for cat in Constants.categories_inclTodo}

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
                old_value = self._cat_tracker[t.category][date]
                if old_value is None:
                    new_value = t.value
                else:
                    new_value = old_value + t.value
                self._cat_tracker[t.category][date] = new_value

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
        for tracker in self._cat_tracker.values():
            if date in tracker: raise RuntimeError(f"Date {date} already exists")
            tracker[date] = None
delta_tracker = DeltaTracker(sorted_transactions)

class Bucket:
    def __init__(self, name, max_value, monthly_refill):
        self.name = name
        self.max_value = max_value
        self.refill = monthly_refill / 30

class BucketTracker(BaseTracker):
    _empty_bucket = Bucket("empty", 0, 0)
    def __init__(self, delta_tracker: DeltaTracker, initial_date: datetime.date, final_date: datetime.date, bucket_info: dict[str, Bucket] = {}):
        """refill_amts - {category: amount to add per DAY}"""
        self._cat_tracker = {}
        self.transaction_dates: dict[str, list[datetime.date]]
        self.transaction_dates = {}
        for cat in delta_tracker.categories:
            tracker = self._cat_tracker[cat] = {} ; tracker: dict[datetime.date, float | None]
            tdates = self.transaction_dates[cat] = [] ; tdates: list[datetime.date]
            dtracker = delta_tracker.get_category(cat)
            bucket = bucket_info.get(cat, self._empty_bucket)
            refill = bucket.refill

            # Skip categories that never change
            if refill == 0 and all(v is None for v in dtracker.values()):
                tracker[initial_date] = None
                continue

            # Calculate the value for each day (previous day + transactions + refilling)
            last_value = 0 # Initial value or value of previous day
            date = initial_date
            while date <= final_date:
                # Handle transactions
                if date in dtracker:
                    tvalue = dtracker[date]
                    if tvalue is None:
                        tvalue = 0
                    else:
                        # Include the delta value, and mark this date as having a transaction
                        tdates.append(date)
                else:
                    tvalue = 0

                # Handle refilling and max value
                fill = refill + tvalue
                new_value = last_value + fill
                if new_value > bucket.max_value:
                    fill = bucket.max_value - last_value
                    new_value = bucket.max_value
                
                # Save the value
                tracker[date] = new_value

                # Increment for next loop
                date += Constants.one_day
                last_value = new_value

    def plot(self, ax: plt.Axes, category: str) -> None:
        """Plot the values for the given category on the given Axes"""
        value_timeline = self.get_category(category)
        tval_timeline = {date:v for date,v in value_timeline.items() if date in self.transaction_dates[category]}
        if all(v is None for v in value_timeline.values()): return # Don't plot unused categories
        # Plot transaction points
        line = ax.plot(tval_timeline.keys(), tval_timeline.values(), '.', label=category)[0]
        # Plot bucket value including refills (no label, so doesn't show up on auto-legend)
        ax.plot(value_timeline.keys(), value_timeline.values(), '-', color=line.get_color(), linewidth=0.5)

    def plot_all(self, ax: plt.Axes):
        """Sugar syntax to call plot on all categories"""
        for cat in self.categories:
            self.plot(ax, cat)

bucket_info = {
    # Car
    'Car - Note': (320, 320),
    'Car/Rental Insurance': (150, 150),
    'Car - Other': (100, 20),
    'Car - Parking Pass': (50, 20), # TODO change to just "Parking" or split pass from incidental. Can't do until after porting over old sheet

    # Education
    'Self-improvement': (0, 0),

    # Entertainment
    'Dates': (75, 20),
    'Entertainment - Other': (75, 20),
    'Games': (75, 20),
    'Going Out': (75, 20),
    'Books': (75, 20),
    'Big Fun': (0, 20), # TODO shouldn't be zero, but then the graph gets messy

    # Food
    'Groceries': (300, 200),
    'Food - nice': (100, 35),

    # Housing
    'Rent': (1850, 1850),
    'Utilities': (200, 150),
    'Internet': (40.41, 40.41),
    'Housing - Other': (50, 20),
    'Decoration': (50, 20),

    # Investments/Savings
    '401k': (0, 0),
    'Retirement': (0, 0),
    'Long-term': (0, 0),
    'Unexpected Fund': (0, 0),

    # Medical/Dental
    'Medical - Other': (200, 20),
    'Medical Insurance': (0, 0),

    # Other
    'ATM': (200, 20),
    'Other - Other': (200, 20),

    # Personal Care / Clothing
    'Clothes/Personal care': (100, 30),
}
bucket_info = {category:Bucket(category, max_value, monthly_refill) for category, (max_value, monthly_refill) in bucket_info.items()}
bucket_tracker = BucketTracker(delta_tracker,
    initial_date=sorted_transactions[0].date, final_date=sorted_transactions[-1].date,
    bucket_info=bucket_info)

#%% Display

# Legend outside and scrollablehttps://stackoverflow.com/a/55869324

fig, ax = plt.subplots()
fig.subplots_adjust(right=0.75)
bucket_tracker.plot_all(ax)
ax.grid(True)
legend = ax.legend(bbox_to_anchor=(1.05, 1.0))

_scroll_pixels = {'down': 30, 'up': -30}
def scroll(event):
    if not legend.contains(event): return
    bbox = legend.get_bbox_to_anchor()
    bbox = Bbox.from_bounds(bbox.x0, bbox.y0+_scroll_pixels[event.button], bbox.width, bbox.height)
    tr = legend.axes.transAxes.inverted()
    legend.set_bbox_to_anchor(bbox.transformed(tr))
    fig.canvas.draw_idle()
fig.canvas.mpl_connect("scroll_event", scroll)

plt.show()
