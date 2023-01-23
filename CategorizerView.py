#%% Imports
from dataclasses import dataclass
import TkinterPlus as gui

from Root import Constants
from Root import Sorting
import Record
import Parsing
import Categorize

#%% Definitions for GUI

# FIXME? Should it check existing auto-generated templates?
@dataclass
class AddedTemplate:
    """Class to make type-checking easier"""
    raw: Record.RawRecord # The existing RawRecord to match against
    new: dict # Dict of new values to set

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
    n.setdefault('duration', 1)
    # Fill in the given information
    n.update(new)

# Callbacks (and subclasses for typing)
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

#%% Table processing
def create_table(root, categorized_transactions):
    table = gui.ScrollableFrame(root)
    table.pack(side = "top", fill="both", expand=True)

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
                cat.disable_scroll()
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
    return table

def post_process(added_templates):
    successful_add = []
    failed_add = []
    for template in added_templates:
        pattern = template.raw.items()
        new = template.new
        try:
            Categorize.add_template(["Auto-generated", "Individual"], "", pattern, new)
        except Exception as e:
            failed_add.append(template)
            print(template)
            print(e)
        else:
            successful_add.append(template)
    if successful_add:
        print("Saving added templates:")
        print(successful_add)
        Categorize.save_templates()
    if failed_add:
        print("FAILED TO ADD TEMPLATES:")
        print(failed_add)
        print('\n\n F A I L E D   T E M P L A T E S\n\n')

#%% Main
if __name__ == "__main__":
    import Functionified as fn

    # Parse
    transactions = Parsing.run()

    # Categorize
    categorized_transactions = fn.categorize(transactions, cat_filter=[], keep_filter=True)

    # Pre-processing
    # categorized_transactions = Sorting.cat_then_desc(categorized_transactions)
    categorized_transactions = Sorting.by_date(categorized_transactions)

    # Needed because some functions use enclosing scope
    added_templates: list[AddedTemplate] = []

    root = gui.Root(17, 30)
    table = create_table(root, categorized_transactions)
    root.mainloop()

    post_process(added_templates)
