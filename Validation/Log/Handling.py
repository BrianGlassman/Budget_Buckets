"""
Process the input data
"""

# General imports
from copy import deepcopy


# Project imports
from BaseLib.CategoryList import categories


# Logging
from BaseLib.logger import delegate_print as print

# Typing
Item = dict[str, dict[str, str]]


def handle(data: list[Item]):
    ret: list[Item] = deepcopy(data)
    for item in ret:
        # Handle override logic
        final = item['Final'] = {}
        for key, override in item['Override'].items():
            final[key] = override if override else item['Imported'][key]

        # Handle error logic
        item['E'] = {
            'E': '.' if (item['My Category']['My Category'] in categories) else 'E'
        }

        if item['E']['E'] == 'E':
            print("FOUND ERROR ITEM:\n" + str(item))
    return ret
