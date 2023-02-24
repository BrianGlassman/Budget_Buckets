import os as _imported_os
import re as _imported_re
import json as _imported_json
from functools import partial
from _collections_abc import Iterable as _imported_Iterable
from _collections_abc import Mapping as _imported_Mapping

if __name__ == "__main__":
    import sys
    path = _imported_os.path.dirname(__file__)
    path = _imported_os.path.dirname(path)
    sys.path.append(path)

from Root import Constants as _imported_Constants
from Root.Buckets import categories as _imported_categories

auto_templates_file = _imported_Constants.AutoTemplates_file # Store for writing to later
if not auto_templates_file.startswith("Categorize"):
    auto_templates_file = _imported_os.path.join("Categorize", auto_templates_file)

class Template:
    """Functions like a dictionary"""
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
    
    def run_create(self, rawRecord):
        """Create the Records specified by the create list, using the given Record as a base"""
        from dateutil import parser as dateParser
        import Record
        # TODO should have some info tracking the original source (in source_specific?)
        ret = []
        for create in self.create:
            # Account
            account = create['account']

            # Date
            date = create['date']
            if date == "$SAME":
                date = rawRecord.date
            else:
                date = dateParser.parse(create['date']).date()
            
            # Description
            desc = create['desc']

            # Value
            value = create['value']
            if value == "$SAME":
                value = rawRecord.value
            elif value == "$NEG":
                value = -rawRecord.value
            else:
                pass # Decoder does conversion already

            # Category
            category = create['category']

            # Comment
            comment = create.get('comment', None)

            # Duration
            duration = create.get('duration', 1)

            ct = Record.CategorizedRecord(account, date, desc, value, category=category, comment=comment, duration=duration)
            ret.append(ct)
        return ret

class TemplateGroup(_imported_Iterable):
    """Functions like a list of Templates"""
    name: str
    templates: list[Template]
    def __init__(self, name: str, templates: list[Template] = []) -> None:
        super().__init__()
        self.name = name
        # Avoid stupid Python reference shenanigans
        self.templates = templates if templates else []
    
    def append(self, t: Template):
        self.templates.append(t)
    
    def __iter__(self):
        return self.templates.__iter__()

class TemplateSuperGroup(_imported_Mapping):
    """Functions like a dict of TemplateGroups"""
    name: str
    g_dict: dict[str, TemplateGroup]
    def __init__(self, name: str, groups: dict[str, TemplateGroup] = {}) -> None:
        super().__init__()
        self.name = name
        # Avoid stupid Python reference shenanigans
        self.g_dict = groups if groups else {}
    
    @property
    def groups(self) -> list[TemplateGroup]:
        return list(self.g_dict.values())
    
    def __getitem__(self, __key: str) -> TemplateGroup:
        return self.g_dict.__getitem__(__key)
    
    def __setitem__(self, __key: str, __value: TemplateGroup) -> None:
        return self.g_dict.__setitem__(__key, __value)

    def __iter__(self):
        return self.g_dict.__iter__()
    
    def __len__(self) -> int:
        return self.g_dict.__len__()

class AllTemplates(_imported_Mapping):
    """Functions like a dict of TemplateSuperGroups"""
    sg_dict: dict[str, TemplateSuperGroup]
    # The TemplateGroup of auto-generated templates (which gets saved to when templates are added)
    auto_templates: TemplateGroup | None
    def __init__(self, superGroups: dict[str, TemplateSuperGroup] = {}) -> None:
        super().__init__()
        # Avoid stupid Python reference shenanigans
        self.sg_dict = superGroups if superGroups else {}

        self.auto_templates = None
    
    @property
    def superGroups(self) -> list[TemplateSuperGroup]:
        return list(self.sg_dict.values())
    
    def __getitem__(self, __key: str) -> TemplateSuperGroup:
        return self.sg_dict.__getitem__(__key)
    
    def __setitem__(self, __key: str, __value: TemplateSuperGroup) -> None:
        return self.sg_dict.__setitem__(__key, __value)

    def __iter__(self):
        return self.sg_dict.__iter__()
    
    def __len__(self) -> int:
        return self.sg_dict.__len__()
    
    def update(self, *args, **kwargs) -> None:
        return self.sg_dict.update(*args, **kwargs)
    
    def _set_auto_templates(self, superGroup: str, group: str):
        """Set the pointer so that templates can be added or saved
        Has to be called after the appropriate file is loaded so that the target exists"""
        target = self[superGroup][group]
        assert isinstance(target, TemplateGroup)
        self.auto_templates = target
        return target
    def set_auto_templates(self):
        """TEMPORARY convenience function to make sure the shortcut is set before use"""
        self._set_auto_templates('Auto-generated', 'Individual')    

    def add_auto_template(self, name: str, pattern: dict, new: dict):
        """Add an auto-generated template"""
        self.set_auto_templates()
        assert self.auto_templates is not None

        # Type checking
        assert isinstance(name, str)
        assert isinstance(pattern, dict)
        assert isinstance(new, dict)

        # Category verification (must be a real category)
        if 'category' in new:
            assert new['category'] in _imported_categories, "Category '" + new['category'] + "' not found"

        template = Template(name=name, pattern=pattern, new=new)
        self.auto_templates.append(template)

    def save_auto_templates(self):
        self.set_auto_templates()
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
                elif isinstance(obj, TemplateGroup):
                    return obj.templates
                elif isinstance(obj, TemplateSuperGroup):
                    return obj.g_dict
                elif isinstance(obj, AllTemplates):
                    return obj.sg_dict
                else:
                    # Let the base class default method raise the TypeError
                    return super().default(obj)

        output = {'Auto-generated': {'Individual': self.auto_templates}}
        with open(auto_templates_file, 'w') as f:
            _imported_json.dump(output, f, indent=2, cls=Encoder)
        

    def load_templates_file(self, file: str) -> None:
        """Loads templates from a file and adds them to the tracker"""
        if not _imported_os.path.exists(file):
            print("Can't find template file, skipping:")
            print("\t" + file)
            return None
        
        try:
            with open(file, 'r') as f:
                raw_templates = _imported_json.load(f, object_hook=_as_regex)
        except _imported_json.decoder.JSONDecodeError:
            print(f"Failed to decode template file {file}")
            raise

        # Remove the schema specification
        if '$schema' in raw_templates:
            raw_templates.pop('$schema')

        raw_templates: dict[str, dict[str, list[dict]]]
        # Convert lowest level of nested dicts to Template
        for sg_name, raw_sg in raw_templates.items():
            assert sg_name not in self, f"Duplicate super group name: {sg_name}"
            super_group = self[sg_name] = TemplateSuperGroup(name=sg_name)
            for g_name, raw_g in raw_sg.items():
                assert isinstance(raw_g, list)
                assert g_name not in self, f"Duplicate group name: {g_name}"
                g_templates = [Template(**raw_g[i]) for i in range(len(raw_g))]
                group = TemplateGroup(name=g_name, templates=g_templates)
                super_group[g_name] = group
            
    def flattened(self, item=None) -> list[Template]:
        """Templates file is nested to help with organization
        Return a flattened list of Templates, which is more directly useful"""
        try:
            if item is None:
                ret = []
                for superGroup in self.superGroups:
                    ret.extend(self.flattened(superGroup))
                return ret
            elif isinstance(item, TemplateSuperGroup):
                ret = []
                for group in item.groups:
                    ret.extend(self.flattened(group))
                return ret
            elif isinstance(item, TemplateGroup):
                return item.templates
            else:
                raise NotImplementedError(f"Unknown type {type(item)}")
        except Exception:
            print("Failed: " + str(item))
            raise

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

# Load templates
_nested_templates = AllTemplates()
for templates_file in [
    _imported_Constants.Templates_file, # Generic templates
    _imported_Constants.ManualAccountHandling_file,
    auto_templates_file, # Auto-generated templates from GUI, override anything else
    ]:
    _nested_templates.load_templates_file(templates_file)
_templates = _nested_templates.flattened()

def add_template(name: str, pattern: dict, new: dict) -> None:
    _nested_templates.add_auto_template(name=name, pattern=pattern, new=new)

def save_templates() -> None:
    _nested_templates.save_auto_templates()

def run(transactions: list, limit: int = -1, use_uncat = True, use_cat = True, use_internal = True) -> list:
    import Record
    from Root import Buckets
    categorized_transactions: list[Record.CategorizedRecord] = []
    limited = False
    for rawRecord in transactions:
        match = match_templates(rawRecord)
        if match is None:
            # No match, fill in with placeholder values
            if use_uncat:
                category = Buckets.todo_category
                comment = None
                duration = 1
                ct = Record.CategorizedRecord.from_RawRecord(rawRecord, category, comment=comment, duration=duration)
            else:
                continue
        else:
            # Found a match, fill in the templated values
            new = match.new

            category = new['category']
            if category == Buckets.del_category:
                # "Delete" this transaction by not adding it to the output list
                # FIXME probably cases where this causes the wrong control flow
                continue
            assert category in Buckets.categories, f"Bad category: {category}"
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

            categorized_transactions.extend(match.run_create(rawRecord=rawRecord))
        categorized_transactions.append(ct)

        if limit>0 and len(categorized_transactions) >= limit: # Use >= in case creations overshoot the limit
            limited = True
            break
    
    if not limited:
        # Can't checksum with partial data
        internal_sum = sum(x.value for x in categorized_transactions if x.category in Buckets.internal_categories)
        if abs(internal_sum) >= 0.01:
            import warnings
            warnings.warn(f"Internals ({', '.join(Buckets.internal_categories)}) unbalanced by ${internal_sum:0,.2f}")
    
    if not use_internal:
        # Remove the internal transactions
        categorized_transactions = [x for x in categorized_transactions if x.category not in Buckets.internal_categories]

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

