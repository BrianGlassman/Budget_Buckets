# Project imports
from ...Base import HandlerChain, DescAmount


restaurants = HandlerChain(
    DescAmount([ # Expensive
        "Cosmos Pizza",
        "Domino's",
        "Panera Bread",
    ], 15, 60),
    DescAmount([ # Normal
        "Applebees",
        "Asian Chao",
        "BJ's Restaurant",
        "Blaze Pizza",
        "Bovas Market and Grill",
        "Chipotle",
        "Dunkin'",
        "Falafel King",
        "Grubhub",
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
    ], 0, 30)
)

vending_machines = DescAmount("PepsiCo", 0, 4)

handler = HandlerChain(restaurants, vending_machines)
