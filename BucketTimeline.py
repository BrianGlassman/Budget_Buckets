#%% Imports
from matplotlib import pyplot as plt
from matplotlib.transforms import Bbox
import datetime
from collections import UserDict
from typing import TypeVar

from Root import Constants
import Parsing
import Record # TODO? Only needed for type-hinting, so probably a way to get rid of this import

# Type aliasing
Cat = Constants.CatType
Date = datetime.date

#%% Class definitions

T = TypeVar('T')

class BaseCalendar(UserDict[Date, T]):
    """A special case dictionary like {date: object} where dates are not necessarily consecutive"""
    def dates(self):
        return self.keys()

class SparseCalendar(BaseCalendar[T]):
    """No difference from BaseCalendar"""
    pass

class ConsecCalendar(BaseCalendar[T]):
    """A calendar with consecutive dates"""
    
    def verify(self):
        dates = list(self.keys())
        deltas = [new - old for new, old in zip(dates[1:], dates[:-1])]
        assert all(delta.days == 1 for delta in deltas)

class BaseTracker():
    _cat_tracker: dict[Cat, ConsecCalendar]

    def __init__(self, dated_transactions: list[Record.CategorizedRecord]): pass

    def get_category(self, key: Cat) -> ConsecCalendar:
        """Gets the values across all days for a given category"""
        assert key in Constants.categories_inclTodo
        return self._cat_tracker[key]

    def get_date(self, key: Date) -> dict[Cat, float]:
        """Gets the values across all categories for a given day"""
        assert type(key) is Date
        ret = {}
        for cat, values in self._cat_tracker.items():
            ret[cat] = values[key]
        return ret

    def get(self, key: Cat | Date) -> ConsecCalendar | dict[Cat, float]:
        if isinstance(key, Cat):
            return self.get_category(key)
        elif type(key) is Date:
            return self.get_date(key)
        else:
            raise ValueError(f"Unknown key: '{key}' of type '{type(key)}'")

    @property
    def categories(self):
        return self._cat_tracker.keys()

class DeltaTracker(BaseTracker):
    _cat_tracker: dict[Cat, ConsecCalendar] # {category: {date: delta that day}}
    _cat_dates: dict[Cat, list[Date]] # {category: [dates where single-day transactions occurred]}
    _cat_amort: dict[Cat, list[Date]] # {category: [dates where amortized transactions began]}
    def __init__(self, dated_transactions: list[Record.CategorizedRecord]):
        # Note: dated_transactions must be sorted
        categories = Constants.categories_inclTodo

        # Initialize the categorized tracker and date tracker
        self._cat_tracker = {cat:ConsecCalendar() for cat in categories}
        self._cat_dates = {cat:[] for cat in categories}
        self._cat_amort = {cat:[] for cat in categories}

        # Setup the first day
        one_day = Constants.one_day
        i = 0 # Index within dated_transactions
        t = dated_transactions[i]
        date = t.date
        self.create_day(date)

        # Fill in the trackers
        while i < len(dated_transactions):
            transaction_today = {cat:False for cat in categories}
            amortized_today = {cat:False for cat in categories}

            # Add the transactions until one has a different (later) date
            while date == t.date:
                # Check for single-day or amortized transaction
                assert t.duration > 0
                if t.duration == 1:
                    transaction_today[t.category] = True
                else:
                    amortized_today[t.category] = True

                # Add transaction value to today's running total
                self._cat_tracker[t.category][date] += t.value

                i += 1
                if i == len(dated_transactions): break
                t = dated_transactions[i]
            if i == len(dated_transactions): break

            # Note if there was a transaction today
            for cat in categories:
                if transaction_today[cat]:
                    self._cat_dates[cat].append(date)
                if amortized_today[cat]:
                    self._cat_amort[cat].append(date)

            # Go to tomorrow
            date += one_day

            # Add days until the next transaction is reached
            while date < t.date:
                self.create_day(date)
                date += one_day
            self.create_day(date)

        for temp in self._cat_tracker.values():
            temp.verify()
        
    def create_day(self, date: Date) -> None:
        """Create a new date, with 0 for all category values"""
        for tracker in self._cat_tracker.values():
            if date in tracker: raise RuntimeError(f"Date {date} already exists")
            tracker[date] = 0
    
    def get_tdates(self, key: Cat) -> list[Date]:
        """Gets the single-day transaction dates for a given category"""
        assert key in Constants.categories_inclTodo
        return self._cat_dates[key]
    
    def get_adates(self, key: Cat) -> list[Date]:
        """Gets the amortized transaction start dates for a given category"""
        assert key in Constants.categories_inclTodo
        return self._cat_amort[key]

class Bucket:
    def __init__(self, name, max_value, monthly_refill):
        self.name = name
        self.max_value = max_value
        self.refill = monthly_refill / 30

class BucketTracker(BaseTracker):
    _empty_bucket = Bucket("empty", 0, 0)
    def __init__(self, delta_tracker: DeltaTracker, initial_date: Date, final_date: Date, bucket_info: dict[Cat, Bucket] = {}):
        """refill_amts - {category: amount to add per DAY}"""
        self._delta_tracker = delta_tracker

        self._cat_tracker = {}
        for cat in delta_tracker.categories:
            tracker = self._cat_tracker[cat] = ConsecCalendar() ; tracker: ConsecCalendar
            dtracker = delta_tracker.get_category(cat)
            bucket = bucket_info.get(cat, self._empty_bucket)
            refill = bucket.refill

            # Skip categories that never change
            if refill == 0 and all(v == 0 for v in dtracker.values()):
                tracker[initial_date] = 0
                continue

            # Calculate the value for each day (previous day + transactions + refilling)
            last_value = 0 # Initial value or value of previous day
            date = initial_date
            while date <= final_date:
                # Handle transactions
                if date in dtracker:
                    tvalue = dtracker[date]
                else:
                    tvalue = 0

                # Handle refilling and max value
                # Do transaction first, then refill if below max
                new_value = last_value + tvalue
                if new_value < bucket.max_value:
                    new_value += min(refill, bucket.max_value - new_value)
                
                # Save the value
                tracker[date] = new_value

                # Increment for next loop
                date += Constants.one_day
                last_value = new_value

            tracker.verify()

    def _plot_transaction_points(self, values: dict[Date, float], ax: plt.Axes, category: Cat):
        """Plot the points where single-day transactions occurred"""
        values = {date:v for date,v in values.items() if date in self._delta_tracker.get_tdates(category)}
        # Plot transaction points
        line = ax.plot(values.keys(), values.values(), '.', label=category)
        return line[0]
    
    def _plot_amort_points(self, values: dict[Date, float], ax: plt.Axes, category: Cat, color: str):
        """Plot the points where amortized transactions began"""
        values = {date:v for date,v in values.items() if date in self._delta_tracker.get_adates(category)}
        # Plot amortized transaction points (no label, so doesn't show up on auto-legend)
        line = ax.plot(values.keys(), values.values(), 'x', color=color)
        return line[0]

    def _plot_bucket_vals(self, values: dict[Date, float], ax: plt.Axes, color: str):
        """Plot the bucket values"""
        # Plot bucket value including refills (no label, so doesn't show up on auto-legend)
        line = ax.plot(values.keys(), values.values(), '-', color=color, linewidth=0.5)
        return line[0]

    def plot(self, ax: plt.Axes, category: Cat) -> None:
        """Plot the values for the given category on the given Axes"""
        value_timeline = self.get_category(category)
        if len(self._delta_tracker.get_tdates(category)) == 0 and len(self._delta_tracker.get_adates(category)) == 0:
            # Skip categories with no transactions
            return

        line = self._plot_transaction_points(value_timeline, ax, category) # type: ignore
        color = line.get_color()
        self._plot_amort_points(value_timeline, ax, category, color) # type: ignore
        self._plot_bucket_vals(value_timeline, ax, color) # type: ignore
        
    def plot_all(self, ax: plt.Axes):
        """Sugar syntax to call plot on all categories"""
        for cat in self.categories:
            self.plot(ax, cat)

#%% Define buckets
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

#%% Pre-processing

skip_cats = [
    '401k', # Not relevant
    *(Constants.income_categories), # Not really a bucket
    'Long-term', 'Rent', 'Medical Insurance', # Messes up the graph
]

def pre_process(categorized_transactions: list[Record.CategorizedRecord]) -> BucketTracker:
    from Root import Sorting

    # Sort by date
    sorted_transactions = Sorting.by_date(categorized_transactions)

    # Track daily changes
    delta_tracker = DeltaTracker(sorted_transactions)

    # Track bucket values
    bucket_tracker = BucketTracker(delta_tracker,
        initial_date=sorted_transactions[0].date, final_date=sorted_transactions[-1].date,
        bucket_info=bucket_info)
    
    return bucket_tracker
#%% Display
# Legend outside and scrollablehttps://stackoverflow.com/a/55869324

def display(bucket_tracker: BucketTracker):
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

    return fig, ax

#%% Main
if __name__ == "__main__":
    import Functionified as fn

    # Parse
    transactions = Parsing.run()

    # Categorize
    categorized_transactions = fn.categorize(transactions, skip_cats, keep_filter=False)

    # Pre-processing
    bucket_tracker = pre_process(categorized_transactions)

    fig, ax = display(bucket_tracker)
