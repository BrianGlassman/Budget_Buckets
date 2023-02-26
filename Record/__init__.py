import datetime
import typing as _import_typing

from Root import Buckets

class Field:
    _type: _import_typing.Type
    def __init__(self, value):
        self.set(value=value)

    def set(self, value):
        self.check_value(value=value)
        self.value = value

    def check_value(self, value):
        """Error if value is invalid"""
        assert isinstance(value, self._type), f"Type is '{type(value)}', not '{self._type}"

class StrField(Field):
    _type = str

class CatField(Field):
    _type = str
    def check_value(self, value):
        assert isinstance(value, self._type), f"Type is '{type(value)}', not '{self._type}"
        assert value in Buckets.categories_inclTodo, f"Category '{value}' not recognized"

class DateField(Field):
    _type = datetime.date

class IntField(Field):
    _type = int

class PosIntField(IntField):
    def check_value(self, value):
        super().check_value(value)
        assert value > 0, f"Value '{value}' must be positive"

class MoneyField(Field):
    _type = float

class DictField(Field):
    _type = dict

class BaseRecord:
    _account: StrField
    _date: DateField
    _desc: StrField
    _value: MoneyField
    _source_specific: DictField
    def __init__(self, account: str, date: datetime.date, desc: str, value: float, source_specific = {}):
        self._account = StrField(account)
        self._date = DateField(date)
        self._desc = StrField(desc)
        self._value = MoneyField(value)
        self._source_specific = DictField(source_specific)

    @property
    def account(self):
        return self._account.value
    @property
    def date(self):
        return self._date.value
    @property
    def desc(self):
        return self._desc.value
    @property
    def value(self):
        return self._value.value
    @property
    def source_specific(self):
        return self._source_specific.value

    @account.setter
    def account(self, value):
        return self._account.set(value)
    @date.setter
    def date(self, value):
        return self._date.set(value)
    @desc.setter
    def desc(self, value):
        return self._desc.set(value)
    @value.setter
    def value(self, value):
        return self._value.set(value)
    @source_specific.setter
    def source_specific(self, value):
        return self._source_specific.set(value)

    def __getitem__(self, key):
        if key == 'account': return self.account
        elif key == 'date':  return self.date
        elif key == 'desc':  return self.desc
        elif key == 'value': return self.value
        elif key == 'source_specific': return self.source_specific
        else:
            raise KeyError()
    
    def __setitem__(self, key, item):
        if key == 'account': self.account = item
        elif key == 'date':  self.date = item
        elif key == 'desc':  self.desc = item
        elif key == 'value': self.value = item
        elif key == 'source_specific': self.source_specific = item
        else:
            raise KeyError()
        
    def values(self) -> list[str | datetime.date | float | dict]:
        return [self.account, self.date, self.desc, self.value, self.source_specific]

    @classmethod
    def keys(cls):
        return ['account', 'date', 'desc', 'value', 'source_specific']
    
    def fields(self) -> list[Field]:
        return [self._account, self._date, self._desc, self._value, self._source_specific]
    
    @classmethod
    def class_fields(cls):
        return [StrField, DateField, StrField, MoneyField, DictField]

    @classmethod
    def class_items(cls):
        return zip(cls.keys(), cls.class_fields())

    def items(self) -> dict:
        return {k:v for k,v in zip(self.keys(), self.values())}

    def __str__(self) -> str:
        return str(self.values())
    def __repr__(self) -> str:
        return str(self)

class RawRecord(BaseRecord):
    """A record (mostly) unchanged from the source data, with minimal processing and no categorization"""
    pass

class CategorizedRecord(BaseRecord):
    """A record that has been categorized"""
    def __init__(self, account: str, date: datetime.date, desc: str, value: float, source_specific={},
                 category: str = Buckets.todo_category, comment: str = '', rawRecord: RawRecord | None = None,
                 duration: int = 1):
        super().__init__(account, date, desc, value, source_specific)
        assert rawRecord is None or isinstance(rawRecord, RawRecord)
        self.rawRecord = rawRecord

        self._category = CatField(category)

        self._comment = StrField(comment)

        self._duration = PosIntField(duration)

    @property
    def category(self):
        return self._category.value
    @property
    def comment(self):
        return self._comment.value
    @property
    def duration(self):
        return self._duration.value

    @category.setter
    def category(self, value):
        return self._category.set(value)
    @comment.setter
    def comment(self, value):
        return self._comment.set(value)
    @duration.setter
    def duration(self, value):
        return self._duration.set(value)

    @classmethod
    def from_RawRecord(cls, rawRecord: RawRecord, category: str, comment: str = '', duration: int = 1):
        assert isinstance(rawRecord, RawRecord)
        return cls(rawRecord.account, rawRecord.date, rawRecord.desc, rawRecord.value, rawRecord.source_specific,
                   category, comment, rawRecord, duration)

    def values(self):
        return super().values() + [self.category, self.comment, self.duration]

    @classmethod
    def keys(cls):
        return super().keys() + ['category', 'comment', 'duration']

    def fields(self):
        return super().fields() + [self._category, self._comment, self._duration]

    @classmethod
    def class_fields(cls):
        return super().class_fields() + [CatField, StrField, PosIntField]
