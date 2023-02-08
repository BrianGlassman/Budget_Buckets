import datetime
import _collections_abc

from Root import Constants
import Record

class CategorizeConfig(_collections_abc.Mapping):
    cat_filter: list
    keep_filter: bool
    limit: int
    use_uncat: bool
    use_cat: bool
    def __init__(self) -> None:
        self.cat_filter = []
        self.keep_filter = False
        self.limit = 0
        self.use_cat = True
        self.use_uncat = True

    # Implement Mapping to enable ** operator
    # Ref: https://stackoverflow.com/a/33402305
    def __getitem__(self, __key: str):
        return self.__getattribute__(__key)
    def __iter__(self):
        yield from ('cat_filter', 'keep_filter', 'limit', 'use_cat', 'use_uncat')
    def __len__(self) -> int:
        return super().__len__()

_default_categorize_config = CategorizeConfig()

df = _default_categorize_config
def categorize(transactions, cat_filter=df.cat_filter, keep_filter=df.keep_filter, limit=df.limit,
    use_uncat=df.use_uncat, use_cat=df.use_cat, use_internal=False) -> list[Record.CategorizedRecord]:
    """
    cat_filter - list of categories to include/exclude
    keep_filter - if False, exclude the categories in cat_filter. If True, include only those categories
    limit = 0 # Use 0 for all
    use_uncat = True # Whether to show uncategorized items
    use_cat = True # Whether to show categorized items
    """
    import Categorize

    assert all(cat in Constants.categories for cat in cat_filter)

    categorized_transactions = Categorize.run(
        transactions=transactions, limit=limit, use_uncat=use_uncat, use_cat=use_cat, use_internal=use_internal)

    categorized_transactions = [x for x in categorized_transactions if
        (x.category in cat_filter) == keep_filter # weird boolean logic to make filtering work correctly
        ]
    
    return categorized_transactions
del df

def add_month(date: datetime.date, inc: int) -> datetime.date:
    """Increments the month, incrementing year if needed
    Returns the new date"""
    assert isinstance(date, datetime.date)
    if date.day > 28: raise NotImplementedError("Not sure what happens if day isn't in month")
    assert isinstance(inc, int)
    assert inc in [1, -1]
    month = date.month + inc
    if month > 12:
        month = 1
        year = date.year + 1
    elif month < 1:
        month = 12
        year = date.year - 1
    else:
        year = date.year
    return date.replace(year=year, month=month)
def inc_month(date: datetime.date): return add_month(date, +1)
def dec_month(date: datetime.date): return add_month(date, -1)

def get_str_stop(transactions):
    """Get the earliest and latest date
    Makes no assumptions about sorting"""
    strt: datetime.date
    stop: datetime.date
    strt = min(x.date for x in transactions)
    stop = max(x.date for x in transactions)
    return strt, stop