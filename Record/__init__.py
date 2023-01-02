class Record:
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
