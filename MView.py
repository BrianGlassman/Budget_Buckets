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
    if inc_row: coords[0] += 1
    if inc_col: coords[1] += 1
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

    # Category rows
    coords = [coords[0]+1, 0]
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
        
        # Go to start of next row
        coords = [coords[0]+1, 0]

root = gui.Root(10, 10)

# make_tracker_sheet(root, values['income'], "Income", Constants.income_categories)
make_tracker_sheet(root, values['expenses'], "Expenses", Constants.expense_categories)

root.mainloop()