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
        category = 'TODO'
    else:
        category = match['new']['category']
    ct = Record.CategorizedRecord(baseRecord, category)
    categorized_transactions.append(ct)

    if len(categorized_transactions) == 10:
        break

#%% Display
import TkinterPlus as gui

root = gui.Root(10, 10)

table = gui.ScrollableFrame(root)
table.pack(side = "top", fill="both", expand=True)

# [(pattern, new)]
added_templates = []
def onModification(event: gui.tkinter.Event):
    text = event.widget.get("1.0", "end-1c")

    t = event.widget.transaction
    pattern = t.items()
    pattern.pop('category')
    new = {'category': text}

    create = True
    for i, pn in enumerate(added_templates):
        p, n = pn
        # Overwrite existing, if there is one
        if p == pattern:
            added_templates[i] = (pattern, new)
            create = False
            break
    if create:
        added_templates.append((pattern, new))

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
            txt.transaction = row
        else:
            if c < len(widths) and (widths[c] is not None):
                gui.tkinter.Label(table.frame, text = str(cell), anchor = 'w', relief='solid', bd = 1, width=widths[c]).grid(row=r, column=c)
            else:
                gui.tkinter.Label(table.frame, text = str(cell), anchor = 'w', relief='solid', bd = 1).grid(row=r, column=c)

root.mainloop()

for pattern, new in added_templates:
    Categorize.add_template("Auto-generated", "", pattern, new)
if added_templates:
    print("Saving added templates:")
    print(added_templates)
    Categorize.save_templates()
