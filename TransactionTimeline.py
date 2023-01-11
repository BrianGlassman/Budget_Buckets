import Record

#%% Parsing
import Parsing

transactions: list[Record.RawRecord]
transactions = Parsing.run()

#%% Categorizing
import Categorize
from Root import Constants

limit = -1 # Use -1 for all
use_uncat = True # Whether to show uncategorized items
use_cat = False # Whether to show categorized items

categorized_transactions = Categorize.run(
    transactions=transactions, limit=limit, use_uncat=use_uncat, use_cat=use_cat, use_internal=True)

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
        self.cat_tracker = {cat:{} for cat in Constants.categories_inclTodo}

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
        assert key in Constants.categories_inclTodo
        return self.cat_tracker[key]

    def get_date(self, key: datetime.date) -> dict[str, float | None]:
        """Gets the values across all categories for a given day"""
        assert type(key) is datetime.date
        ret = {}
        for cat, values in self.cat_tracker.items():
            ret[cat] = values[key]
        return ret

    def get(self, key: str | datetime.date) -> dict[datetime.date, float | None] | dict[str, float | None]:
        if isinstance(key, str):
            return self.get_category(key)
        elif type(key) is datetime.date:
            return self.get_date(key)
        else:
            raise ValueError(f"Unknown key: '{key}' of type '{type(key)}'")
tracker = Tracker(sorted_transactions)

#%% Display
from matplotlib import pyplot as plt
from matplotlib.transforms import Bbox

# Legend outside and scrollablehttps://stackoverflow.com/a/55869324

fig, ax = plt.subplots()
fig.subplots_adjust(right=0.75)
for cat in Constants.categories_inclTodo:
    values = tracker.get_category(cat)
    if all(v is None for v in values.values()): continue # Don't plot unused categories
    ax.plot(values.keys(), values.values(), '.', label=cat)
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
