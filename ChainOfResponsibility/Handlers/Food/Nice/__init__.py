# Project imports
from ....Base import HandlerChain, DescAmount


restaurants = HandlerChain(
    DescAmount([
        "Cosmos Pizza",
        "Domino's",
        "Grubhub",
        "Panera Bread",
    ], 10, 60, name="Expensive Restaurants"),
    DescAmount([
        "Applebees",
        "Asian Chao",
        "BJ's Restaurant",
        "Blaze Pizza",
        "Bovas Market and Grill",
        "Chipotle",
        "Dunkin'",
        "Falafel King",
        "Gurkhas On The Hill",
        "Illegal Pete S Hil",
        "Ipie",
        "Jimmy Johns",
        "Mod pizza",
        "Old Nelson Food",
        "Panda Express",
        "Pizza Wings Steaks",
        "Qdoba",
        "Schlotzsky's",
        "Shamane's Bake Shoppe",
        "Smashburger",
        "Snarf's",
        "Square Gravity Espresso",
        "Thai Avenue",
        "Tiffins India Cafe",
        "Torchys Boulder",
        "Village Cafe",
        "Wawa",
        "Zodiac Subs",
    ], 0, 30, name="Normal Restaurants"),
    name="Restaurants"
)

vending_machines = DescAmount("PepsiCo", 0, 4, name="Vending Machines")

handler = HandlerChain(restaurants, vending_machines, name="Nice Food")
