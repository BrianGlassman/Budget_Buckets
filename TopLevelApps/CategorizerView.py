#%% Imports
from dataclasses import dataclass
import dash

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

# Callbacks
def CB_onModification(event):
    text = event.widget.get()

    t = event.widget.transaction
    new = {'category': text}

    assert t.rawRecord is not None
    update_templates(t.rawRecord, new)

def Cmt_onModification(event):
    text = event.widget.get('1.0', 'end').strip()

    t = event.widget.transaction
    new = {'comment': text}

    assert t.rawRecord is not None
    update_templates(t.rawRecord, new)

#%% Table processing
def create_table(categorized_transactions):
    # Header
    header = ['Account', 'Date', 'Description', 'Value', 'UNUSED source-specific', 'Category', 'Comment', 'Dur.']

    # Populate the table
    data = []
    for transaction in categorized_transactions:
        table_row = {}
        for key, cell in zip(header, transaction.values()):
            if key.startswith('UNUSED'): continue # Skip the source-specific data
            elif key == 'Category': table_row[key] = cell
            elif key == 'Comment': table_row[key] = str(cell)
            else: table_row[key] = (str(cell))
        data.append(table_row)
    
    columns = []
    for name in header:
        if name.startswith('UNUSED'): continue
        entry = {'name': name, 'id': name}
        if name == 'Category':
            entry.update(dict(presentation = 'dropdown'))
        if name in ('Category', 'Comment', 'Dur.'):
            entry.update(dict(editable = True)) # type: ignore
        columns.append(entry)


    table = dash.dash_table.DataTable(
        columns=columns,
        data=data,
        dropdown={
            'Category': {
                'options': [{'label': cat, 'value': cat} for cat in Categories.categories],
            }
        },
        page_size=50,
        # page_action='none', # Can uncomment to show everything on one page, but then it gets pretty slow
    )

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

class CategorizerView:
    def __init__(self, categorized_transactions: list[Record.CategorizedRecord]):
        create_table(categorized_transactions=categorized_transactions)

    # FIXME re-enable this somehow
    # def on_close(self):
    #     post_process()
    #     self.destroy()

#%% Main
if __name__ == "__main__":
    import Functionified as fn

    # Parse
    transactions = Parsing.run()

    # Categorize
    categorized_transactions = fn.categorize(transactions, use_cat=True, use_uncat=True, limit=0)

    # Pre-processing
    # categorized_transactions = Sorting.cat_then_desc(categorized_transactions)
    categorized_transactions = Sorting.by_date(categorized_transactions)

    app = dash.Dash(__name__)

    table = create_table(categorized_transactions)

    app.layout = dash.html.Div(table)

    app.run(debug=True)
