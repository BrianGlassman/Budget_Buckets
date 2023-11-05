#%% Imports
import plotly
import plotly.graph_objects as go
import datetime
from collections import UserDict
from typing import TypeVar
import dash

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
        """Returns all categories"""
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

        self._cat_tracker = {}
        for cat in delta_tracker.categories:
            tracker = self._cat_tracker[cat] = ConsecCalendar() ; tracker: ConsecCalendar
            dtracker = delta_tracker.get_category(cat)
            bucket = bucket_info.get(cat, self._empty_bucket)
            refill = bucket.refill

            # Skip categories that never change (use max_value as initial/constant value)
            if refill == 0 and all(v == 0 for v in dtracker.values()):
                tracker[initial_date] = bucket.max_value
                continue

            # Calculate the value for each day (previous day + transactions + refilling)
            last_value = bucket.max_value # Initial value or value of previous day (start at max_value)
            date = initial_date
            while date <= final_date:
                # Handle transactions
                tvalue = dtracker.get(date, 0)

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

    def _plot_transaction_points(self, values: dict[Date, float], fig: go.Figure, category: Cat, color: str):
        """Plot the points where single-day transactions occurred"""
        values = {date:v for date,v in values.items() if date in self._delta_tracker.get_tdates(category)}
        # Plot transaction points
        fig.add_scatter(x=list(values.keys()), y=list(values.values()), mode='markers', marker_color=color,
                        name=category, showlegend=True, legendgroup=category)
    
    def _plot_amort_points(self, values: dict[Date, float], fig: go.Figure, category: Cat, color: str):
        """Plot the points where amortized transactions began"""
        values = {date:v for date,v in values.items() if date in self._delta_tracker.get_adates(category)}
        # Plot amortized transaction points
        fig.add_scatter(x=list(values.keys()), y=list(values.values()),
                        mode='markers', marker=go.scatter.Marker(symbol='circle-open', color=color, size=5),
                        name=category, showlegend=False, legendgroup=category)

    def _plot_bucket_vals(self, values: ConsecCalendar, fig: go.Figure, category: Cat, color: str):
        """Plot the bucket values"""
        # Make sure the line starts from bucket max_value
        keys = list(values.keys())
        vals = list(values.values())

        max_value = Classes.bucket_info[category].max_value
        if vals[0] != max_value:
            keys = [keys[0]] + keys
            vals = [max_value] + vals

        # Plot bucket value including refills
        fig.add_scatter(x=keys, y=vals, mode='lines', line=go.scatter.Line(width=1, color=color),
                        name=category, showlegend=False, legendgroup=category)

    def plot(self, fig: go.Figure, category: Cat, color) -> None:
        """Plot the values for the given category on the given graph"""
        value_timeline = self.get_category(category)
        if len(self._delta_tracker.get_tdates(category)) == 0 and len(self._delta_tracker.get_adates(category)) == 0:
            # Skip categories with no transactions
            return

        self._plot_transaction_points(value_timeline, fig, category, color=color) # type: ignore
        self._plot_amort_points(value_timeline, fig, category, color=color) # type: ignore
        self._plot_bucket_vals(value_timeline, fig, category, color=color)
        
    def plot_all(self, fig: go.Figure):
        """Sugar syntax to call plot on all categories"""
        n_cats = len(self.categories)
        colors = plotly.colors.sample_colorscale('turbo', [n/(n_cats - 1) for n in range(n_cats)])
        for cat, color in zip(self.categories, colors):
            self.plot(fig, cat, color)
    
    def table_row(self, category: Cat):
        """Make a row for the given category"""
        value_timeline = self.get_category(category)
        if len(self._delta_tracker.get_tdates(category)) == 0 and len(self._delta_tracker.get_adates(category)) == 0:
            # Skip categories with no transactions
            return

        keys = list(value_timeline.keys())
        vals = list(value_timeline.values())

        # Start the line at bucket max_value
        max_value = Classes.bucket_info[category].max_value
        if vals[0] != max_value:
            # Insert a max_value entry
            keys = [keys[0]] + keys
            vals = [max_value] + vals
        
        # Only show initial value, month-start, and final value
        # Note: uses month-start instead of month-end just because it's always 1
        # TODO allow a configurable list of dates to show
        data = {}
        # Initial value
        data[keys[0]] = vals[0]
        # All month-starts
        data.update({key:val for key, val in zip(keys[1:-1], vals[1:-1]) if key.day==1})
        # Final value
        data[keys[-1]] = vals[-1]
        
        # Keys must be str, int, float, bool or None for Dash
        data = {str(key):f'${val:0,.2f}' for key, val in data.items()}

        # Add the category to the front and return
        row = {'Category': category}
        row.update(data)
        return row

    def table(self):
        data = [self.table_row(cat) for cat in self.categories]

        row = data[0]
        assert row is not None
        header = row.keys()

        columns = [{'name': name, 'id': name, 'editable': False, 'selectable': False} for name in header]
        table = dash.dash_table.DataTable(
            columns=columns,
            data=data,
            page_action='none', # Show everything on one page
            # fixed_columns={'headers': True, 'data': 1},
            fixed_rows={'headers': True},
        )

        return table

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

def display(bucket_tracker: BucketTracker, show=True):
    fig = go.Figure(layout=go.Layout(title="Bucket Timeline", plot_bgcolor='white'))
    fig.update_yaxes(title_text="Value ($)",
        showline=True, linecolor='black', mirror=True,
        gridcolor='LightGray', zerolinecolor='LightGray')
    fig.update_xaxes(title_text="Date",
        showline=True, linecolor='black', mirror=True,
        gridcolor='LightGray', zerolinecolor='LightGray')
    bucket_tracker.plot_all(fig)

    if show: fig.show()

    return fig

#%% Main
def show_plot(tracker: BucketTracker):
    fig = display(tracker)
    return fig

def show_table(tracker: BucketTracker):
    app = dash.Dash(__name__)

    table = tracker.table()

    app.layout = dash.html.Div(table)

    app.run(debug=False)

if __name__ == "__main__":
    import Functionified as fn

    # Parse
    transactions = Parsing.run()

    # Categorize
    categorized_transactions = fn.categorize(transactions, skip_cats, keep_filter=False)

    # Pre-processing
    bucket_tracker = pre_process(categorized_transactions)

    # show_plot(bucket_tracker)
    show_table(bucket_tracker)
