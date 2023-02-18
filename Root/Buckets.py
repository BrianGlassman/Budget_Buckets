from Root import Constants as _import_Constants

class Bucket:
    def __init__(self, name, max_value, monthly_refill):
        self.name = name
        self.max_value = max_value
        self.refill = monthly_refill / 30
#%% Define buckets
_bucket_info: dict[_import_Constants.CatType, tuple]
_bucket_info = { # {category: (max, monthly)}
    # Car
    'Car - Note': (320, 320),
    'Car/Rental Insurance': (175, 160),
    'Car - Other': (300, 75),
    'Car - Parking Pass': (75, 50), # TODO change to just "Parking" or split pass from incidental. Can't do until after porting over old sheet

    # Education
    'Self-improvement': (100, 10),

    # Entertainment
    'Dates': (150, 50),
    'Entertainment - Other': (75, 20),
    'Games': (75, 20),
    'Going Out': (150, 50),
    'Books': (75, 20),
    'Big Fun': (500, 20),

    # Food
    'Groceries': (300, 250),
    'Food - nice': (100, 80),

    # Housing
    'Rent': (1850, 1850),
    'Utilities': (200, 150),
    'Internet': (40.41, 40.41),
    'Housing - Other': (150, 100),
    'Decoration': (150, 20),

    # Investments/Savings
    '401k': (0, 0),
    'Retirement': (0, 0),
    'Long-term': (0, 0),
    'Unexpected Fund': (0, 0),

    # Medical/Dental
    'Medical - Other': (200, 20),
    'Medical Insurance': (0, 0),

    # Other
    'ATM': (200, 25),
    'Other - Other': (200, 20),

    # Personal Care / Clothing
    'Clothes/Personal care': (100, 30),

    # Uncategorized
    _import_Constants.todo_category: (0, 0),
}
bucket_info = {category:Bucket(category, max_value, monthly_refill) for category, (max_value, monthly_refill) in _bucket_info.items()}
