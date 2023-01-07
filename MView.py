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
months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')

values: dict[str, dict[int, float]] # {cat: {month number: value}}
values = {cat:{m+1:0 for m in range(len(months))} for cat in Constants.categories_inclTodo}

for t in categorized_transactions:
    values[t.category][t.date.month] += t.value

#%% Display

import TkinterPlus as gui

root = gui.Root(10, 10)

table = gui.ScrollableFrame(root)
table.pack(side="top", fill="both", expand=True)

#%% Income sheet
def add_text(text: str, width: int, coords: list, inc_row = False, inc_col = True, **kwargs):
    """Creates a new Label object at the given coordinates
    text - the text to fill in
    width - the Label's width parameter
    coords - a list of [row, column]
        Note: modified in-place if inc_row and/or inc_col are True"""
    for key, val in [['anchor', 'w'], ['relief', 'solid'], ['bd', 1]]:
        kwargs.setdefault(key, val)
    label = gui.tkinter.Label(table.frame, text=text, width=width, **kwargs)
    label.grid(row=coords[0], column=coords[1])
    if inc_row: coords[0] += 1
    if inc_col: coords[1] += 1
    return label

coords = [0, 0]
widths = {'label': 20, 'data': 10, 'total': 10, 'average': 10}

# Header row
add_text("INCOME", widths['label'], coords, bd=2)
for i, month in enumerate(months):
    add_text(month, widths['data'], coords)
add_text("Total", widths['total'], coords)
add_text("Average", widths['average'], coords)

# Category rows
coords = [coords[0]+1, 0]
for cat in Constants.categories_inclTodo:
    # Label
    add_text(cat, widths['label'], coords)
    # Values
    total = 0
    for m in range(12):
        val = values[cat][m+1]
        add_text(f"${val:0.2f}", widths['data'], coords)
        total += val
    add_text(f"${total:0.2f}", widths['total'], coords)
    add_text(f"${total/12:0.2f}", widths['average'], coords)
    
    # Go to start of next row
    coords = [coords[0]+1, 0]

root.mainloop()