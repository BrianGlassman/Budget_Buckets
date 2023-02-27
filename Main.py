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
    # Static class, so only use class variables
    data_read = False
    data_listeners = []
    config = fn.CategorizeConfig()

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
        for key, label, (callback, cb_args), dependencies in (
                ('Config', 'Configure', (run_config, []), set()),
                ('Template', 'Template Viewer', (run_templates, []), set()),
                ('Load', 'Load Data', (load_data, []), set()),
                ('Predict', 'Predict Future Transactions', (predict, []), {'data'}),
                ('MView', 'Summary Table', (run_MView, []), {'data'}),
                ('CView', 'Categorizing', (run_CView, []), {'data'}),
                # ('TTime', 'Transaction Timeline', (lambda: 0, []), {'data'}), # FIXME TransactionTimeline.py exists, but isn't functionified
                ('BTime', 'Bucket Timeline', (run_BTime, []), {'data'}),
            ):
            # Add the arguments to the callback
            callback = partial(callback, *cb_args) # type: ignore
            buttons[key] = Button(key=key, label=label, callback=callback, dependencies=dependencies)
    _make_buttons()

    # Make the buttons
    width = max(len(b.label) for b in buttons.values())
    for button in buttons.values():
        button.create(parent=root, width=width)
        button.obj.pack()
    
    root.mainloop()

def run_config():
    window = gui.Root(3,6, title='Config')

    def make_labelled_entry(parent, label: str, default: str):
        '''Makes a label on the left, with an entry box filling the rest of the space'''
        frame = gui.Frame(parent, relief=gui.tkinter.FLAT)
        label_obj = gui.tkinter.Label(frame, text=label+' ')
        label_obj.pack(side=gui.tkinter.LEFT)
        var = gui.tkinter.StringVar(value=default)
        entry = gui.Entry(frame, textvariable=var)
        entry.pack(side=gui.tkinter.RIGHT)
        frame.pack()
        return var, entry

    def make_labelled_checkbox(parent, label: str, default: bool, callback=None):
        '''Makes a checkbox on the right, with a right-aligned label to the left of it'''
        frame = gui.Frame(parent, relief=gui.tkinter.FLAT)
        label_obj = gui.tkinter.Label(frame, text=label, anchor='e')
        label_obj.pack(side=gui.tkinter.LEFT, fill='both', expand=1) # Needs BOTH fill and expand
        var = gui.tkinter.BooleanVar(value=default)
        if callback is not None: var.trace_add('write', callback)
        checkbox = gui.tkinter.Checkbutton(frame, variable=var)
        checkbox.pack(side=gui.tkinter.RIGHT, anchor='e')
        frame.pack(fill='both')
        return var, checkbox

    cat_filter, _ = make_labelled_entry(window, 'Category filter', '[]')

    # keep_filter
    def callback(*_): Model.config.keep_filter = keep_filter.get() # type: ignore
    keep_filter, _ = make_labelled_checkbox(window, 'Keep filter categories', Model.config.keep_filter, callback=callback)

    # limit
    def callback(*_): # type: ignore
        """Uses enclosing scope so that I don't have to mess with order of definition vs packing"""
        if do_limit.get():
            limit_obj['state'] = gui.tkinter.NORMAL
        else:
            limit_obj['state'] = gui.tkinter.DISABLED
            limit_callback(val=0)
    do_limit, _ = make_labelled_checkbox(window, 'Limit transaction count', Model.config.limit > 0, callback)
    def limit_callback(*_, val=None): # type: ignore
        """Parse the limit field and set the Model config accordingly"""
        if val is not None:
            # Use the given value directly
            assert isinstance(val, int)
        else:
            # Get the value from the GUI
            # Entry gives a string, we want an int
            val = limit.get().strip()
            if val == '': val = 0
            try:
                val = int(val)
            except ValueError:
                raise RuntimeError(f"Tried to use a non-int limit {val}")
        Model.config.limit = val
    limit, limit_obj = make_labelled_entry(window, 'Limit', str(Model.config.limit))
    limit.trace_add('write', limit_callback)
    if do_limit.get():
        limit_obj['state'] = gui.tkinter.NORMAL
    else:
        limit_obj['state'] = gui.tkinter.DISABLED

    # use_cat
    def callback(*_): Model.config.use_cat = use_cat.get() # type: ignore
    use_cat, cb = make_labelled_checkbox(window, 'Include categorized', Model.config.use_cat, callback)

    # use_uncat
    def callback(*_): Model.config.use_uncat = use_uncat.get() # type: ignore
    use_uncat, _ = make_labelled_checkbox(window, 'Include uncategorized', Model.config.use_uncat, callback)

    # use_internal
    def callback(*_): Model.config.use_internal = use_internal.get() # type: ignore
    use_internal, _ = make_labelled_checkbox(window, 'Include internal transfers', Model.config.use_internal, callback)

    window.mainloop()

def run_templates():
    from TemplateViewer import TemplateViewer

    TemplateViewer()

def load_data():
    # Parse
    transactions = Parsing.run()

    # Categorize
    categorized_transactions = fn.categorize(transactions, **Model.config)

    # Pre-processing
    categorized_transactions = Sorting.by_date(categorized_transactions)

    report(f"Loading complete ({len(categorized_transactions)} records)")
    Model.update_data()
    
    Model.categorized_transactions = categorized_transactions

def predict():
    actual_transactions = Model.categorized_transactions
    future_transactions = Predict.make_predictions(actual_transactions)
    oldest = future_transactions[0].date
    newest = future_transactions[-1].date
    report(f"Predicted {len(future_transactions)} future transactions from {oldest} to {newest}")
    Model.categorized_transactions.extend(future_transactions)

def run_CView():
    categorized_transactions = Model.categorized_transactions

    root = gui.Root(17, 30)
    _ = CategorizerView.create_table(root, categorized_transactions)
    root.mainloop()

    CategorizerView.post_process()

def run_BTime():
    categorized_transactions = Model.categorized_transactions

    categorized_transactions = [x for x in categorized_transactions
        if x.category not in BucketTimeline.skip_cats]
    
    bucket_tracker = BucketTimeline.pre_process(categorized_transactions)

    BucketTimeline.display(bucket_tracker)

def run_MView():
    categorized_transactions = Model.categorized_transactions
    
    import datetime

    from Root import Buckets
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

    cat_groups = {'income': Buckets.income_categories, 'expenses': Buckets.expense_categories, 'internal': Buckets.internal_categories, 'UNCATEGORIZED': (Buckets.todo_category,)}
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

    # MView.make_tracker_sheet(root, values['income'], "Income", Buckets.income_categories, months)
    MView.make_tracker_sheet(root, values['expenses'], "Expenses", Buckets.expense_categories, months)
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
        predict()

    if mode.isCView:
        run_CView()
    elif mode.isBTime:
        run_BTime()
    elif mode.isMView:
        run_MView()
