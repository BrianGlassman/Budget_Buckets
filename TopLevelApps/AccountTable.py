"""
Idea is to see how money moves between accounts
Can also be used for checksumming against current balance
"""

import datetime

from BaseLib import Accounts
from Handlers import Parsing
import Functionified as fn
import TkinterPlus as gui

#%% Pre-processing
def make_date_key(date: datetime.date) -> datetime.date:
    """Gets just the year and month for use as a key"""
    return datetime.date(date.year, date.month, 1)

def make_date_label(date: datetime.date) -> str:
    return date.strftime("%b %y") # https://www.programiz.com/python-programming/datetime/strftime

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
    return _add_text_merged(parent=parent, text=text, width=width, coords=coords, inc_row=inc_row, inc_col=inc_col, columnspan=1, **kwargs)

def _add_text_merged(parent, text: str, width: int, coords: list, inc_row = False, inc_col = True, columnspan = 1, rowspan = 1, **kwargs):
    """Like _add_text, but for a merged cell"""
    for key, val in [['anchor', 'w'], ['relief', 'solid'], ['bd', 1]]:
        kwargs.setdefault(key, val)
    label = gui.tkinter.Label(master=parent, text=text, width=width, **kwargs)
    label.grid(row=coords[0], column=coords[1], columnspan=columnspan, rowspan=rowspan)
    if inc_row: 
        for _ in range(rowspan):
            _next_row(coords)
    elif inc_col:
        for _ in range(columnspan):
            _next_col(coords)
    return label

def make_summary_sheet(parent, deltas, starting_balance: dict[str, float], months: list[datetime.date]) -> None:
    table = gui.ScrollableFrame(parent)
    table.pack(side="top", fill="both", expand=True)

    coords = [0,0]
    widths = {'label': 20, 'delta': 10, 'final': 10}

    # Header row
    _add_text(table.frame, "ACCOUNT", widths['label'], coords, bd=2, anchor='center')
    # Month labels (2-column)
    for month in months:
        _add_text_merged(table.frame, make_date_label(month), widths['delta']+widths['final'], coords, anchor='center', columnspan=2)
    _next_row(coords)
    _next_col(coords) # Skip first column
    # Delta and Final labels
    for month in months:
        _add_text(table.frame, "Delta", widths['delta'], coords, anchor='center')
        _add_text(table.frame, "Final", widths['final'], coords, anchor='center')
    _next_row(coords)

    # Fill in the data
    _deltas = deltas
    for account, deltas in _deltas.items():
        balance = starting_balance[account]
        _add_text(table.frame, account, widths['label'], coords, anchor='center')
        for month in months:
            delta = deltas[month]
            _add_text(table.frame, f"${delta:0,.2f}", widths['delta'], coords, anchor='e')
            balance += delta
            _add_text(table.frame, f"${balance:0,.2f}", widths['final'], coords, anchor='e')
        _next_row(coords)

#%% Main
def run():
    # Parse
    transactions = Parsing.run()

    # Categorize
    categorized_transactions = fn.categorize(transactions, use_internal=True)

    # Get first/last month (instead of first/last date)
    strt, stop = fn.get_str_stop(categorized_transactions)
    strt = datetime.date(year=strt.year, month=strt.month, day=1)
    stop = datetime.date(year=stop.year, month=stop.month, day=1)

    # Create a consecutive list of months from strt to stop
    months: list[datetime.date] = []
    date = strt
    while date <= stop:
        months.append(date)
        date = fn.inc_month(date)
    
    # Get all the accounts
    accounts = Accounts.accounts

    # Initialize all month's deltas as 0
    deltas: dict[str, dict[datetime.date, float]] # {account: {date_key: delta this month}}
    deltas = {}
    for account in accounts:
        deltas[account] = {month:0 for month in months}

    # Fill in the data
    for t in categorized_transactions:
        deltas[t.account][make_date_key(t.date)] += t.value

    root = gui.Root(25, 10)

    starting_balance = {act:0 for act in accounts}
    starting_balance: dict[str, float] # {account: balance}
    starting_balance.update({
        # Investment accounts aren't actually correct, but I don't want to account for market changes
        '401(k)': 33261.21,
        'M1': 1183.73,
        'Checking': 37237.66, # 2021/08/30 statement
        'FStocks': 17879.89,
        'Credit Card': -(220.92 # Balance as of 2021/09/17 (end of statement)
            - (1150.17 + 283.90 + 54.41) # Payments and Credits in September
            + (8.14+32.62+79.44+109.89+126.82+54.41+14.71+60.12+30+55.96+40+7.95+10.27+160.94+17.38+32.33)), # Charges in September
    })

    # TODO pretty sure Credit Card is wrong, but I need to think of a better way of dealing with the mid-month statement cycle

    make_summary_sheet(root, deltas, starting_balance, months)

    root.mainloop()

if __name__ == "__main__":
    run()