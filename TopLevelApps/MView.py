import datetime

from BaseLib import Categories
from Handlers import Parsing
import Functionified as fn
import TkinterPlus as gui

#%% Display pre-processing

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
    for key, val in [['anchor', 'w'], ['relief', 'solid'], ['bd', 1]]:
        kwargs.setdefault(key, val)
    label = gui.tkinter.Label(master=parent, text=text, width=width, **kwargs)
    label.grid(row=coords[0], column=coords[1])
    if inc_row: _next_row(coords)
    if inc_col: _next_col(coords)
    return label

def make_tracker_sheet(parent, values, title: str, categories: tuple[str, ...], months: list[datetime.date]) -> None:
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
    grand_total = 0
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
        _add_text(table.frame, f"${total/len(months):0,.2f}", widths['average'], coords, anchor='e')
        
        grand_total += total
        _next_row(coords)

    # Total row
    coords[1] = len(months) # Start in last data column
    # Label
    _add_text(table.frame, "Total", widths['data'], coords, anchor='center')
    # Total of all categories
    _add_text(table.frame, f"${grand_total:0,.2f}", widths['total'], coords, anchor='e')
    # Average monthly total
    _add_text(table.frame, f"${grand_total/len(months):0,.2f}", widths['average'], coords, anchor='e')

def make_summary_sheet(parent, values, starting_balance: float, months: list[datetime.date]) -> None:
    month_count = len(months)
    before_strt = fn.dec_month(months[0])

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

    def make_section(title: str, source):
        _add_text(table.frame, title, widths['label'], coords, anchor='center')
        total = 0
        for month in months:
            val = 0
            for month_vals in source:
                val += month_vals[month]
            monthly_delta[month] += val
            total += val
            _add_text(table.frame, f"${val:0,.2f}", widths['data'], coords, anchor='e')
        _add_text(table.frame, f"${total:0,.2f}", widths['total'], coords, anchor='e')
        _add_text(table.frame, f"${total/month_count:0,.2f}", widths['average'], coords, anchor='e')
        _next_row(coords)

    make_section("Income", values['income'].values())
    make_section("Expenses", values['expenses'].values())
    make_section("Internal", values['internal'].values())

    # Net
    _add_text(table.frame, "Net Change", widths['label'], coords, anchor='center')
    total = 0
    for month in months:
        val = monthly_delta[month]
        total += val
        _add_text(table.frame, f"${val:0,.2f}", widths['data'], coords, anchor='e')
    _add_text(table.frame, f"${total:0,.2f}", widths['total'], coords, anchor='e')
    _add_text(table.frame, f"${total/month_count:0,.2f}", widths['average'], coords, anchor='e')
    _next_row(coords)

    # Balance
    _add_text(table.frame, "Balance", widths['label'], coords, anchor='center')
    total = 0
    for month in months:
        val = monthly_balance[fn.dec_month(month)] + monthly_delta[month]
        monthly_balance[month] = val
        total += val
        _add_text(table.frame, f"${val:0,.2f}", widths['data'], coords, anchor='e')
    _add_text(table.frame, "", widths['total'], coords)
    _add_text(table.frame, f"${total/month_count:0,.2f}", widths['average'], coords, anchor='e')
    _next_row(coords)

#%% Main
def run():
    # Parse
    transactions = Parsing.run()

    # Categorize
    categorized_transactions = fn.categorize(transactions, cat_filter=[], keep_filter=False)

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

    cat_groups = {'income': Categories.income_categories, 'expenses': Categories.expense_categories, 'internal': Categories.internal_categories}
    values: dict[str, dict[str, dict[datetime.date, float]]] # {grouping: {cat: {date_key: value}}}
    values = {}
    for group, categories in cat_groups.items():
        values[group] = {cat:{month:0 for month in months} for cat in categories}

    for t in categorized_transactions:
        cat = t.category
        group = None

        # Skip meta-flagged transactions
        if cat in (Categories.todo_category, Categories.del_category):
            continue

        for g, categories in cat_groups.items():
            if cat in categories:
                assert group is None, f"Category '{cat}' appears in multiple groups"
                group = g
        assert group is not None, f"Category '{cat}' not found in any group"
        values[group][cat][make_date_key(t.date)] += t.value

    root = gui.Root(25, 10)

    # make_tracker_sheet(root, values['income'], "Income", Categories.income_categories, months)
    # make_tracker_sheet(root, values['expenses'], "Expenses", Categories.expense_categories, months)

    make_summary_sheet(root, values, 0, months)

    root.mainloop()

if __name__ == "__main__":
    run()