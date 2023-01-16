import datetime

from Root import Sorting
import Record
import Functionified as fn

#%% Category separating
# Take the daily average and apply going forwards
_avg_cats = (
    # Car
    # 'Car - Note', # predict_regular
    'Car/Rental Insurance',
    'Car - Other',
    'Car - Parking Pass', # TODO change to just "Parking" or split pass from incidental. Can't do until after porting over old sheet

    # Education
    # 'Self-improvement',

    # Entertainment
    # 'Dates', # Only one day :(
    'Entertainment - Other',
    'Games',
    'Going Out',
    'Books',
    # 'Big Fun',

    # Food
    'Groceries',
    'Food - nice',

    # Housing
    # 'Rent', # predict_regular
    'Utilities',
    # 'Internet', # predict_regular
    'Housing - Other',
    'Decoration',

    # Investments/Savings
    # '401k',
    # 'Retirement',
    # 'Long-term',
    # 'Unexpected Fund',

    # Medical/Dental
    'Medical - Other',
    'Medical Insurance',

    # Other
    'ATM',
    'Other - Other',

    # Personal Care / Clothing
    # 'Clothes/Personal care', # Only one day
)
_regular_cats = (
    'Car - Note',
    'Rent',
    'Internet',
)

#%% Helper functions
def _get_avg_values(transactions):
    """Assumes transactions are sorted by date"""
    avg_vals = {}
    for cat in _avg_cats:
        try:
            temp = [x for x in transactions if x.category == cat]
            if len(temp) == 0: continue
            days = (temp[-1].date - temp[0].date).days
            value = sum(x.value for x in temp)
            if value == 0: continue
            avg_vals[cat] = value / days
        except Exception:
            print(cat)
            raise
    return avg_vals

def _predict_regular(transactions, category):
    """Predict fixed monthly expenses (ex. rent, car note, etc.)
    Assumes transactions are sorted by date"""
    transactions = [x for x in transactions if x.category == category]
    if len(transactions) == 0: return []
    last_actual = transactions[-1]
    last_actual: Record.CategorizedRecord
    assert last_actual.rawRecord is not None
    stop = datetime.date(2023, 6, 30)

    # Start one month after the last actual, then each month after that
    future_transactions = []
    date = fn.inc_month(last_actual.date)
    while date < stop:
        new = Record.CategorizedRecord.from_RawRecord(last_actual.rawRecord, last_actual.category)
        new.desc = "--- Extrapolate from last instance ---"
        new.date = date
        future_transactions.append(new)

        date = fn.inc_month(date)
    
    return future_transactions

#%% Main
def make_predictions(actual_transactions) -> list[Record.CategorizedRecord]:
    # Pre-processing
    categorized_transactions = Sorting.by_date(actual_transactions)
    avg_values = _get_avg_values(actual_transactions)

    # Prediction
    stop = datetime.date(2023, 6, 30) # Predict until a little after graduation
    actual_transactions = categorized_transactions ; del categorized_transactions
    future_transactions = []

    for cat in _regular_cats:
        try:
            future_transactions.extend(_predict_regular(actual_transactions, cat))
        except Exception:
            print(cat)
            raise

    for cat, daily_val in avg_values.items():
        # Get the last real transaction
        last_actual = [x for x in actual_transactions if x.category == cat][-1]
        last_date: datetime.date = last_actual.date

        # Start predictions on 15th of next month
        date = last_date.replace(day=15)
        date = fn.inc_month(date)

        # Create one predicted transaction per month
        while date < stop:
            delta = (date - last_date).days

            new = Record.CategorizedRecord('', date, '--- Extrapolate daily average ---',
                round(daily_val*delta, 2), category=cat)
            future_transactions.append(new)

            last_date = date
            date = fn.inc_month(date)

    # Sort before returning
    future_transactions = Sorting.by_date(future_transactions)

    return future_transactions
