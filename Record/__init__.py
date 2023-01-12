import datetime

from Root import Constants

class BaseRecord:
    def __init__(self, account: str, date: datetime.date, desc: str, value: float, source_specific = {}):
        assert isinstance(account, str), f"Type is '{type(account)}'"
        self.account = account
        assert type(date) is datetime.date, f"Type is '{type(date)}'"
        self.date = date
        assert isinstance(desc, str), f"Type is '{type(desc)}'"
        self.desc = desc
        assert isinstance(value, float), f"Type is '{type(value)}'"
        self.value = value
        assert isinstance(source_specific, dict), f"Type is '{type(source_specific)}'"
        self.source_specific = source_specific
        
    def values(self) -> list[str | datetime.date | float | dict]:
        return [self.account, self.date, self.desc, self.value, self.source_specific]

    def keys(self):
        return ['account', 'date', 'desc', 'value', 'source_specific']

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
                 category: str = Constants.todo_category, comment: str | None = None, rawRecord: RawRecord | None = None):
        super().__init__(account, date, desc, value, source_specific)
        assert rawRecord is None or isinstance(rawRecord, RawRecord)
        self.rawRecord = rawRecord

        assert isinstance(category, str)
        self.category = category

        assert (comment is None) or (isinstance(comment, str))
        self.comment = comment

    @classmethod
    def from_RawRecord(cls, rawRecord: RawRecord, category: str, comment: str | None = None):
        assert isinstance(rawRecord, RawRecord)
        return cls(rawRecord.account, rawRecord.date, rawRecord.desc, rawRecord.value, rawRecord.source_specific,
                   category, comment, rawRecord)

    def values(self):
        return super().values() + [self.category, self.comment]

    def keys(self):
        return super().keys() + ['category', 'comment']
