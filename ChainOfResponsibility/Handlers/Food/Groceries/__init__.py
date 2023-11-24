# Project imports
from ....Base import HandlerChain, DescKeywords, DescAmount


grocery_stores = DescKeywords([
    "ACME",
    "Shoprite",
    "FreshGrocer",
    "King Soopers",
    "Safeway",
], name="Grocery Stores")

hello_fresh = DescAmount("HelloFresh", 49.81, 49.81, name="HelloFresh")

handler = HandlerChain(grocery_stores, hello_fresh, name="Groceries")
