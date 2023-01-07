import Record

#%% Parsing
import Parsing

transactions: list[Record.RawRecord] = []
for parser in [
    Parsing.USAAParser("Checking", "2022_chk.csv"),
    Parsing.USAAParser("Credit Card", "2022_cc.csv")
    ]:
    transactions.extend(parser.transactions)

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
months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')

cat_groups = {'income': Constants.income_categories, 'expenses': Constants.expense_categories, 'internal': Constants.internal_categories}
values: dict[str, dict[str, dict[int, float]]] # {grouping: cat: {month number: value}}}
values = {}
for group, categories in cat_groups.items():
    values[group] = {cat:{m+1:0 for m in range(len(months))} for cat in categories}

for t in categorized_transactions:
    cat = t.category
    group = None
    for g, categories in cat_groups.items():
        if cat in categories:
            assert group is None, f"Category '{cat}' appears in multiple groups"
            group = g
    assert group is not None, f"Category '{cat}' not found in any group"
    values[group][cat][t.date.month] += t.value

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
        _add_text(table.frame, month, widths['data'], coords, anchor='center')
    _add_text(table.frame, "Total", widths['total'], coords, anchor='center')
    _add_text(table.frame, "Average", widths['average'], coords, anchor='center')
    _next_row(coords)

    # Category rows
    for cat in categories:
        # Label
        _add_text(table.frame, cat, widths['label'], coords, anchor='e')
        # Values
        total = 0
        for m in range(12):
            val = values[cat][m+1]
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
    monthly_delta = {m+1:0.0 for m in range(12)}
    monthly_balance = {m+1:0.0 for m in range(12)}
    monthly_balance[0] = starting_balance
    # Header row
    _add_text(table.frame, "SUMMARY", widths['label'], coords, bd=2, anchor='center')
    for month in months:
        _add_text(table.frame, month, widths['data'], coords, anchor='center')
    _add_text(table.frame, "Total", widths['total'], coords, anchor='center')
    _add_text(table.frame, "Average", widths['average'], coords, anchor='center')
    _next_row(coords)

    # Income
    _add_text(table.frame, "Income", widths['label'], coords, anchor='center')
    total = 0
    for m in range(12):
        val = 0
        for month_vals in values['income'].values():
            val += month_vals[m+1]
        monthly_delta[m+1] += val
        total += val
        _add_text(table.frame, f"${val:0,.2f}", widths['data'], coords, anchor='e')
    _add_text(table.frame, f"${total:0,.2f}", widths['total'], coords, anchor='e')
    _add_text(table.frame, f"${total/12:0,.2f}", widths['average'], coords, anchor='e')
    _next_row(coords)

    # Expenses
    _add_text(table.frame, "Expenses", widths['label'], coords, anchor='center')
    total = 0
    for m in range(12):
        val = 0
        for month_vals in values['expenses'].values():
            val += month_vals[m+1]
        monthly_delta[m+1] += val
        total += val
        _add_text(table.frame, f"${val:0,.2f}", widths['data'], coords, anchor='e')
    _add_text(table.frame, f"${total:0,.2f}", widths['total'], coords, anchor='e')
    _add_text(table.frame, f"${total/12:0,.2f}", widths['average'], coords, anchor='e')
    _next_row(coords)

    # Internal
    _add_text(table.frame, "Internal", widths['label'], coords, anchor='center')
    total = 0
    for m in range(12):
        val = 0
        for month_vals in values['internal'].values():
            val += month_vals[m+1]
        monthly_delta[m+1] += val
        total += val
        _add_text(table.frame, f"${val:0,.2f}", widths['data'], coords, anchor='e')
    _add_text(table.frame, f"${total:0,.2f}", widths['total'], coords, anchor='e')
    _add_text(table.frame, f"${total/12:0,.2f}", widths['average'], coords, anchor='e')
    _next_row(coords)

    # Net
    _add_text(table.frame, "Net Change", widths['label'], coords, anchor='center')
    total = 0
    for m in range(12):
        val = monthly_delta[m+1]
        total += val
        _add_text(table.frame, f"${val:0,.2f}", widths['data'], coords, anchor='e')
    _add_text(table.frame, f"${total:0,.2f}", widths['total'], coords, anchor='e')
    _add_text(table.frame, f"${total/12:0,.2f}", widths['average'], coords, anchor='e')
    _next_row(coords)

    # Balance
    _add_text(table.frame, "Balance", widths['label'], coords, anchor='center')
    total = 0
    for m in range(12):
        val = monthly_balance[m] + monthly_delta[m+1]
        monthly_balance[m+1] = val
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