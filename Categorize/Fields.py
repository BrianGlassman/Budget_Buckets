import datetime
from dateutil import parser as dateParser
from typing import Type as _import_Type

from BaseLib import Accounts, Categories

class Field:
    _type: _import_Type | tuple[_import_Type]
    is_set: bool
    flags: list[str] = [] # Flags that are valid values for special processing
    def __init__(self, value):
        if value is None:
            self.clear()
        else:
            self.set(value=value)
    
    def get(self):
        """Gets the value, returns None if field is not set"""
        if self.is_set:
            return self._value
        else:
            return None

    def set(self, value):
        """Sets the value, if there's a problem error out with the error message(s)"""
        msg = []
        if not self.is_valid(value=value, msg=msg):
            raise ValueError("Failed with message(s):" + '\n'.join(m for m in msg))
        self._value = value
        self.is_set = True
    
    def try_set(self, value) -> bool:
        """Tries to set the value, return True if successful False if failed"""
        try:
            self.set(value)
        except Exception:
            return False
        else:
            return True
    
    def clear(self):
        """Clears the field"""
        self._value = None
        self.is_set = False

    def is_flag(self, value) -> bool:
        return value in self.flags
    
    def is_valid(self, value, msg=None) -> bool:
        """Tells whether value is a valid value for this field
        Pass a list to msg to receive error message(s), if there are any
        Example:
            msg = []
            field.is_valid(bad_value, msg=msg)
            print(msg)
        Will print any error message(s)"""
        valid = True
        if self.is_flag(value):
            return True
        elif not isinstance(value, self._type):
            valid = False
            if msg is not None:
                msg.append(f"Type is '{type(value)}', not '{self._type}")
        return valid

class StrField(Field):
    _type = str
    allowed = []
    def is_valid(self, value, msg=None) -> bool:
        valid = super().is_valid(value=value, msg=msg)
        if self.allowed and (value not in self.allowed):
            valid = False
            if msg is not None:
                msg.append(f"Value '{value}' not in allowed set: {','.join(self.allowed)}")
        return valid

class IntField(Field):
    _type = int

class PosIntField(IntField):
    def is_valid(self, value, msg=None) -> bool:
        valid = super().is_valid(value=value, msg=msg)
        if value <= 0:
            valid = False
            if msg is not None:
                msg.append(f"Value '{value}' must be positive")
        return valid

#%% Meta fields

class Name(StrField):
    pass # No restrictions

#%% RawRecord fields

class Account(StrField):
    allowed = Accounts.accounts

class Date(Field):
    _type = datetime.date
    def set(self, value):
        try:
            value = dateParser.parse(value).date()
        except Exception:
            pass # Let the normal process handle it
        super().set(value=value)

class Desc(StrField):
    def is_valid(self, value, msg=None) -> bool:
        valid = True
        if isinstance(value, str):
            valid = super().is_valid(value, msg=msg)
        elif isinstance(value, (list, tuple)):
            if not all(self.is_valid(v, msg=msg) for v in value):
                valid = False
                if msg is not None:
                    msg.append("Description options must all be valid descriptions")
        return valid

class Value(Field):
    _type = (int, float)
    def set(self, value):
        if isinstance(value, str):
            try:
                # FIXME eval is probably bad
                value = eval(value)
            except Exception:
                pass # Let the normal process handle it
        super().set(value=value)

    def is_valid(self, value, msg=None) -> bool:
        valid = True
        if self.is_flag(value):
            return True
        elif isinstance(value, (int, float)):
            # Can't call super().is_valid because _type isn't defined
            valid = super().is_valid(value=value, msg=msg)
        elif isinstance(value, (list, tuple)):
            if len(value) != 2:
                valid = False
                if msg is not None:
                    msg.append("Value range must be two elements")
            if not all(self.is_valid(v, msg=msg) for v in value):
                valid = False
                if msg is not None:
                    msg.append("Elements of value range must be valid")
        else:
            valid = False
            if msg is not None:
                msg.append("Value must be a number or list of 2 numbers")
        return valid

class SourceSpecific(Field):
    _type = dict
    def set(self, value):
        if isinstance(value, str):
            try:
                # FIXME eval is probably bad
                value = eval(value)
            except Exception:
                pass # Let the normal process handle it
        super().set(value=value)

#%% CategorizedRecord fields

class Category(StrField):
    allowed = Categories.categories

class Comment(StrField):
    pass # No restrictions

class Duration(PosIntField):
    pass # No additional restrictions

#%% Create fields
class CreateDate(Date):
    flags = ['$SAME']

class CreateValue(Value):
    flags = ['$SAME', '$NEG']
