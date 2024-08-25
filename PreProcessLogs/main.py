"""
Handle original/override/final Log logic
"""

# General imports
from copy import deepcopy

# Typing
Item = dict[str, dict[str, str]]


def pre_process(data: list[Item]):
    """Handle override logic: Combines Imported and Override fields to create the Final fields"""
    ret: list[Item] = deepcopy(data)
    for item in ret:
        final = item['Final'] = {}
        for key, override in item['Override'].items():
            final[key] = override if override else item['Imported'][key]
    return ret
