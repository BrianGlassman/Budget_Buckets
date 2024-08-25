# General imports
from copy import deepcopy
import csv

# Project imports
from BaseLib.CategoryList import categories
from BaseLib.utils import safe_open
from BaseLib.money import Money

# Typing
Item = dict[str, dict[str, str]]


with safe_open('Rules.csv', 'r', errors='ignore') as f:
    # FIXME some lines apparently have non-utf-8 bytes, but I can't find which characters. So just ignore and hope it works
    rules = list(csv.DictReader(f))
for rule in rules:
    # Use Money objects
    rule['Amount'] = Money.from_dollars(rule['Amount'])
    # Enforce consistent category capitalization
    rule_cat: str = rule['My Category']
    for real_cat in categories:
        if rule_cat.lower() == real_cat.lower() and rule_cat != real_cat:
            # Same category, just wrong capitalization
            rule['My Category'] = real_cat
            break

input_keys = ["Date", "Description", "Original Description", "Category", "Amount", "Status"]
output_keys = ["My Category", "Comment"]

def categorize(data: list[Item]):
    """Handle categorization logic"""
    # FIXME this is ridiculously inefficient
    ret: list[Item] = deepcopy(data)
    for item in ret:
        final = item['Final']
        for rule in rules:
            if all(final[key] == rule[key] for key in input_keys):
                for key in output_keys:
                    assert key not in final

                    item[key] = {key: rule[key]} # type: ignore
                
                
                # FIXME this block is kind of hacky
                key = 'E'
                e = '.' if (item['My Category']['My Category'] in categories) else 'E'
                if e == 'E': print("FOUND ERROR ITEM:\n" + str(item))
                assert e == rule[key]
                item[key] = {key: e} # type: ignore
                break
        else:
            raise ValueError(f"No rule matched for:\n{final}")
    return ret
