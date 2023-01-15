#%% Imports
import TkinterPlus as gui

from Root import Constants
from Root import Sorting
import Record
import Parsing
import Categorize

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
            elif c == 7 and cell is None: cell = '' # Comment=None --> Comment=''
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

#%% Main
if __name__ == "__main__":
    import datetime

    import Functionified as fn

    # Parse
    transactions = Parsing.run()

    # Categorize
    categorized_transactions = fn.categorize(transactions, cat_filter=['Rent'], keep_filter=True)

    # Pre-processing
    categorized_transactions = Sorting.by_date(categorized_transactions, reverse=False)

    # Prediction
    actual_transactions = categorized_transactions ; del categorized_transactions
    future_transactions = []
    last_actual = actual_transactions[-1]
    last_actual: Record.CategorizedRecord
    assert last_actual.rawRecord is not None
    last_date = last_actual.date
    stop = datetime.date(2023, 6, 30)
    date = fn.inc_month(last_date)
    while date < stop:
        new = Record.CategorizedRecord.from_RawRecord(last_actual.rawRecord, last_actual.category)
        new.desc = "--- Predicted Transaction ---"
        future_transactions.append(new)

        date = fn.inc_month(date)

    root = gui.Root(17, 30)
    table = create_table(root, actual_transactions, future_transactions)
    root.mainloop()