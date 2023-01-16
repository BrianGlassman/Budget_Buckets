import Parsing
from Root import Sorting
import Functionified as fn
import TkinterPlus as gui

import CategorizerView
import BucketTimeline
# import TransactionTimeline
# import MView

import Predict

#%% Mode handling
class Modes:
    CategorizerView = 0
    BucketTimeline = 1
    TransactionTimeline = 2
    MView = 3

class ModeSetter:
    def __init__(self, mode, predict=False) -> None:
        self.mode = mode
        self._predict = predict

    # Mode properties
    @property
    def isCView(self):
        return self.mode == Modes.CategorizerView
    @property
    def isBTime(self):
        return self.mode == Modes.BucketTimeline
    @property
    def isTTime(self):
        return self.mode == Modes.TransactionTimeline
    @property
    def isMView(self):
        return self.mode == Modes.MView
    
    # Other properties
    @property
    def predict(self):
        return self._predict

#%% Runners
def run_CView(categorized_transactions):
    # Needed because some functions use enclosing scope
    added_templates: list[CategorizerView.AddedTemplate] = []
    
    root = gui.Root(17, 30)
    _ = CategorizerView.create_table(root, categorized_transactions)
    root.mainloop()

    CategorizerView.post_process(added_templates)

def run_BTime(categorized_transactions):
    bucket_tracker = BucketTimeline.pre_process(categorized_transactions)

    BucketTimeline.display(bucket_tracker)

def run_MView(categorized_transactions):
    import datetime

    from Root import Constants
    import MView

    # Get first/last month (instead of first/last date)
    strt, stop = fn.get_str_stop(categorized_transactions)
    strt = datetime.date(year=strt.year, month=strt.month, day=1)
    stop = datetime.date(year=stop.year, month=stop.month, day=1)

    # Create a consecutive list of months from strt to stop
    months: list[datetime.date] = []
    date = strt
    while date <= stop:
        months.append(date)
        date = fn.inc_month(date)

    cat_groups = {'income': Constants.income_categories, 'expenses': Constants.expense_categories, 'internal': Constants.internal_categories}
    values: dict[str, dict[str, dict[datetime.date, float]]] # {grouping: cat: {date_key: value}}}
    values = {}
    for group, categories in cat_groups.items():
        values[group] = {cat:{month:0 for month in months} for cat in categories}

    for t in categorized_transactions:
        cat = t.category
        group = None
        for g, categories in cat_groups.items():
            if cat in categories:
                assert group is None, f"Category '{cat}' appears in multiple groups"
                group = g
        assert group is not None, f"Category '{cat}' not found in any group"
        values[group][cat][MView.make_date_key(t.date)] += t.value

    root = gui.Root(25, 10)

    # MView.make_tracker_sheet(root, values['income'], "Income", Constants.income_categories, months)
    MView.make_tracker_sheet(root, values['expenses'], "Expenses", Constants.expense_categories, months)
    # MView.make_summary_sheet(root, values, 5000, months)

    root.mainloop()

#%% Main

mode = ModeSetter(Modes.MView,
    predict=True)

# Parse
transactions = Parsing.run()

# Categorize
cat_filter = []
keep_filter = False
if mode.isBTime:
    cat_filter = BucketTimeline.skip_cats
    keep_filter = False
categorized_transactions = fn.categorize(transactions,
    cat_filter=cat_filter, keep_filter=keep_filter)

# Pre-processing
categorized_transactions = Sorting.by_date(categorized_transactions)
if mode.predict:
    future_transactions = Predict.make_predictions(categorized_transactions)
    categorized_transactions.extend(future_transactions)

if mode.isCView:
    run_CView(categorized_transactions)
elif mode.isBTime:
    run_BTime(categorized_transactions)
elif mode.isMView:
    run_MView(categorized_transactions)
