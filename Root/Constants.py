import datetime as _import_datetime
import os as _import_os

one_day = _import_datetime.timedelta(days=1)

CatType = str

# Collect file paths in one place so that other things can reference them
# (namely, the Build script)
AutoTemplates_file = _import_os.path.join('Categorize', 'AutoTemplates.json')
Templates_file = _import_os.path.join('Categorize', 'Templates.json')
ManualAccountHandling_file = _import_os.path.join('Categorize', 'ManualAccountHandling.json')
ParseSettings_file = _import_os.path.join('Parsing', 'ParseSettings.csv')
Constants_file = _import_os.path.join('Root', 'Constants.py') # Not used, but good for the user to have
filepaths = [
    AutoTemplates_file,
    Templates_file,
    ManualAccountHandling_file,
    ParseSettings_file,
    Constants_file,
]

categories = (
    # Car
    'Car - Note',
    'Car/Rental Insurance',
    'Car - Other',
    'Car - Parking Pass', # TODO change to just "Parking" or split pass from incidental. Can't do until after porting over old sheet

    # Education
    'Self-improvement',

    # Entertainment
    'Dates',
    'Entertainment - Other',
    'Games',
    'Going Out',
    'Books',
    'Big Fun',

    # Food
    'Groceries',
    'Food - nice',

    # Housing
    'Rent',
    'Utilities',
    'Internet',
    'Housing - Other',
    'Decoration',

    # Investments/Savings
    '401k',
    'Retirement',
    'Long-term',
    'Unexpected Fund',

    # Medical/Dental
    'Medical - Other',
    'Medical Insurance',

    # Other
    'ATM',
    'Other - Other',

    # Personal Care / Clothing
    'Clothes/Personal care',

    # Income
    'Parental Funds',
    'Loans',
    'Salary',
    'Income - Other',

    # Internal
    'CC Payments',
    'Internal Transfers',
    )

todo_category = '*** TODO ***'
del_category = 'DELETE' # Flag to delete this transaction (keep in raw data for checksumming against sources)
categories_inclTodo = tuple(list(categories) + [todo_category])

expense_categories = (
    # Car
    'Car - Note',
    'Car/Rental Insurance',
    'Car - Other',
    'Car - Parking Pass', # TODO change to just "Parking" or split pass from incidental. Can't do until after porting over old sheet

    # Education
    'Self-improvement',

    # Entertainment
    'Dates',
    'Entertainment - Other',
    'Games',
    'Going Out',
    'Books',
    'Big Fun',

    # Food
    'Groceries',
    'Food - nice',

    # Housing
    'Rent',
    'Utilities',
    'Internet',
    'Housing - Other',
    'Decoration',

    # Investments/Savings
    '401k',
    'Retirement',
    'Long-term',
    'Unexpected Fund',

    # Medical/Dental
    'Medical - Other',
    'Medical Insurance',

    # Other
    'ATM',
    'Other - Other',

    # Personal Care / Clothing
    'Clothes/Personal care',
)

income_categories = (
    # Income
    'Parental Funds',
    'Loans',
    'Salary',
    'Income - Other',
)

internal_categories = (
    # Internal
    'CC Payments',
    'Internal Transfers',
)