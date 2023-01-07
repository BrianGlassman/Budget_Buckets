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
use_uncat = True # Whether to show uncategorized items
use_cat = False # Whether to show categorized items

categorized_transactions: list[Record.CategorizedRecord] = []
for baseRecord in transactions:
    match = Categorize.match_templates(baseRecord)
    if match is None:
        if use_uncat:
            category = '*** TODO ***'
        else:
            continue
    else:
        category = match['new']['category']
        assert category in Constants.categories, f"Bad category: {category}"
        if not use_cat:
            continue
    ct = Record.CategorizedRecord(baseRecord, category)
    categorized_transactions.append(ct)

    if len(categorized_transactions) == limit:
        break

#%% Display
import TkinterPlus as gui

root = gui.Root(10, 10)

table = gui.ScrollableFrame(root)
table.pack(side = "top", fill="both", expand=True)

# Mouse wheel changes the combobox selection, which I don't want
def empty_scroll(event): return "break"
def disable_scroll(obj):
    obj.bind("<MouseWheel>", empty_scroll)
    obj.bind("<ButtonPress-4>", empty_scroll)
    obj.bind("<ButtonPress-5>", empty_scroll)

# Group together by Category, then description
# Sort to have the largest groups first
def sort_transactions(transactions):
    annotated = ((t.category + "<>" + t.desc, t) for t in transactions)
    grouped = {}
    for key, t in annotated:
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(t)

    _sorted = sorted(grouped.items(), key=lambda item: len(item[1]))
    _reversed = reversed(_sorted)

    ret = []
    for k,v in _reversed:
        ret.extend(v)
    return ret
categorized_transactions = sort_transactions(categorized_transactions)

class CategoryBox(gui.Combobox):
    transaction: Record.CategorizedRecord
class CBevent(gui.tkinter.Event):
    widget: CategoryBox

# [(pattern, new)]
added_templates: list[tuple[dict, dict]] = []
def onModification(event: CBevent):
    text = event.widget.get()

    t = event.widget.transaction
    pattern = t.items()
    pattern.pop('category')
    new = {'category': text}

    create = True
    for i, (p, _) in enumerate(added_templates):
        # Overwrite existing, if there is one
        if p == pattern:
            added_templates[i] = (pattern, new)
            create = False
            break
    if create:
        added_templates.append((pattern, new))

# Populate the table
widths = {'account': 10, 'date': 10, 'desc': 40, 'value': 8, 'source-specific': None, 'category': 20}
widths = list(widths.values())
for r, row in enumerate(categorized_transactions):
    for c, cell in enumerate(row.values()):
        if c == 4: continue # Skip the source-specific data
        if c == 5:
            # Category
            cat = CategoryBox(master = table.frame, values = Constants.categories, initial = row.category, width = widths[c])
            cat.set_state_readonly()
            cat.grid(row=r, column=c)
            cat.bind(func = onModification)
            cat.transaction = row
            disable_scroll(cat)
        else:
            if c < len(widths) and (widths[c] is not None):
                gui.tkinter.Label(table.frame, text = str(cell), anchor = 'w', relief='solid', bd = 1, width=widths[c]).grid(row=r, column=c)
            else:
                gui.tkinter.Label(table.frame, text = str(cell), anchor = 'w', relief='solid', bd = 1).grid(row=r, column=c)

root.mainloop()

if added_templates:
    raise RuntimeError("Auto-generating templates temporarily disabled")

for pattern, new in added_templates:
    Categorize.add_template("Auto-generated", "", pattern, new)
if added_templates:
    print("Saving added templates:")
    print(added_templates)
    Categorize.save_templates()
