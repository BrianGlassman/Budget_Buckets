#%% Imports
from matplotlib import pyplot as plt
from matplotlib.transforms import Bbox
import datetime
from collections import UserDict
from typing import TypeVar

from BaseLib import Constants, Categories, Sorting
from Classes import Record # TODO? Only needed for type-hinting, so probably a way to get rid of this import
from Classes import Bucket
import Classes
from Handlers import Parsing

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

class AmortizedItem:
    # Note: daily value is always rounded to 2 decimal places

    def __init__(self, duration: int, value: float) -> None:
        assert isinstance(duration, int)
        assert duration > 0
        self.duration = duration

        assert isinstance(value, float)
        self.total_value = value
        self.daily_value = round(value / duration, 2)

    def apply(self):
        # Save original value to return
        ret = self.daily_value

        # Decrement duration
        self.duration -= 1

        # Update values, avoiding repeated-rounding problems
        self.total_value -= ret
        if self.duration == 0:
            self.daily_value = 0
        else:
            self.daily_value = round(self.total_value / self.duration, 2)

        return ret
    
    @property
    def complete(self):
        return self.duration == 0

class AmortizedItems():
    items: list[AmortizedItem]
    def __init__(self) -> None:
        self.items = []

    def add(self, t: Record.CategorizedRecord):
        self.items.append(AmortizedItem(t.duration, t.value))
    
    def apply(self):
        """Decrement all durations by 1 and return the total"""
        total = 0.0
        i = 0
        while i < len(self.items):
            # Apply the transaction
            item = self.items[i]
            total += item.apply()

            # Remove completed transactions
            # Only incrememnt index if no removal
            if item.complete:
                self.items.pop(i)
            else:
                i += 1
        return total

class BaseTracker():
    _cat_tracker: dict[Cat, ConsecCalendar]

    def __init__(self, dated_transactions: list[Record.CategorizedRecord]): pass

    def get_category(self, key: Cat) -> ConsecCalendar:
        """Gets the values across all days for a given category"""
        assert key in Categories.categories
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
    _cat_tracker: dict[Cat, ConsecCalendar[float]] # {category: {date: delta that day}}
    _cat_tdates: dict[Cat, list[Date]] # {category: [dates where single-day transactions occurred]}
    _cat_adates: dict[Cat, list[Date]] # {category: [dates where amortized transactions began]}
    def __init__(self, dated_transactions: list[Record.CategorizedRecord]):
        # Note: dated_transactions must be sorted
        categories = Categories.categories

        # Group transactions by category, then date
        cat_transactions = {}
        cat_transactions: dict[Cat, SparseCalendar[list[Record.CategorizedRecord]]]
        strt = dated_transactions[0].date
        stop = strt
        for t in dated_transactions:
            cat = t.category
            if cat not in cat_transactions:
                cat_transactions[cat] = SparseCalendar()
            calendar = cat_transactions[cat]
            date = t.date
            if date not in calendar:
                calendar[date] = []
            calendar[date].append(t)

            # Update bounds
            if date < strt:
                strt = date
            if date > stop:
                stop = date 
        
        # Initialize the top-level trackers
        self._cat_tracker = {}
        self._cat_tdates = {}
        self._cat_adates = {}

        # Fill in the trackers category-by-category
        for cat in categories:
            # Get the transactions in this category
            transactions = cat_transactions.get(cat, None)

            # Skip categories with no transactions
            if transactions is None: continue

            # Initialize the trackers for this category
            tracker = self._cat_tracker[cat] = ConsecCalendar()
            tracker: ConsecCalendar[float]
            tdates = self._cat_tdates[cat] = []
            tdates: list[Date]
            adates = self._cat_adates[cat] = []
            adates: list[Date]

            amort_items = AmortizedItems()

            # Apply each day
            date = strt
            while date <= stop:
                delta = 0

                # Get transactions today
                t_today = False
                a_today = False
                today_transactions = transactions.get(date, [])
                for t in today_transactions:
                    assert t.duration > 0
                    if t.duration == 1:
                        # Single-day transaction - apply now
                        t_today = True
                        delta += t.value
                    else:
                        # Amortized transaction - save for later
                        a_today = True
                        amort_items.add(t)

                # Record what kind of transactions happened today
                if t_today:
                    tdates.append(date)
                if a_today:
                    adates.append(date)
                
                # Apply any amortized transactions
                a_delta = amort_items.apply()
                delta += a_delta
                
                tracker[date] = delta
                
                # Increment the date
                date += Constants.one_day

            tracker.verify()
            assert list(tracker.dates())[ 0] == strt
            assert list(tracker.dates())[-1] == stop
    
    def get_tdates(self, key: Cat) -> list[Date]:
        """Gets the single-day transaction dates for a given category"""
        assert key in Categories.categories
        return self._cat_tdates[key]
    
    def get_adates(self, key: Cat) -> list[Date]:
        """Gets the amortized transaction start dates for a given category"""
        assert key in Categories.categories
        return self._cat_adates[key]

class BucketTracker(BaseTracker):
    _empty_bucket = Bucket("empty", 0, 0)
    def __init__(self, delta_tracker: DeltaTracker, initial_date: Date, final_date: Date, bucket_info: dict[Cat, Bucket] = {}):
        """refill_amts - {category: amount to add per DAY}"""
        self._delta_tracker = delta_tracker

        # Create the tracker with initial values
        self._cat_tracker = {}
        for cat in delta_tracker.categories:
            tracker = ConsecCalendar()
            bucket = bucket_info.get(cat, self._empty_bucket)
            tracker[initial_date] = bucket.initial_value
            self._cat_tracker[cat] = tracker
        
        # Iterate
        date = initial_date
        yesterday = initial_date
        while date <= final_date:
            dtracker = delta_tracker.get_date(date)
            for cat, tracker in self._cat_tracker.items():
                # Skip if already handled
                if cat in skip_cats: continue
                # Aliasing
                bucket = bucket_info.get(cat, self._empty_bucket)

                # Yesterday's value
                last_value = tracker.get(yesterday, None)
                assert last_value is not None

                # Today's transactions
                transaction_value = dtracker.get(cat, 0)

                # Handle refilling and max value
                # Do transaction first, then refill if below max
                new_value = last_value + transaction_value
                if new_value < bucket.max_value:
                    new_value += min(bucket.refill, bucket.max_value - new_value)
                
                # Save the new value
                tracker[date] = new_value

            # Increment for the next loop
            yesterday = date
            date += Constants.one_day
        
        for tracker in self._cat_tracker.values():
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

    def _plot_bucket_vals(self, values: ConsecCalendar, ax: plt.Axes, color: str, category: Cat):
        """Plot the bucket values"""
        # Make sure the line starts from bucket max_value
        keys = list(values.keys())
        vals = list(values.values())

        max_value = Classes.bucket_info[category].max_value
        if vals[0] != max_value:
            keys = [keys[0]] + keys
            vals = [max_value] + vals

        # Plot bucket value including refills (no label, so doesn't show up on auto-legend)
        line = ax.plot(keys, vals, '-', color=color, linewidth=0.5)
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
        self._plot_bucket_vals(value_timeline, ax, color, category)
        
    def plot_all(self, ax: plt.Axes):
        """Sugar syntax to call plot on all categories"""
        for cat in self.categories:
            self.plot(ax, cat)

#%% Pre-processing

skip_cats = [
    '401k', # Not relevant
    *(Categories.income_categories), # Not really a bucket
    'Long-term', 'Rent', 'Medical Insurance', # Messes up the graph
]

def pre_process(categorized_transactions: list[Record.CategorizedRecord]) -> BucketTracker:

    # Sort by date
    sorted_transactions = Sorting.by_date(categorized_transactions)

    # Track daily changes
    delta_tracker = DeltaTracker(sorted_transactions)

    # Track bucket values
    bucket_tracker = BucketTracker(delta_tracker,
        initial_date=sorted_transactions[0].date, final_date=sorted_transactions[-1].date,
        bucket_info=Classes.bucket_info)
    
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
