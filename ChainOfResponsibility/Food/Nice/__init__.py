# Project imports
from ...Base import DescAmount


handler = DescAmount([
    "Applebees",
    "Asian Chao",
    "Blaze Pizza",
    "Chipotle",
    "Grubhub",
    "Jimmy Johns",
    "Mod pizza",
    "Old Nelson Food",
    "Pizza Wings Steaks",
    "Village Cafe",
    "Wawa",
], 0, 30)

if __name__ == "__main__":
    handler.print_alpha()
