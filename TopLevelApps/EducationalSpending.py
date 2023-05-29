#%% Imports
from dataclasses import dataclass
import TkinterPlus as gui

from BaseLib import Categories, Sorting
from Classes import Record
from Handlers import Parsing
from Handlers import Categorize
import Functionified as fn

#%% Definitions for GUI

# FIXME? Should it check existing auto-generated templates?
@dataclass
class AddedTemplate:
    """Class to make type-checking easier"""
    raw: Record.RawRecord # The existing RawRecord to match against
    new: dict # Dict of new values to set

added_templates: list[AddedTemplate] = []

def update_templates(transaction: Record.RawRecord, new: dict) -> None:
    # FIXME doesn't detect generic templates (i.e. only detects existing individual templates)
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
    n.setdefault('category', Categories.todo_category)
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
    table = gui.ScrollableFrame(root, hscroll=False)
    table.pack(side = "top", fill="both", expand=True)

    # Table settings
    widths = {'account': 10, 'date': 10, 'desc': 40, 'value': 8, 'source-specific': None, 'category': 20, 'comment': 30, 'duration': 4}
    widths = list(widths.values())

    # Header
    for c, name in enumerate(['Account', 'Date', 'Description', 'Value', 'UNUSED source-specific', 'Category', 'Comment', 'Dur.']):
        if name.startswith('UNUSED'): continue
        gui.tkinter.Label(table.frame, text=name, anchor='center', relief='solid', bd=1, width=widths[c]).grid(row=0, column=c)

    # Populate the table
    for r, row in enumerate(categorized_transactions):
        r += 1 # Account for header
        for c, cell in enumerate(row.values()):
            if c == 4: continue # Skip the source-specific data
            elif c == 5:
                # Category
                cat = CategoryBox(master = table.frame, values = Categories.categories, initial = row.category, width = widths[c])
                cat.set_state_readonly()
                cat.grid(row=r, column=c)
                cat.bind(func = CB_onModification)
                cat.transaction = row
                cat.disable_scroll()
            elif c == 6:
                # Comment
                cmt = Comment(table.frame, text = str(cell), relief='solid', bd = 1, width=widths[c], height=1)
                cmt.grid(row=r, column=c)
                cmt.watch(func = Cmt_onModification)
                cmt.transaction = row
            else:
                if c < len(widths) and (widths[c] is not None):
                    gui.tkinter.Label(table.frame, text = str(cell), anchor = 'w', relief='solid', bd = 1, width=widths[c]).grid(row=r, column=c)
                else:
                    gui.tkinter.Label(table.frame, text = str(cell), anchor = 'w', relief='solid', bd = 1).grid(row=r, column=c)
        
        # Avoid freezing the computer with too much stuff
        if r >= 50:
            label = gui.tkinter.Label(table.frame, text = 'Max row count reached, use Configure menu to limit transactions',
                anchor='center', font=('', 20, 'bold'))
            label.grid(row=r+1, column=0, columnspan=table.frame.grid_size()[0])
            break
    return table

def post_process():
    successful_add = []
    failed_add = []
    for template in added_templates:
        pattern = template.raw.items()
        new = template.new
        try:
            Categorize.add_auto_template("", pattern, new)
        except Exception as e:
            failed_add.append(template)
            print('-'*25)
            print("Failed to add template:")
            print(template)
            print("Error message:")
            print(e)
            print('-'*25)
        else:
            successful_add.append(template)
    if successful_add:
        print("Saving added templates:")
        print(successful_add)
        Categorize.save_auto_templates()
    if failed_add:
        print("FAILED TO ADD TEMPLATES:")
        print(failed_add)
        print('\n\n F A I L E D   T E M P L A T E S\n\n')
    
    # Summary line at the end
    if len(successful_add) == 0 and len(failed_add) == 0:
        print("\nNo changes made\n")
    elif len(successful_add) > 0 and len(failed_add) == 0:
        print("\nSuccess\n")

class CategorizerView(gui.Root):
    def __init__(self, categorized_transactions: list[Record.CategorizedRecord]):
        super().__init__(17, 30)
        create_table(root=self, categorized_transactions=categorized_transactions)

        self.protocol('WM_DELETE_WINDOW', self.on_close)
        self.mainloop()
    
    def on_close(self):
        post_process()
        self.destroy()

#%% Main
if __name__ == "__main__":
    import Functionified as fn

    # Parse
    transactions = Parsing.run()

    # Categorize
    categorized_transactions = fn.categorize(transactions, use_cat=True, use_uncat=True, limit=0)

    # Restrict to pre-graduation
    import datetime
    graduation = datetime.date(2023, 5, 1) # Be conservative, drop all of May even though I was in class for a week
    categorized_transactions = [x for x in categorized_transactions if x.date < graduation]

    totals = {year:0.0 for year in [2021, 2022, 2023]}

    # According to https://www.irs.gov/publications/p970 internet access while enrolled counts as educational expense
    internet = [x for x in categorized_transactions if x.category == 'Internet']
    assert not any(x.account == 'CU Bills' for x in internet)
    print("\nTotal for internet: (TODO need to limit to only when I was enrolled)")
    for year in [2021, 2022, 2023]:
        year_total = sum(x.value for x in internet if x.date.year == year)
        print(f"{year}: ${year_total:0,.2f}")
        totals[year] += year_total

    # According to https://www.irs.gov/publications/p970#idm140550550966672 room and board is a QEA under conditions
    """
    Expenses for room and board must be incurred by students who are enrolled at least half-time (defined later).
    The expense for room and board qualifies only to the extent that it isn't more than the greater of the following two amounts.
    a.  The allowance for room and board, as determined by the school, that was included in the cost of attendance (for federal financial aid purposes)
        for a particular academic period and living arrangement of the student.
    b.  The actual amount charged if the student is residing in housing owned or operated by the school.
    You may need to contact the eligible educational institution for qualified room and board costs.
    """
    # From https://www.colorado.edu/bursar/costs/costs-college-school-and-program/fallspring-costs/graduate-colorado-resident/fallspring-7
    """
    15,830 per year (Fall/Spring) --> 7,915 per term
    """
    room_board = [x for x in categorized_transactions if x.category in ('Rent', 'Groceries', 'Food - nice') and x.account != 'CU Bills']
    room_board = [x for x in room_board if "Hazel's" not in x.desc]
    assert not any(x.account == 'CU Bills' for x in room_board)
    print("\nTotal for room and board: (TODO need to limit to only when I was enrolled)")
    for year in [2021, 2022, 2023]:
        if year == 2022:
            cap = 15830.0
        else:
            cap = 15830/2
        year_total = sum(x.value for x in room_board if x.date.year == year)
        print(f"{year}: ${year_total:0,.2f} (cap: ${cap:0,.2f})")
        totals[year] += min(year_total, cap)

    cu_bills = [x for x in categorized_transactions if x.account == 'CU Bills']
    def is_cu_bill(t: Record.CategorizedRecord):
        desc = t.desc
        if any(x in desc for x in ['Insurance', 'Meal Plan', 'Supplies', 'Parking']):
            return False
        return True
    cu_bills = [x for x in cu_bills if is_cu_bill(x)]
    print("\nTotal for CU Bills:")
    for year in [2021, 2022, 2023]:
        year_total = sum(x.value for x in cu_bills if x.date.year == year)
        print(f"{year}: ${year_total:0,.2f}")
        totals[year] += year_total

    categorized_transactions = internet + room_board + cu_bills
    categorized_transactions = [x for x in categorized_transactions if x.date.year == 2023]

    print("\nYearly totals:")
    for year, total in totals.items():
        print(f"{year}: ${total:0,.2f}")

    # Pre-processing
    # categorized_transactions = Sorting.cat_then_desc(categorized_transactions)
    categorized_transactions = Sorting.by_date(categorized_transactions)

    CategorizerView(categorized_transactions)

# %%
