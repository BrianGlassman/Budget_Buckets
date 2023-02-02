from functools import partial

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
    class Mode:
        def __init__(self, value: int) -> None:
            self.value = value
    MainMenu = Mode(-1)
    CategorizerView = Mode(0)
    BucketTimeline = Mode(1)
    TransactionTimeline = Mode(2)
    MView = Mode(3)

class ModeSetter:
    def __init__(self, mode=Modes.MainMenu, *, predict=False) -> None:
        self.mode = mode
        self._predict = predict

    # Mode properties
    @property
    def isMainMenu(self):
        return self.mode == Modes.MainMenu
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

#%% Observers

#%% Model
class Model():
    data_read = False
    data_listeners = []

    categorized_transactions: list

    @classmethod
    def update_data(cls):
        cls.data_read = True
        for listener in cls.data_listeners:
            listener.update()

#%% Runners
def report(*args, **kwargs):
    """Either prints or displays to the gui, as appropriate"""
    # TODO display to gui
    print(*args, **kwargs)

def run_MainMenu():
    """Opens a GUI for selecting options"""
    root = gui.Root(10, 10)

    class Button:
        key: str
        label: str
        # callback: 
        dependencies: list[str]
        obj: gui.Button
        def __init__(self, key, label, *, callback, dependencies=set()) -> None:
            self.key = key
            self.label = label
            self.callback = callback
            self.dependencies = dependencies

            if 'data' in dependencies:
                Model.data_listeners.append(self)

        def create(self, parent, width):
            state = gui.tkinter.DISABLED if self.dependencies else gui.tkinter.ACTIVE
            self.obj = gui.Button(master=parent, text=self.label, command=self.callback, width=width, state=state)

        def update(self):
            if Model.data_read:
                self.obj['state'] = gui.tkinter.ACTIVE

    buttons = {}
    buttons: dict[str, Button]
    def _make_buttons():
        """Function for scoping reasons"""
        for key, label, callback, dependencies in (
                ('Load', 'Load Data', load_data, set()),
                ('Predict', 'Predict Future Transactions', predict, {'data'}),
                ('MView', 'Summary Table', run_MView, {'data'}),
                ('CView', 'Categorizing', run_CView, {'data'}),
                ('TTime', 'Transaction Timeline', None, {'data'}),
                ('BTime', 'Bucket Timeline', run_BTime, {'data'}),
            ):
            buttons[key] = Button(key=key, label=label, callback=callback, dependencies=dependencies)
    _make_buttons()

    # Make the buttons
    width = max(len(b.label) for b in buttons.values())
    for button in buttons.values():
        button.create(parent=root, width=width)
        button.obj.pack()
    
    root.mainloop()

def load_data():
    # Parse
    transactions = Parsing.run()

    # Categorize
    categorized_transactions = fn.categorize(transactions)

    # Pre-processing
    categorized_transactions = Sorting.by_date(categorized_transactions)

    report("Loading complete")
    Model.update_data()
    
    Model.categorized_transactions = categorized_transactions

def predict():
    actual_transactions = Model.categorized_transactions
    future_transactions = Predict.make_predictions(actual_transactions)
    return future_transactions

def run_CView():
    categorized_transactions = Model.categorized_transactions

    # Needed because some functions use enclosing scope
    added_templates: list[CategorizerView.AddedTemplate] = []
    
    root = gui.Root(17, 30)
    _ = CategorizerView.create_table(root, categorized_transactions)
    root.mainloop()

    CategorizerView.post_process(added_templates)

def run_BTime():
    categorized_transactions = Model.categorized_transactions

    categorized_transactions = [x for x in categorized_transactions
        if x.category not in BucketTimeline.skip_cats]
    
    bucket_tracker = BucketTimeline.pre_process(categorized_transactions)

    BucketTimeline.display(bucket_tracker)

def run_MView():
    categorized_transactions = Model.categorized_transactions
    
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

mode = ModeSetter(
    Modes.MainMenu,
    predict=True)

if mode.isMainMenu:
    run_MainMenu()
else:
    load_data()

    if mode.predict:
        Model.categorized_transactions.extend(predict())

    if mode.isCView:
        run_CView()
    elif mode.isBTime:
        run_BTime()
    elif mode.isMView:
        run_MView()
