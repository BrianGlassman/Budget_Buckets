import datetime

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
    transactions=transactions, limit=limit, use_uncat=use_uncat, use_cat=use_cat)

#%% Display pre-processing
import TkinterPlus as gui

def make_date_key(date: datetime.date) -> datetime.date:
    """Gets just the year and month for use as a key"""
    return datetime.date(date.year, date.month, 1)

def make_date_label(date: datetime.date) -> str:
    return date.strftime("%b %y") # https://www.programiz.com/python-programming/datetime/strftime

def add_month(date: datetime.date, inc: int) -> datetime.date:
    """Increments the month, incrementing year if needed
    Returns the new date"""
    assert isinstance(date, datetime.date)
    if date.day > 28: raise NotImplementedError("Not sure what happens if day isn't in month")
    assert isinstance(inc, int)
    assert inc in [1, -1]
    month = date.month + inc
    if month > 12:
        month = 1
        year = date.year + 1
    elif month < 1:
        month = 12
        year = date.year - 1
    else:
        year = date.year
    return date.replace(year=year, month=month)
def inc_month(date: datetime.date): return add_month(date, +1)
def dec_month(date: datetime.date): return add_month(date, -1)

# Get the earliest and latest date
strt: datetime.date
stop: datetime.date
strt = stop = categorized_transactions[0].date
for t in categorized_transactions:
    date = t.date
    if date < strt: strt = date
    if date > stop: stop = date

# Create a consecutive list of months from strt to stop
months: list[datetime.date] = []
strt = datetime.date(year=strt.year, month=strt.month, day=1)
before_strt = dec_month(strt)
stop = datetime.date(year=stop.year, month=stop.month, day=1)
date = strt
while date <= stop:
    months.append(date)
    date = inc_month(date)
month_count = len(months)

cat_groups = {'income': Constants.income_categories, 'expenses': Constants.expense_categories, 'internal': Constants.internal_categories}
values: dict[str, dict[str, dict[datetime.date, float]]] # {grouping: cat: {date_key: value}}}
values = {}
for group, categories in cat_groups.items():
    values[group] = {cat:{month:0 for month in months} for cat in categories}

for t in categorized_transactions:
    cat = t.category
    group = None
    for g, categories in cat_groups.items():
        if cat in categories:
            assert group is None, f"Category '{cat}' appears in multiple groups"
            group = g
    assert group is not None, f"Category '{cat}' not found in any group"
    values[group][cat][make_date_key(t.date)] += t.value

def _next_row(coords):
    coords[0] += 1
    coords[1] = 0

def _next_col(coords):
    coords[1] += 1

def _add_text(parent, text: str, width: int, coords: list, inc_row = False, inc_col = True, **kwargs):
    """Creates a new Label object at the given coordinates
    text - the text to fill in
    width - the Label's width parameter
    coords - a list of [row, column]
        Note: modified in-place if inc_row and/or inc_col are True"""
    for key, val in [['anchor', 'w'], ['relief', 'solid'], ['bd', 1]]:
        kwargs.setdefault(key, val)
    label = gui.tkinter.Label(master=parent, text=text, width=width, **kwargs)
    label.grid(row=coords[0], column=coords[1])
    if inc_row: _next_row(coords)
    if inc_col: _next_col(coords)
    return label

def make_tracker_sheet(parent, values, title: str, categories: tuple[str, ...]) -> None:
    """
    values - {category: {month number (Jan = 1): value}}
    """
    table = gui.ScrollableFrame(parent)
    table.pack(side="top", fill="both", expand=True)

    coords = [0, 0]
    widths = {'label': 20, 'data': 10, 'total': 10, 'average': 10}

    # Header row
    _add_text(table.frame, title.upper(), widths['label'], coords, bd=2, anchor='center')
    for month in months:
        _add_text(table.frame, make_date_label(month), widths['data'], coords, anchor='center')
    _add_text(table.frame, "Total", widths['total'], coords, anchor='center')
    _add_text(table.frame, "Average", widths['average'], coords, anchor='center')
    _next_row(coords)

    # Category rows
    for cat in categories:
        # Label
        _add_text(table.frame, cat, widths['label'], coords, anchor='e')
        # Values
        total = 0
        for month in months:
            val = values[cat][month]
            _add_text(table.frame, f"${val:0,.2f}", widths['data'], coords, anchor='e')
            total += val
        _add_text(table.frame, f"${total:0,.2f}", widths['total'], coords, anchor='e')
        _add_text(table.frame, f"${total/12:0,.2f}", widths['average'], coords, anchor='e')
        
        _next_row(coords)

def make_summary_sheet(parent, values, starting_balance: float) -> None:
    #----------------
    # Pre-processing
    #----------------

    #---------
    # Display
    #---------
    table = gui.ScrollableFrame(parent)
    table.pack(side="top", fill="both", expand=True)

    coords = [0,0]
    widths = {'label': 20, 'data': 10, 'total': 10, 'average': 10}

    # --- Summary section ---
    monthly_delta   = {month:0.0 for month in months}
    monthly_balance = {month:0.0 for month in months}
    monthly_balance[before_strt] = starting_balance
    # Header row
    _add_text(table.frame, "SUMMARY", widths['label'], coords, bd=2, anchor='center')
    for month in months:
        _add_text(table.frame, make_date_label(month), widths['data'], coords, anchor='center')
    _add_text(table.frame, "Total", widths['total'], coords, anchor='center')
    _add_text(table.frame, "Average", widths['average'], coords, anchor='center')
    _next_row(coords)

    # Income
    _add_text(table.frame, "Income", widths['label'], coords, anchor='center')
    total = 0
    for month in months:
        val = 0
        for month_vals in values['income'].values():
            val += month_vals[month]
        monthly_delta[month] += val
        total += val
        _add_text(table.frame, f"${val:0,.2f}", widths['data'], coords, anchor='e')
    _add_text(table.frame, f"${total:0,.2f}", widths['total'], coords, anchor='e')
    _add_text(table.frame, f"${total/12:0,.2f}", widths['average'], coords, anchor='e')
    _next_row(coords)

    # Expenses
    _add_text(table.frame, "Expenses", widths['label'], coords, anchor='center')
    total = 0
    for month in months:
        val = 0
        for month_vals in values['expenses'].values():
            val += month_vals[month]
        monthly_delta[month] += val
        total += val
        _add_text(table.frame, f"${val:0,.2f}", widths['data'], coords, anchor='e')
    _add_text(table.frame, f"${total:0,.2f}", widths['total'], coords, anchor='e')
    _add_text(table.frame, f"${total/12:0,.2f}", widths['average'], coords, anchor='e')
    _next_row(coords)

    # Internal
    _add_text(table.frame, "Internal", widths['label'], coords, anchor='center')
    total = 0
    for month in months:
        val = 0
        for month_vals in values['internal'].values():
            val += month_vals[month]
        monthly_delta[month] += val
        total += val
        _add_text(table.frame, f"${val:0,.2f}", widths['data'], coords, anchor='e')
    _add_text(table.frame, f"${total:0,.2f}", widths['total'], coords, anchor='e')
    _add_text(table.frame, f"${total/12:0,.2f}", widths['average'], coords, anchor='e')
    _next_row(coords)

    # Net
    _add_text(table.frame, "Net Change", widths['label'], coords, anchor='center')
    total = 0
    for month in months:
        val = monthly_delta[month]
        total += val
        _add_text(table.frame, f"${val:0,.2f}", widths['data'], coords, anchor='e')
    _add_text(table.frame, f"${total:0,.2f}", widths['total'], coords, anchor='e')
    _add_text(table.frame, f"${total/12:0,.2f}", widths['average'], coords, anchor='e')
    _next_row(coords)

    # Balance
    _add_text(table.frame, "Balance", widths['label'], coords, anchor='center')
    total = 0
    for month in months:
        val = monthly_balance[dec_month(month)] + monthly_delta[month]
        monthly_balance[month] = val
        total += val
        _add_text(table.frame, f"${val:0,.2f}", widths['data'], coords, anchor='e')
    _add_text(table.frame, "", widths['total'], coords)
    _add_text(table.frame, f"${total/12:0,.2f}", widths['average'], coords, anchor='e')
    _next_row(coords)

root = gui.Root(25, 10)

# make_tracker_sheet(root, values['income'], "Income", Constants.income_categories)
# make_tracker_sheet(root, values['expenses'], "Expenses", Constants.expense_categories)

make_summary_sheet(root, values, 5000)

root.mainloop()