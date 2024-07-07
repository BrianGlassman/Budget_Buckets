categories = """
Car - Note
Car/Rental Insurance
Car - Other
Car - Parking Pass
Self-improvement
Dates
Entertainment - Other
Games
Going out
Books
Big Fun
Groceries
Food - nice
Rent
Utilities
Internet
Housing - Other
Decoration
401k
Retirement
Long-term
Unexpected Fund
Medical - Other
Medical Insurance
ATM
Other - Other
Clothes/Personal care
Parental Funds
Salary
Income - Other
CC Payments
Internal Transfers
"""
categories = [c.strip() for c in categories.splitlines()]
categories = [c for c in categories if c]