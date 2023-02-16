import os as _imported_os
import re as _imported_re
import json as _imported_json
from functools import partial

if __name__ == "__main__":
    import sys
    path = _imported_os.path.dirname(__file__)
    path = _imported_os.path.dirname(path)
    sys.path.append(path)

from Root.Constants import categories as _imported_categories

class Template:
    name: str
    pattern: dict
    new: dict
    create: list[dict]
    def __init__(self, name: str, pattern: dict, new: dict, create=[]):
        self.name = name
        self.pattern = pattern
        self.new = new
        self.create = create

    def as_dict(self):
        ret = {
            'name': self.name,
            'pattern': self.pattern,
            'new': self.new}
        # Only include a "create" entry if it's relevant
        # This mimics the old dictionary behavior
        if self.create:
            ret['create'] = self.create
        return ret
    
    def __str__(self) -> str:
        return f"Template<{self.as_dict()}>"

    def __repr__(self) -> str:
        return str(self)
    

#TODO validate field names against the appropriate data structures somehow

# Regex notes:
#   \*{11} matches exactly 11 asterisks

# TODO add entries for other pay rates at Leonardo, with dates

# Helper functions to check different fields
def __desc_helper(mask: _imported_re.Pattern | str, desc: str) -> bool:
    if isinstance(mask, _imported_re.Pattern):
        # Regex matching (search returns None if no match found)
        return mask.search(desc) is not None
    elif isinstance(mask, str):
        # Exact string matching
        return desc == mask
    else:
        raise NotImplementedError("Unknown mask type")
def __check_desc(record, pattern) -> bool:
    """Assumes that pattern contains a desc field"""
    mask = pattern['desc']
    desc = record.desc
    if isinstance(mask, list):
        # List of patterns
        return any(__desc_helper(m, desc) for m in mask)
    else:
        return __desc_helper(mask, desc)
            
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
def __check_date(record, pattern) -> bool:
    """Assumes that pattern contans a date field
    Handles datetime.date vs string by just converting everything to string"""
    mask = pattern['date']
    assert isinstance(mask, str)
    date = str(record.date)
    return date == mask

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
            'date': __check_date,
            }
for key in ('account', 'date', 'desc', 'value', 'source_specific', 'category'):
    _checker.setdefault(key, partial(__check_generic, key=key))

def match_templates(record) -> Template | None:
    """Check against the common templates. Return whichever template
    matches, or None if no match"""

    try:
        matched = None
        # Check the transaction against all templates in order
        for template in _templates:
            pattern = template.pattern
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
    except Exception:
        print(r" \/ \/ \/ FAILED RECORD \/ \/ \/ ")
        print(record)
        print(r" /\ /\ /\ FAILED RECORD /\ /\ /\ ")
        raise
    return matched

_re_prefix = 'REGEX:'

# Specialized encoding/decoding https://docs.python.org/3/library/json.html
def _as_regex(dct):
    """Used when loading the JSON from file"""
    if 'desc' in dct and isinstance(dct['desc'], str) and dct['desc'].startswith(_re_prefix):
        # Convert it back into a compiled regex
        pattern = dct['desc'].replace(_re_prefix, '')
        assert not pattern.startswith(' '), f"Template {dct} probably shouldn't have a space after 'REGEX:'"
        dct['desc'] = _imported_re.compile(pattern)
        return dct
    else:
        # Normal processing
        return dct

def load_templates(file: str) -> dict[str, dict]:
    if not file.startswith("Categorize"):
        file = _imported_os.path.join("Categorize", file)
    if not _imported_os.path.exists(file):
        print("Can't find template file, skipping:")
        print("\t" + file)
        return {}
    
    try:
        with open(file, 'r') as f:
            templates = _imported_json.load(f, object_hook=_as_regex)
    except _imported_json.decoder.JSONDecodeError:
        print(f"Failed to decode template file {file}")
        raise

    # Remove the schema specification
    if '$schema' in templates:
        templates.pop('$schema')

    # Convert lowest level of nested dicts to Template
    for sg in templates.values():
        for group in sg.values():
            assert isinstance(group, list)
            for i in range(len(group)):
                group[i] = Template(**group[i])
    return templates

# Load templates
auto_templates_file = "AutoTemplates.json" # Store for writing to later
if not auto_templates_file.startswith("Categorize"):
    auto_templates_file = _imported_os.path.join("Categorize", auto_templates_file)
    
_nested_templates = {}
for templates_file in [
    "Templates.json", # Generic templates
    "ManualAccountHandling.json",
    auto_templates_file, # Auto-generated templates from GUI, override anything else
    ]:
    _nested_templates.update(load_templates(templates_file))

# Templates file is nested to help with organization, flatten it to be directly useful
_templates: list[Template] = []
def _flatten(dct: dict) -> None:
    try:
        if isinstance(dct, list):
            # Recurse into Array
            for v in dct:
                _flatten(v)
        elif isinstance(dct, Template):
            # Found a template, add it
            _templates.append(dct)
        else:
            # Recurse into Object
            for k,v in dct.items():
                _flatten(v)
    except Exception:
        print("Failed:" + str(dct))
        raise
_flatten(_nested_templates)

_added_templates = load_templates(auto_templates_file)
_addTemp_shortcut = _added_templates['Auto-generated']['Individual']
def add_template(group: list[str], name: str, pattern: dict, new: dict) -> None:
    assert isinstance(group, list)
    assert all(isinstance(g, str) for g in group)
    assert isinstance(name, str)
    assert isinstance(pattern, dict)
    assert isinstance(new, dict)
    if 'category' in new:
        assert new['category'] in _imported_categories, "Category '" + new['category'] + "' not found"

    template = Template(name=name, pattern=pattern, new=new)
    # Drill down to the right group
    foo = _nested_templates
    try:
        for g in group:
            foo = foo[g]
    except Exception:
        raise ValueError(f"Group '{group}' not found")
    foo.append(template) # type: ignore
    _templates.append(template)
    _addTemp_shortcut.append(template)

def save_templates() -> None:
    class Encoder(_imported_json.JSONEncoder):
        """Used when saving to JSON file"""
        def default(self, obj):
            import datetime
            if isinstance(obj, _imported_re.Pattern):
                return _re_prefix + obj.pattern
            elif isinstance(obj, datetime.date):
                return str(obj)
            elif isinstance(obj, Template):
                return obj.as_dict()
            else:
                # Let the base class default method raise the TypeError
                return super().default(obj)

    with open(auto_templates_file, 'w') as f:
        _imported_json.dump(_added_templates, f, indent=2, cls=Encoder)

def _create_from_template(create: dict, rawRecord):
    """Used to create a Record for elements in Template.create"""
    from dateutil import parser as dateParser
    import Record
    # TODO should have some info tracking the original source (in source_specific?)

    account = create['account']

    date = create['date']
    if date == "$SAME":
        date = rawRecord.date
    else:
        date = dateParser.parse(create['date']).date()
    
    desc = create['desc']

    value = create['value']
    if value == "$SAME":
        value = rawRecord.value
    elif value == "$NEG":
        value = -rawRecord.value
    else:
        pass # Decoder does conversion already

    category = create['category']

    comment = create.get('comment', None)

    duration = create.get('duration', 1)

    ct = Record.CategorizedRecord(account, date, desc, value, category=category, comment=comment, duration=duration)
    return ct

def run(transactions: list, limit: int = -1, use_uncat = True, use_cat = True, use_internal = True) -> list:
    import Record
    from Root import Constants
    categorized_transactions: list[Record.CategorizedRecord] = []
    limited = False
    for rawRecord in transactions:
        match = match_templates(rawRecord)
        if match is None:
            # No match, fill in with placeholder values
            if use_uncat:
                category = Constants.todo_category
                comment = None
                duration = 1
                ct = Record.CategorizedRecord.from_RawRecord(rawRecord, category, comment=comment, duration=duration)
            else:
                continue
        else:
            # Found a match, fill in the templated values
            new = match.new
            create = match.create

            category = new['category']
            if category == Constants.del_category:
                # "Delete" this transaction by not adding it to the output list
                # FIXME probably cases where this causes the wrong control flow
                continue
            assert category in Constants.categories, f"Bad category: {category}"
            if not use_cat:
                # FIXME probably cases where this causes the wrong control flow
                continue
            comment = new.get('comment', None)
            duration = new.get('duration', 1)
            ct = Record.CategorizedRecord.from_RawRecord(rawRecord, category, comment=comment, duration=duration)

            # Update using whatever was in the pattern
            for key, val in new.items():
                # Skip keys that have already been handled
                if key in ('category', 'comment', 'duration'):
                    continue
                ct[key] = val

            for c in create:
                categorized_transactions.append(_create_from_template(c, rawRecord))
        categorized_transactions.append(ct)

        if limit>0 and len(categorized_transactions) >= limit: # Use >= in case creations overshoot the limit
            limited = True
            break
    
    if not limited:
        # Can't checksum with partial data
        internal_sum = sum(x.value for x in categorized_transactions if x.category in Constants.internal_categories)
        if abs(internal_sum) >= 0.01:
            import warnings
            warnings.warn(f"Internals ({', '.join(Constants.internal_categories)}) unbalanced by ${internal_sum:0,.2f}")
    
    if not use_internal:
        # Remove the internal transactions
        categorized_transactions = [x for x in categorized_transactions if x.category not in Constants.internal_categories]

    # Easy way to filter stuff
    categorized_transactions = [x for x in categorized_transactions if
        True
        ]

    assert len(categorized_transactions) > 0

    return categorized_transactions

if __name__ == "__main__":
    import Record
    import Parsing

    transactions: list[Record.RawRecord]
    transactions = Parsing.run()

    categorized_transactions = run(transactions=transactions, 
        limit=0, use_uncat=True, use_cat=True, use_internal=True)

