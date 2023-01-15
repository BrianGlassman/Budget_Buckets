import Parsing
from Root import Sorting
import Functionified as fn
import TkinterPlus as gui

import CategorizerView
import BucketTimeline
# import TransactionTimeline
# import MView

#%% Mode handling
class ModeSetter:
    CategorizerView = 0
    BucketTimeline = 1
    TransactionTimeline = 2
    MView = 3

    def __init__(self, mode) -> None:
        self.mode = mode

    @property
    def is_CView(self):
        return self.mode == self.CategorizerView
    @property
    def is_BTime(self):
        return self.mode == self.BucketTimeline
    @property
    def is_TTime(self):
        return self.mode == self.TransactionTimeline
    @property
    def is_MView(self):
        return self.mode == self.MView

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

mode = ModeSetter(ModeSetter.BucketTimeline)

# Parse
transactions = Parsing.run()

# Categorize
cat_filter = []
keep_filter = True
if mode.is_BTime:
    cat_filter = BucketTimeline.skip_cats
    keep_filter = False
categorized_transactions = fn.categorize(transactions,
    cat_filter=cat_filter, keep_filter=keep_filter)

# Pre-processing
categorized_transactions = Sorting.by_date(categorized_transactions)

if mode.is_CView:
    run_CView(categorized_transactions)
elif mode.is_BTime:
    run_BTime(categorized_transactions)
