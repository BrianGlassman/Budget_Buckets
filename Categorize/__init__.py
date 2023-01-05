import re as _imported_re
import json as _imported_json
from functools import partial

#TODO validate field names against the appropriate data structures somehow

# Regex notes:
#   \*{11} matches exactly 11 asterisks

# TODO add entries for other pay rates at Leonardo, with dates

categories = (
    # Car
    'Car - Note',
    'Car/Rental Insurance',
    'Car - Other',
    'Car - Parking Pass', # TODO change to just "Parking" or split pass from incidental. Can't do until after porting over old sheet

    # Education
    'Self-improvement',

    # Entertainment
    'Dates',
    'Entertainment - Other',
    'Games',
    'Going Out',
    'Books',
    'Big Fun',

    # Food
    'Groceries',
    'Food - nice',

    # Housing
    'Rent',
    'Utilities',
    'Internet',
    'Housing - Other',
    'Decoration',

    # Investments/Savings
    '401k',
    'Retirement',
    'Long-term',
    'Unexpected Fund',

    # Medical/Dental
    'Medical - Other',
    'Medical Insurance',

    # Other
    'ATM',
    'Other - Other',

    # Personal Care / Clothing
    'Clothes/Personal care',

    # Income
    'Parental Funds',
    'Loans',
    'Salary',
    'Income - Other',

    # Internal
    'CC Payments',
    'Internal Transfers',
    )

# Helper functions to check different fields
def __check_desc(record, pattern) -> bool:
    """Assumes that pattern contains a desc field"""
    mask = pattern['desc']
    desc = record.desc
    if isinstance(mask, _imported_re.Pattern):
        # Regex matching (None if no match found)
        return mask.search(desc) is not None
    elif isinstance(mask, str):
        # Exact string matching
        return desc == mask
    else:
        raise NotImplementedError("Unknown mask type")
def __check_value(record, pattern) -> bool:
    """Assumes that pattern contains a value field
    Pattern must be a number or range (list of two numbers)
    True if record value matches the number or is within the given range (inclusive)
    """
    mask = pattern['value']
    if isinstance(mask, (int, float)):
        # Exact value matching
        return record.value == mask
    else:
        # Range matching
        assert len(mask) == 2
        assert mask[0] != mask[1]
        return min(mask) <= record.value <= max(mask)

def __check_generic(record, pattern, key) -> bool:
    """record - BaseRecord
    pattern - dict
    """
    value = getattr(record, key)
    mask = pattern[key]
    return value == mask

# Mapping from field name to helper function
_checker = {'desc': __check_desc,
            'value': __check_value,
            }
for key in ('account', 'date', 'desc', 'value', 'source_specific', 'category'):
    _checker.setdefault(key, partial(__check_generic, key=key))

def match_templates(record):
    """Check against the common templates. Return whichever template
    matches, or None if no match"""

    matched = None
    # Check the transaction against all templates in order
    for template in _templates:
        pattern = template['pattern']
        match = True
        # Run the checker for each field that has a pattern, break if any fail
        for key in pattern:
            try:
                checker = _checker[key]
                if not checker(record, pattern):
                    match = False
                    break
            except TypeError:
                val = _checker[key](record, pattern)
                print(val)
                raise

        if match:
            # Template matched, stop searching
            matched = template
            break
    return matched

templates_file = "Categorize/Templates.json"
_re_prefix = 'REGEX:'

# Specialized encoding/decoding https://docs.python.org/3/library/json.html
def _as_regex(dct):
    if 'desc' in dct and dct['desc'].startswith(_re_prefix):
        # Convert it back into a compiled regex
        pattern = dct['desc'].replace(_re_prefix, '')
        dct['desc'] = _imported_re.compile(pattern)
        return dct
    else:
        # Normal processing
        return dct

with open(templates_file, 'r') as f:
    _nested_templates = _imported_json.load(f, object_hook=_as_regex)

# Templates file is nested to help with organization, flatten it to be directly useful
_templates = []
def _flatten(dct: dict) -> None:
    if isinstance(dct, list):
        for v in dct:
            _flatten(v)
    elif all(k in dct for k in ('name', 'pattern', 'new')):
        # Found a template, add it
        _templates.append(dct)
    else:
        # Recurse
        for v in dct.values():
            _flatten(v)
_flatten(_nested_templates)

def add_template(group, name, pattern, new):
    assert isinstance(group, str)
    assert group in _nested_templates, f"Group '{group}' not found"
    assert isinstance(name, str)
    assert isinstance(pattern, dict)
    assert isinstance(new, dict)
    if 'category' in new:
        assert new['category'] in categories

    template = {'name': name, 'pattern': pattern, 'new': new}
    _nested_templates[group].append(template)
    _templates.append(template)

def save_templates():
    class _RegexEncoder(_imported_json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, _imported_re.Pattern):
                return _re_prefix + obj.pattern
            else:
                # Let the base class default method raise the TypeError
                return super().default(obj)

    with open(templates_file, 'w') as f:
        _imported_json.dump(_nested_templates, f, indent=2, cls=_RegexEncoder)