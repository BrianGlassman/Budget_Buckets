#%% Imports
import datetime

import TkinterPlus as gui
from BaseLib import Categories, Sorting
from Classes import Buckets, Record
import Parsing

raise NotImplementedError("This file is out of date")

#%% Table creation
def create_table(root, actual, future):
    table = gui.ScrollableFrame(root)
    table.pack(side="top", fill="both", expand=True)

    widths = {'status': 10, 'account': 10, 'date': 10, 'desc': 40, 'value': 8, 'source-specific': None, 'category': 20, 'comment': 30}
    widths = list(widths.values())
    def create_row(r, row):
        for c, cell in enumerate(row.values()):
            c = c + 1 # Account for the Status column that's not part of the transaction
            if c == 5: continue # Skip the source-specific data
            gui.tkinter.Label(table.frame, text = str(cell), anchor = 'w', relief='solid', bd = 1, width=widths[c]).grid(row=r, column=c)

    # Populate the table
    r = 0
    for r, row in enumerate(actual):
        gui.tkinter.Label(table.frame, text='Actual', anchor='w', relief='solid', bd=1, width=widths[0]).grid(row=r, column=0)
        create_row(r, row)
    last = r
    for _r, row in enumerate(future):
        r = last + _r
        gui.tkinter.Label(table.frame, text='Future', anchor='w', relief='solid', bd=1, width=widths[0]).grid(row=r, column=0)
        create_row(r, row)
    return table

#%% Prediction logic

# Take the daily average and apply going forwards
avg_cats = (
    # Car
    # 'Car - Note', # predict_regular
    'Car/Rental Insurance',
    'Car - Other',
    'Car - Parking Pass', # TODO change to just "Parking" or split pass from incidental. Can't do until after porting over old sheet

    # Education
    # 'Self-improvement',

    # Entertainment
    # 'Dates', # Only one day :(
    'Entertainment - Other',
    'Games',
    'Going Out',
    'Books',
    # 'Big Fun',

    # Food
    'Groceries',
    'Food - nice',

    # Housing
    # 'Rent', # predict_regular
    'Utilities',
    # 'Internet', # predict_regular
    'Housing - Other',
    'Decoration',

    # Investments/Savings
    # '401k',
    # 'Retirement',
    # 'Long-term',
    # 'Unexpected Fund',

    # Medical/Dental
    'Medical - Other',
    'Medical Insurance',

    # Other
    'ATM',
    'Other - Other',

    # Personal Care / Clothing
    # 'Clothes/Personal care', # Only one day
)
regular_cats = (
    'Car - Note',
    'Rent',
    'Internet',
)
def do_stuff(transactions):
    """Assumes transactions are sorted by date"""
    avg_vals = {}
    for cat in avg_cats:
        try:
            temp = [x for x in transactions if x.category == cat]
            if len(temp) == 0: continue
            days = (temp[-1].date - temp[0].date).days
            value = sum(x.value for x in temp)
            if value == 0: continue
            avg_vals[cat] = value / days
        except Exception:
            print(cat)
            raise
    return avg_vals

def predict_regular(transactions, category):
    """Predict fixed monthly expenses (ex. rent, car note, etc.)
    Assumes transactions are sorted by date"""
    transactions = [x for x in transactions if x.category == category]
    last_actual = transactions[-1]
    last_actual: Record.CategorizedRecord
    assert last_actual.rawRecord is not None
    stop = datetime.date(2023, 6, 30)

    # Start one month after the last actual, then each month after that
    future_transactions = []
    date = fn.inc_month(last_actual.date)
    while date < stop:
        new = Record.CategorizedRecord.from_RawRecord(last_actual.rawRecord, last_actual.category)
        new.desc = "--- Extrapolate from last instance ---"
        new.date = date
        future_transactions.append(new)

        date = fn.inc_month(date)
    
    return future_transactions

#%% Main
if __name__ == "__main__":
    import datetime

    import Functionified as fn

    # Parse
    transactions = Parsing.run()

    # Categorize
    categorized_transactions = fn.categorize(transactions, cat_filter=Categories.expense_categories, keep_filter=True)

    # Pre-processing
    categorized_transactions = Sorting.by_date(categorized_transactions)
    avg_values = do_stuff(categorized_transactions)

    # Prediction
    stop = datetime.date(2023, 6, 30) # Predict until a little after graduation
    actual_transactions = categorized_transactions ; del categorized_transactions
    future_transactions = []

    for cat in regular_cats:
        future_transactions.extend(predict_regular(actual_transactions, cat))

    last_actual = actual_transactions[-1]
    last_date: datetime.date = last_actual.date
    date = fn.inc_month(last_date)
    while date < stop:
        delta = (date - last_date).days
        for cat, daily_val in avg_values.items():
            new = Record.CategorizedRecord('', date, '--- Extrapolate daily average ---', round(daily_val*delta, 2),
                category=cat)
            future_transactions.append(new)

        last_date = date
        date = fn.inc_month(date)

    # Sort before displaying
    future_transactions = Sorting.by_date(future_transactions)

    root = gui.Root(17, 30)
    # Using all the actual transactions takes too long, just show the predicted future ones
    # table = create_table(root, actual_transactions, future_transactions)
    table = create_table(root, [], future_transactions)
    root.mainloop()