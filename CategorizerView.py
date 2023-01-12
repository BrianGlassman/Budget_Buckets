from dataclasses import dataclass

import Record

#%% Parsing
import Parsing

transactions: list[Record.RawRecord]
transactions = Parsing.run()

#%% Categorizing
import Categorize
from Root import Constants

limit = -1 # Use -1 for all
use_uncat = True # Whether to show uncategorized items
use_cat = True # Whether to show categorized items

categorized_transactions = Categorize.run(
    transactions=transactions, limit=limit, use_uncat=use_uncat, use_cat=use_cat, use_internal=True)

#%% Display
import TkinterPlus as gui

root = gui.Root(17, 30)

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
# categorized_transactions = sort_transactions(categorized_transactions)

# FIXME? Should it check existing auto-generated templates?
# [{"raw": raw transaction, "new": new_to_add}, ...]
@dataclass
class AddedTemplate:
    """Class to make type-checking easier"""
    raw: Record.RawRecord
    new: dict
added_templates: list[AddedTemplate] = []
def update_templates(transaction: Record.RawRecord, new: dict) -> None:
    # Get/create the matching entry
    for template in added_templates:
        # Overwrite existing, if there is one
        if template.raw == transaction:
            break
    else:
        # No existing, create new
        added_templates.append(AddedTemplate(raw=transaction, new=dict()))
        template = added_templates[-1]

    n = template.new
    assert isinstance(n, dict) # For Pylance and oops-catching
    # Fill in required information
    n.setdefault('category', Constants.todo_category)
    n.setdefault('split', 1)
    # Fill in the given information
    n.update(new)

class CategoryBox(gui.Combobox):
    transaction: Record.CategorizedRecord
class CBevent(gui.tkinter.Event):
    widget: CategoryBox
def CB_onModification(event: CBevent):
    text = event.widget.get()

    t = event.widget.transaction
    new = {'category': text}

    assert t.rawRecord is not None
    update_templates(t.rawRecord, new)

class Comment(gui.WatchedText):
    transaction: Record.CategorizedRecord
class CmtEvent(gui.tkinter.Event):
    widget: Comment
def Cmt_onModification(event: CmtEvent):
    text = event.widget.get('1.0', 'end').strip()

    t = event.widget.transaction
    new = {'comment': text}

    assert t.rawRecord is not None
    update_templates(t.rawRecord, new)

# Populate the table
widths = {'account': 10, 'date': 10, 'desc': 40, 'value': 8, 'source-specific': None, 'category': 20, 'comment': 30}
widths = list(widths.values())
for r, row in enumerate(categorized_transactions):
    for c, cell in enumerate(row.values()):
        if c == 4: continue # Skip the source-specific data
        elif c == 5:
            # Category
            cat = CategoryBox(master = table.frame, values = Constants.categories, initial = row.category, width = widths[c])
            cat.set_state_readonly()
            cat.grid(row=r, column=c)
            cat.bind(func = CB_onModification)
            cat.transaction = row
            disable_scroll(cat)
        elif c == 6:
            # Comment
            if cell is None: cell = ''
            cmt = Comment(table.frame, text = str(cell), relief='solid', bd = 1, width=widths[c], height=1)
            cmt.grid(row=r, column=c)
            cmt.watch(func = Cmt_onModification)
            cmt.transaction = row
        else:
            if c < len(widths) and (widths[c] is not None):
                gui.tkinter.Label(table.frame, text = str(cell), anchor = 'w', relief='solid', bd = 1, width=widths[c]).grid(row=r, column=c)
            else:
                gui.tkinter.Label(table.frame, text = str(cell), anchor = 'w', relief='solid', bd = 1).grid(row=r, column=c)

root.mainloop()

for template in added_templates:
    pattern = template.raw.items()
    new = template.new
    Categorize.add_template(["Auto-generated", "Individual"], "", pattern, new)
if added_templates:
    print("Saving added templates:")
    print(added_templates)
    Categorize.save_templates()
