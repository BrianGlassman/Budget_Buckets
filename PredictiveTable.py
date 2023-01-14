#%% Imports
import TkinterPlus as gui

from Root import Constants
from Root import Sorting
import Record
import Parsing
import Categorize

#%% Table creation
def create_table(root):
    table = gui.ScrollableFrame(root)
    table.pack(side="top", fill="both", expand=True)

    # Populate the table
    widths = {'status': 10, 'account': 10, 'date': 10, 'desc': 40, 'value': 8, 'source-specific': None, 'category': 20, 'comment': 30}
    widths = list(widths.values())
    for r, row in enumerate(categorized_transactions):
        gui.tkinter.Label(table.frame, text='Actual', anchor='w', relief='solid', bd=1, width=widths[0]).grid(row=r, column=0)
        for c, cell in enumerate(row.values()):
            c = c + 1 # Account for the Status column that's not part of the transaction
            if c == 5: continue # Skip the source-specific data
            elif c == 7 and cell is None: cell = '' # Comment=None --> Comment=''
            gui.tkinter.Label(table.frame, text = str(cell), anchor = 'w', relief='solid', bd = 1, width=widths[c]).grid(row=r, column=c)
    return table

#%% Main
if __name__ == "__main__":
    import Functionified as fn

    # Parse
    transactions = Parsing.run()

    # Categorize
    categorized_transactions = fn.categorize(transactions, cat_filter=['Rent'], keep_filter=True)

    # Pre-processing
    categorized_transactions = Sorting.by_date(categorized_transactions)

    # Prediction
    # TODO

    root = gui.Root(17, 30)
    table = create_table(root)
    root.mainloop()