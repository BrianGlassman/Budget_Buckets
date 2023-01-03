class BaseRecord:
    def __init__(self, account: str, date: str, desc: str, amt: float, source_specific = {}):
        assert isinstance(account, str)
        self.account = account
        assert isinstance(date, str)
        self.date = date
        assert isinstance(desc, str)
        self.desc = desc
        assert isinstance(amt, float)
        self.amt = amt
        assert isinstance(source_specific, dict)
        self.source_specific = source_specific
        
    def values(self):
        return [self.account, self.date, self.desc, self.amt, self.source_specific]

class RawRecord(BaseRecord):
    """A record (mostly) as read-in from the source data, with minimal processing and no categorization"""
    pass

class CategorizedRecord(BaseRecord):
    """A record that has been categorized"""
    def __init__(self, baseRecord: BaseRecord, category: str):
        self.account = baseRecord.account
        self.date = baseRecord.date
        self.desc = baseRecord.desc
        self.amt = baseRecord.amt
        self.source_specific = baseRecord.source_specific

        assert isinstance(category, str)
        self.category = category

    def values(self):
        return super().values() + [self.category]
