import json


symbol = '$' # Prefix indicating a Money type
class Money:
    """Avoid floating point problems when doing math with money"""
    value: int
    "Total number of cents"

    def __init__(self, dollars: str|int|float, cents: str|int|float):
        if isinstance(dollars, str):
            dollars = float(dollars)
        if isinstance(dollars, float):
            assert dollars % 1 == 0, "Should be a whole number of dollars, or use from_dollars"
            dollars = int(dollars)
        
        if isinstance(cents, str):
            cents = float(cents)
        if isinstance(cents, float):
            assert cents % 1 == 0, "Should be a whole number of cents"
            cents = int(cents)

        assert isinstance(dollars, int)
        assert isinstance(cents, int)
        self.value = dollars * 100 + cents
    
    @classmethod
    def from_dollars(cls, dollars: str|int|float):
        if isinstance(dollars, str):
            dollars = float(dollars)
        if isinstance(dollars, int):
            # Integer dollars, no cents
            return cls(dollars=dollars, cents=0)
        
        assert isinstance(dollars, float)
        value = round(dollars * 100, 0)
        dollars, cents = divmod(value, 100)
        return cls(dollars=dollars, cents=cents)
    
    @classmethod
    def from_cents(cls, cents: str|int):
        if isinstance(cents, str):
            cents = int(cents)
        
        assert isinstance(cents, int)
        return cls(dollars=0, cents=cents)
    
    def to_dollars(self):
        return round(self.value / 100, 2)
    
    # Math operators (binary)
    def _prep(self, value):
        """Ensure value is a Money object (convert if zero)"""
        if isinstance(value, Money):
            return value
        elif value == 0:
            return Money(0, 0)
        else:
            raise TypeError("Can only operate on another Money object")
    def __add__(self, value):
        value = self._prep(value)
        return Money.from_cents(self.value + value.value)
    __radd__ = __add__
    def __sub__(self, value):
        value = self._prep(value)
        return Money.from_cents(self.value - value.value)
    def __truediv__(self, value) -> float:
        value = self._prep(value)
        return self.value / value.value
    def __mul__(self, value) -> int:
        value = self._prep(value)
        return self.value * value.value
    # Math operators (unary)
    def __neg__(self):
        return Money.from_cents(-self.value)
    
    # Comparison operators
    def __lt__(self, value) -> bool:
        value = self._prep(value)
        return self.value.__lt__(value.value)
    def __eq__(self, value: object) -> bool:
        value = self._prep(value)
        return self.value.__eq__(value.value)

    def pretty_str(self):
        """Copy Excel's money formatting (assuming symbol='$')"""
        return f"{symbol}{self.to_dollars():,.2f}".replace(f'{symbol}-', f'-{symbol}')
    to_excel_format = pretty_str
    __str__ = pretty_str
    def __repr__(self) -> str:
        return f"<Money {str(self)}>"


class MoneyEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Money):
            return o.pretty_str()
        return super().default(o)


class MoneyDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        assert 'object_pairs_hook' not in kwargs
        super().__init__(object_pairs_hook=self.object_pairs_hook, *args, **kwargs)
    def object_pairs_hook(self, dct) -> dict:
        # Use object_pairs_hook instead of object_hook in case there are repeat keys
        # Example: [('Date', '12/30/2023'), ('Description', 'USAA Credit Card'), ('Original Description', 'USAA CREDIT CARD PAYMENT SAN ANTONIO  TX'), ('Category', 'Transfer'), ('Amount', '82379.00'), ('Status', 'Posted')]
        ret = []
        for key, value in dct:
            if isinstance(value, str) and (value.startswith(symbol) or value.startswith(f'-{symbol}')):
                value = value.replace(symbol, '').replace(',', '')
                value = Money.from_dollars(dollars=value)
            ret.append((key, value))
        return dict(ret)
