import os as _imported_os
import re as _imported_re
import json as _imported_json
from functools import partial
from _collections_abc import Iterable as _imported_Iterable
from _collections_abc import Mapping as _imported_Mapping
import datetime as _imported_datetime
from typing import Type as _imported_Type

from BaseLib import Constants as _imported_Constants
import BaseLib.Categories as _imported_Categories
import Classes.Record as Record
from Handlers.Categorize import Fields

_re_prefix = 'REGEX:'

auto_templates_file = _imported_Constants.AutoTemplates_file # Store for writing to later

class BasePattern:
    """Functions like a dictionary"""
    def __init__(self, *args, **kwargs):
        """Positional args should be in the same order as field_dict and fieldType_dict
        Keyword kwargs can be in any order"""
        for key, fieldType, arg in zip(self.keys(), self.fieldType_dict().values(), args):
            self._set_field(key, fieldType, arg)
        
        for key, fieldType in self.fieldType_dict().items():
            fieldType = self.fieldType_dict()[key]
            self._set_field(key, fieldType, kwargs.get(key))
    def _set_field(self, key: str, fieldType: _imported_Type[Fields.Field], value):
        try:
            setattr(self, key, fieldType(value))
        except Exception:
            print(f"Failed to set {key} = {fieldType}({value})")
            raise

    @classmethod
    def fieldType_dict(cls) -> dict[str, _imported_Type[Fields.Field]]:
        return {}

    @classmethod
    def keys(cls):
        return cls.fieldType_dict().keys()

    def field_dict(self) -> dict[str, Fields.Field]:
        return {}

    def as_dict(self):
        """Returns the values of all set fields as a dictionary
        Fields that have not been set (or have been cleared) are not included"""
        ret = {}
        for key, target in self.field_dict().items():
            target: Fields.Field
            if target.is_set:
                ret[key] = target.get()
        return ret
    
    def __getitem__(self, key):
        return self.as_dict()[key]
    
    def get(self, key: str, default):
        """Like dict.get, gets the value in the field"""
        return self.as_dict().get(key, default)
    
    def __setitem__(self, key, value):
        field = self.field_dict()[key]
        field.set(value=value)
    
    def try_set(self, key, value) -> bool:
        """Tries to set the value, return True if successful False if failed"""
        field = self.field_dict()[key]
        return field.try_set(value=value)

    def __iter__(self):
        yield from self.as_dict().keys()
    
    def items(self):
        return self.as_dict().items()
    
    def clear(self, key):
        field = self.field_dict()[key]
        field.clear()

class Pattern(BasePattern):
    """The Pattern part of a Template that matches a RawRecord"""
    account: Fields.Account
    date: Fields.Date
    desc: Fields.Desc
    value: Fields.Value
    source_specific: Fields.SourceSpecific
    
    @classmethod
    def fieldType_dict(cls):
        """Maps key to Field type"""
        return {
            'account': Fields.Account,
            'date': Fields.Date,
            'desc': Fields.Desc,
            'value': Fields.Value,
            'source_specific': Fields.SourceSpecific,
        }

    def field_dict(self):
        """Maps key to Field"""
        return {
            'account': self.account,
            'date': self.date,
            'desc': self.desc,
            'value': self.value,
            'source_specific': self.source_specific,
        }

class New(Pattern):
    """The New part of a Template that sets up a CategorizedRecord
    Inherits all the RawRecord stuff from Pattern, so only needs to define the parts
    that are specific to CategorizedRecords"""
    category: Fields.Category
    comment: Fields.Comment
    duration: Fields.Duration
    
    @classmethod
    def fieldType_dict(cls):
        return super().fieldType_dict() | {
            'category': Fields.Category,
            'duration': Fields.Duration,
            'comment': Fields.Comment,
        }

    def field_dict(self):
        return super().field_dict() | {
            'category': self.category,
            'duration': self.duration,
            'comment': self.comment,
        }

class Create(New):
    """One of the Create elements of a Template that creates a new CategorizedRecord
    Functionally similar to New, but some fields have special processing"""
    date: Fields.CreateDate
    value: Fields.CreateValue

    @classmethod
    def fieldType_dict(cls):
        return super().fieldType_dict() | {
            'date': Fields.CreateDate,
            'value': Fields.CreateValue,
        }

class Template:
    """Functions like a dictionary"""
    name: str
    pattern: Pattern
    new: New
    create: list[Create]
    def __init__(self, name: str, pattern: dict, new: dict, create=[]):
        self.name = name
        self.pattern = Pattern(**pattern)
        self.new = New(**new)
        if create:
            self.create = [Create(**c) for c in create]
        else:
            # Avoid stupid Python reference shenanigans
            self.create = []

    @classmethod
    def from_json(cls, dct: dict):
        return cls(**dct)

    def as_dict(self):
        ret = {
            'name': self.name,
            'pattern': self.pattern.as_dict(),
            'new': self.new.as_dict(),
            }
        # Only include a "create" entry if it's relevant
        # This mimics the old dictionary behavior
        if self.create:
            ret['create'] = [c.as_dict() for c in self.create]
        return ret
    
    def __str__(self) -> str:
        return f"Template<{self.as_dict()}>"

    def __repr__(self) -> str:
        return str(self)

    #--------------------------------------------------------------------------
    # Functions to compare different fields against a given Record
    def __desc_helper(self, pattern: str | _imported_re.Pattern, desc: str):
        """Performs the actual check. Functionified for readability"""
        if isinstance(pattern, _imported_re.Pattern):
            # Regex matching (search returns None if no match found)
            return pattern.search(desc) is not None
        elif isinstance(pattern, str):
            # Exact string matching
            return desc == pattern
        else:
            raise NotImplementedError(f"Unknown pattern type {type(pattern)}")
    def match_desc(self, record: Record.BaseRecord) -> bool:
        """True if the record description matches the template"""
        pattern = self.pattern['desc']
        desc = record.desc
        if isinstance(pattern, list):
            # List of patterns, True if record matches any of them
            return any(self.__desc_helper(pattern=p, desc=desc) for p in pattern)
        else:
            return self.__desc_helper(pattern=pattern, desc=desc)
    
    def match_value(self, record: Record.BaseRecord) -> bool:
        """True if the record value matches the template"""
        pattern = self.pattern['value']
        if isinstance(pattern, (int, float)):
            # Exact value matching
            return record.value == pattern
        elif isinstance(pattern, (list, tuple)):
            # Range matching (inclusive, sign-sensitive)
            assert len(pattern) == 2
            assert pattern[0] != pattern[1]
            return min(pattern) <= record.value <= max(pattern)
        else:
            raise NotImplementedError(f"Unknown pattern type {type(pattern)}")
    
    def match_date(self, record: Record.BaseRecord) -> bool:
        """True if record date matches the template"""
        pattern = self.pattern['date']
        assert isinstance(pattern, _imported_datetime.date)
        return pattern == record.date
    
    def match_generic(self, record: Record.BaseRecord, key: str) -> bool:
        """True if record[key] matches template pattern[key]"""
        pattern = self.pattern[key]
        return pattern == getattr(record, key)
    #--------------------------------------------------------------------------

    def run_create(self, rawRecord):
        """Create the Records specified by the create list, using the given Record as a base"""
        from dateutil import parser as dateParser
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
            comment = create.get('comment', '')

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

    @classmethod
    def from_json(cls, name: str, raw_group: list[dict]):
        templates = [Template.from_json(raw_dct) for raw_dct in raw_group]
        return cls(name=name, templates=templates)
    
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

    @classmethod
    def from_json(cls, name: str, raw_sg: dict[str, list[dict]]):
        groups = {name: TemplateGroup.from_json(name, raw_group) for name, raw_group in raw_sg.items()}
        return cls(name=name, groups=groups)
    
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

class TemplateFile(_imported_Mapping):
    """Functions like a dict of TemplateSuperGroups"""
    sg_dict: dict[str, TemplateSuperGroup]
    schema: str | None
    def __init__(self, filepath: str, schema: str | None, superGroups: dict[str, TemplateSuperGroup] = {}) -> None:
        super().__init__()
        self.filepath = filepath
        self.schema = schema
        # Avoid stupid Python reference shenanigans
        self.sg_dict = superGroups if superGroups else {}

    schema_tag = '$schema'
    # Specialized encoding/decoding https://docs.python.org/3/library/json.html
    @classmethod
    def _as_regex(cls, dct):
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
    @classmethod
    def from_json(cls, filepath: str):
        """Loads templates from the given file"""
        if not _imported_os.path.exists(filepath):
            print("Can't find template file, skipping:")
            print("\t" + filepath)
            return None

        try:
            with open(filepath, 'r') as f:
                raw_templates = _imported_json.load(f, object_hook=cls._as_regex)
                raw_templates: dict
        except _imported_json.decoder.JSONDecodeError:
            print(f"Failed to decode template file {filepath}")
            raise

        # Remove the schema specification
        schema: str | None = None
        if cls.schema_tag in raw_templates:
            schema = raw_templates.pop('$schema')

        superGroups = {name: TemplateSuperGroup.from_json(name=name, raw_sg=raw_sg) for name, raw_sg in raw_templates.items()}
        return cls(filepath=filepath, schema=schema, superGroups=superGroups)

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

    def save(self):
        """Save the templates back to the source file"""
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
                elif isinstance(obj, TemplateFile):
                    return obj.sg_dict
                elif isinstance(obj, AllTemplates):
                    return obj.file_dict
                else:
                    # Let the base class default method raise the TypeError
                    return super().default(obj)

        output = {}
        if self.schema is not None:
            output[self.schema_tag] = self.schema
        output.update(self.sg_dict)
        with open(self.filepath, 'w') as f:
            _imported_json.dump(output, f, indent=2, cls=Encoder)

class AllTemplates(_imported_Mapping):
    """Functions like a dict of TemplateFiles"""
    file_dict: dict[str, TemplateFile]
    # The TemplateGroup of auto-generated templates (which gets saved to when templates are added)
    auto_templates: TemplateGroup | None
    auto_file: TemplateFile | None
    def __init__(self, files: dict[str, TemplateFile] = {}) -> None:
        super().__init__()
        # Avoid stupid Python reference shenanigans
        self.file_dict = files if files else {}

        self.auto_file = None
        self.auto_templates = None
    
    @property
    def files(self) -> list[TemplateFile]:
        return list(self.file_dict.values())
    
    def __getitem__(self, __key: str) -> TemplateFile:
        return self.file_dict.__getitem__(__key)
    
    def __setitem__(self, __key: str, __value: TemplateFile) -> None:
        return self.file_dict.__setitem__(__key, __value)

    def __iter__(self):
        return self.file_dict.__iter__()
    
    def __len__(self) -> int:
        return self.file_dict.__len__()
    
    def save(self):
        """Save all children"""
        for file in self.files:
            file.save()
    
    def _set_auto_templates(self, filename:str, superGroup: str, group: str):
        """Set the pointer so that templates can be added or saved
        Has to be called after the appropriate file is loaded so that the target exists"""
        file = self[filename]
        assert isinstance(file, TemplateFile)
        self.auto_file = file
        
        target = file[superGroup][group]
        assert isinstance(target, TemplateGroup)
        self.auto_templates = target
    def set_auto_templates(self):
        """TEMPORARY convenience function to make sure the shortcut is set before use"""
        if self.auto_templates is not None: return
        self._set_auto_templates(auto_templates_file, 'Auto-generated', 'Individual')    

    def add_auto_template(self, name: str, pattern: dict, new: dict):
        """Add an auto-generated template"""
        self.set_auto_templates()
        assert self.auto_templates is not None

        # Type checking
        assert isinstance(name, str)
        assert isinstance(pattern, dict)
        assert isinstance(new, dict)

        # Category verification (must be a real, non-todo category)
        if 'category' in new:
            assert new['category'] in _imported_Categories.categories, "Category '" + new['category'] + "' not found"

        template = Template(name=name, pattern=pattern, new=new)
        self.auto_templates.append(template)

    def save_auto_templates(self):
        """Saves just the auto-generated templates"""
        self.set_auto_templates()
        assert self.auto_file is not None
        self.auto_file.save()
            
    def flattened(self, item=None) -> list[Template]:
        """Templates file is nested to help with organization
        Return a flattened list of Templates, which is more directly useful"""
        try:
            if item is None:
                ret = []
                for file in self.files:
                    ret.extend(self.flattened(file))
                return ret
            elif isinstance(item, TemplateFile):
                ret = []
                for superGroup in item.superGroups:
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

    # Mapping from field name to helper function
    _matcher = {'desc': Template.match_desc,
                'value': Template.match_value,
                'date': Template.match_date,
                }
    for key in ('account', 'date', 'desc', 'value', 'source_specific', 'category'):
        _matcher.setdefault(key, partial(Template.match_generic, key=key))
    
    def match_template(self, record: Record.RawRecord) -> Template | None:
        """Check against the common templates. Return whichever template
        matches, or None if no match"""

        try:
            matched = None
            # Check the transaction against all templates in order
            for template in self.flattened():
                pattern = template.pattern
                match = True
                # Run the checker for each field that has a pattern, break if any fail
                for key in pattern:
                    checker = self._matcher[key]
                    if not checker(self=template, record=record):
                        match = False
                        break

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

#TODO validate field names against the appropriate data structures somehow

# Regex notes:
#   \*{11} matches exactly 11 asterisks

# TODO add entries for other pay rates at Leonardo, with dates

# Load templates
_nested_templates = AllTemplates()
for filepath in [
    _imported_Constants.Templates_file, # Generic templates
    _imported_Constants.ManualAccountHandling_file,
    auto_templates_file, # Auto-generated templates from GUI, override anything else
    ]:
    file_templates = TemplateFile.from_json(filepath)
    assert file_templates is not None
    _nested_templates[filepath] = file_templates

def get_all_templates():
    """Function for the sake of encapsulation (sort of)"""
    return _nested_templates

def match_templates(record) -> Template | None:
    return _nested_templates.match_template(record)

def add_auto_template(name: str, pattern: dict, new: dict) -> None:
    _nested_templates.add_auto_template(name=name, pattern=pattern, new=new)

def save_auto_templates() -> None:
    _nested_templates.save_auto_templates()

def save_all_templates() -> None:
    _nested_templates.save()

def run(transactions: list, limit: int = -1, use_uncat = True, use_cat = True, use_internal = True) -> list:
    categorized_transactions: list[Record.CategorizedRecord] = []
    limited = False
    for rawRecord in transactions:
        match = match_templates(rawRecord)
        if match is None:
            # No match, fill in with placeholder values
            if use_uncat:
                category = _imported_Categories.todo_category
                comment = ''
                duration = 1
                ct = Record.CategorizedRecord.from_RawRecord(rawRecord, category, comment=comment, duration=duration)
            else:
                continue
        else:
            # Found a match, fill in the templated values
            new = match.new

            category = new['category']
            if category == _imported_Categories.del_category:
                # "Delete" this transaction by not adding it to the output list
                # FIXME probably cases where this causes the wrong control flow
                continue
            assert category in _imported_Categories.categories, f"Bad category: {category}"
            if not use_cat:
                # FIXME probably cases where this causes the wrong control flow
                limited = True
                continue
            comment = new.get('comment', '')
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
        internal_sum = sum(x.value for x in categorized_transactions if x.category in _imported_Categories.internal_categories)

        import warnings
        if abs(internal_sum) >= 0.01:
            warnings.warn(f"Internals ({', '.join(_imported_Categories.internal_categories)}) unbalanced by ${internal_sum:0,.2f}")
        else:
            # Use warning anyway so that it only prints once
            warnings.warn(f"(Not actually a warning) Internals ({', '.join(_imported_Categories.internal_categories)}) successfully balanced")
    
    if not use_internal:
        # Remove the internal transactions
        categorized_transactions = [x for x in categorized_transactions if x.category not in _imported_Categories.internal_categories]

    # Easy way to filter stuff
    categorized_transactions = [x for x in categorized_transactions if
        True
        ]

    assert len(categorized_transactions) > 0

    return categorized_transactions

if __name__ == "__main__":
    from Handlers import Parsing

    transactions: list[Record.RawRecord]
    transactions = Parsing.run()

    categorized_transactions = run(transactions=transactions, 
        limit=0, use_uncat=True, use_cat=True, use_internal=True)
