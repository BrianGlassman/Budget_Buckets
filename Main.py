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

#%% Main

mode = ModeSetter(Modes.BucketTimeline,
    predict=True)

# Parse
transactions = Parsing.run()

# Categorize
cat_filter = []
keep_filter = True
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
