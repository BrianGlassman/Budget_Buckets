# General imports
from abc import ABC as _ABC, abstractmethod as _abstractmethod
import re
from typing import Any as _Any


# Project imports
from Raw_Data.Parsing.USAAChecking.Transaction import Transaction
from Raw_Data.Parsing.USAAChecking.Money import money, make_money


#%% Base Classes ================================
class Handler(_ABC):
    @_abstractmethod
    def handle(self, t: Transaction) -> tuple[bool, _Any]:
        """Returns (handled, result)"""

class HandlerChain(Handler):
    """A chain of handlers, called in order\n
    Is itself a Handler subclass so that chains can be nested"""
    handlers: list[Handler]
    def __init__(self, *handlers: Handler) -> None:
        super().__init__()
        assert all(isinstance(h, Handler) for h in handlers)
        self.handlers = list(handlers)
    
    def handle(self, t: Transaction) -> tuple[bool, _Any]:
        for handler in self.handlers:
            handled, result = handler.handle(t=t)
            if handled:
                return result
        else:
            return False, None

#%% Common Usage ================================

class DescKeywords(Handler):
    """Checks for any of a list of phrases in the description (case insensitive)"""
    keywords: list[str]
    def __init__(self, keywords: list[str] | str) -> None:
        if isinstance(keywords, str):
            keywords = [keywords]
        assert all(isinstance(k, str) for k in keywords)
        self.keywords = keywords

    def handle(self, t: Transaction) -> tuple[bool, _Any]:
        desc = t.desc.lower()
        if any(k.lower() in desc for k in self.keywords):
            return True, None
        else:
            return False, None
    
    def print_alpha(self):
        """Convenience function to print the keywords in alphabetical order, formatte as valid code"""
        keywords = sorted(set(self.keywords))
        # Include the first and last, so can't directly join
        out = [f'    "{k}",' for k in keywords]
        out = '\n'.join(out)
        print(out)

class DescAmount(DescKeywords):
    """Checks for description keyword(s) and an amount within certain limits"""
    # For exact amount, just set both bounds the same
    low: money
    high: money
    def __init__(self, keywords: str | list[str], low: money, high: money, *, income=False) -> None:
        super().__init__(keywords=keywords)

        if income:
            assert low >= 0
            assert high >= 0
        else:
            # Convert positive to negative
            if low >= 0: low = -low
            if high >= 0: high = -high

        # Ensure typing
        if not isinstance(low, money):
            low = make_money(low)
        if not isinstance(high, money):
            high = make_money(high)

        # Ensure bounds are low-->high, even if negative
        if low <= high:
            self.low = low
            self.high = high
        else:
            # Got it backwards (probably negative numbers)
            self.low = high
            self.high = low
    
    def handle(self, t: Transaction) -> tuple[bool, _Any]:
        handled, result = super().handle(t)
        if handled and self.low <= t.amount <= self.high:
            return True, result
        else:
            return False, None

class DescRegex(Handler):
    pattern: str
    def __init__(self, pattern: str) -> None:
        assert isinstance(pattern, str)
        self.pattern = pattern
    
    def handle(self, t: Transaction) -> tuple[bool, _Any]:
        desc = t.desc.lower()
        if re.search(self.pattern, desc):
            return True, None
        else:
            return False, None

class DescRegexAmount(Handler):
    """Checks for description keyword(s) and an amount within certain limits"""
    pattern: str
    # For exact amount, just set both bounds the same
    low: money
    high: money
    def __init__(self, pattern: str, low: money, high: money, *, income=False) -> None:
        assert isinstance(pattern, str)
        self.pattern = pattern

        if income:
            assert low >= 0
            assert high >= 0
        else:
            # Convert positive to negative
            if low >= 0: low = -low
            if high >= 0: high = -high

        # Ensure typing
        if not isinstance(low, money):
            low = make_money(low)
        if not isinstance(high, money):
            high = make_money(high)

        # Ensure bounds are low-->high, even if negative
        if low <= high:
            self.low = low
            self.high = high
        else:
            # Got it backwards (probably negative numbers)
            self.low = high
            self.high = low
    
    def handle(self, t: Transaction) -> tuple[bool, _Any]:
        desc = t.desc.lower()
        if re.search(self.pattern, desc) and self.low <= t.amount <= self.high:
            return True, None
        else:
            return False, None
