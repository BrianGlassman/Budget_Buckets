#%% Parsing
import Parsing

parser = Parsing.USAAParser("USAA CC", "cc.csv")

#%% Categorizing
import Record
import Categorize

categorized_transactions = []
for baseRecord in parser.transactions:
    match = Categorize.match_templates(baseRecord)
    if match is None:
        print(f"No template matched for {baseRecord}")
        continue
    ct = Record.CategorizedRecord(baseRecord, match['new']['category'])
    categorized_transactions.append(ct)

#%% Display
import TkinterPlus as gui

root = gui.Root(10, 10)

table = gui.ScrollableFrame(root)
table.pack(side = "top", fill="both", expand=True)

def onModification(event):
    text = event.widget.get("1.0", "end-1c")
    print(f"text changed to {text}")

# Populate the table
widths = {'account': 10, 'date': 10, 'desc': 40, 'value': 8, 'source-specific': None, 'category': 10}
widths = list(widths.values())
for r, row in enumerate(categorized_transactions):
    for c, cell in enumerate(row.values()):
        if c == 0: continue # Skip the Account
        if c == 4: continue # Skip the source-specific data
        if c == 5:
            # Category
            txt = gui.WatchedText(table.frame, text = str(cell), width = widths[c], height = 1)
            txt.grid(row=r, column=c)
            txt.watch(onModification)
        else:
            if c < len(widths) and (widths[c] is not None):
                gui.tkinter.Label(table.frame, text = str(cell), anchor = 'w', relief='solid', bd = 1, width=widths[c]).grid(row=r, column=c)
            else:
                gui.tkinter.Label(table.frame, text = str(cell), anchor = 'w', relief='solid', bd = 1).grid(row=r, column=c)

root.mainloop()
