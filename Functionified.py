import datetime

def categorize(transactions, cat_filter = [], keep_filter=True, limit = 0, use_uncat = True, use_cat = True):
    """
    cat_filter - list of categories to include/exclude
    keep_filter - if False, exclude the categories in cat_filter. If True, include only those categories
    limit = 0 # Use 0 for all
    use_uncat = True # Whether to show uncategorized items
    use_cat = True # Whether to show categorized items
    """
    import Categorize

    categorized_transactions = Categorize.run(
        transactions=transactions, limit=limit, use_uncat=use_uncat, use_cat=use_cat, use_internal=False)

    categorized_transactions = [x for x in categorized_transactions if
        (x.category in cat_filter) == keep_filter # weird boolean logic to make filtering work correctly
        ]
    
    return categorized_transactions

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