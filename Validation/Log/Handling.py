# General imports
from copy import deepcopy


# Project imports
from CategoryList import categories


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
            raise ValueError()
    return ret
