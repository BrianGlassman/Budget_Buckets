import re as _imported_re
import json as _imported_json

#TODO validate field names against the appropriate data structures somehow

# Regex notes:
#   \*{11} matches exactly 11 asterisks

# TODO add entries for other pay rates at Leonardo, with dates

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
    """Assumes that pattern contains a value field"""
    mask = pattern['value']
    if isinstance(mask, (int, float)):
        # Exact value matching
        return self.value == mask
    else:
        # Range matching
        assert len(mask) == 2
        assert mask[0] < mask[1]
        return mask[0] <= record.value <= mask[1]

# Mapping from field name to helper function
_checker = {'desc': __check_desc,
            'value': __check_value,
            }

def match_templates(record):
    """Check against the common templates. Return whichever template
    matches, or None if no match"""

    matched = None
    # Check the transaction against all templates in order
    for template in templates:
        pattern = template['pattern']
        match = True
        # Run the checker for each field that has a pattern, break if any fail
        for key in pattern:
            if not _checker[key](record, pattern):
                match = False
                break

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
templates = []
def _flatten(dct: dict) -> None:
    if isinstance(dct, list):
        for v in dct:
            _flatten(v)
    elif all(k in dct for k in ('name', 'pattern', 'new')):
        # Found a template, add it
        templates.append(dct)
    else:
        # Recurse
        for v in dct.values():
            _flatten(v)
_flatten(_nested_templates)

# For writing to file
if False:
    class _RegexEncoder(_imported_json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, _imported_re.Pattern):
                return _re_prefix + obj.pattern
            else:
                # Let the base class default method raise the TypeError
                return super().default(obj)

    with open(templates_file, 'w') as f:
        _imported_json.json.dump(templates, f, indent=2, cls=_RegexEncoder)