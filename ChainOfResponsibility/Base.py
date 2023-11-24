# General imports
from abc import ABC, abstractmethod
import importlib
import os
import re
from typing import Any


# Project imports
from Raw_Data.Parsing.USAAChecking.Transaction import Transaction
from Raw_Data.Parsing.USAAChecking.Money import money, make_money


#%% Base Classes ================================
class Handler(ABC):
    name: str # An identifier, not guaranteed to be unique
    def __init__(self, name: str) -> None:
        assert isinstance(name, str)
        self.name = name
    
    @abstractmethod
    def handle(self, t: Transaction) -> tuple[bool, Any]:
        """Returns (handled, result)"""

class HandlerChain(Handler):
    """A chain of handlers, called in order\n
    Is itself a Handler subclass so that chains can be nested"""
    handlers: list[Handler]
    def __init__(self, *handlers: Handler, name: str) -> None:
        super().__init__(name=name)
        assert all(isinstance(h, Handler) for h in handlers)
        self.handlers = list(handlers)
    
    @classmethod
    def from_package(cls, file: str, package: str, name: str):
        """Create a HandlerChain from the handler variables in all directories in this package\n
        file: __file__ when calling\n
        package: __package__ when calling"""
        dirname = os.path.dirname(file)
        handlers: list[Handler] = []
        for name in os.listdir(dirname):
            if name == "__pycache__": continue
            if not os.path.isdir(os.path.join(dirname, name)): continue
            try:
                module = importlib.import_module('.'+name, package)
                handler = module.handler
            except Exception as e:
                print(str(e))
            else:
                if not isinstance(handler, Handler): continue
                handlers.append(handler)
        return cls(*handlers, name=name)
        
    def add_handler(self, handler: Handler):
        assert isinstance(handler, Handler)
        self.handlers.append(handler)
    
    def handle(self, t: Transaction) -> tuple[bool, Any]:
        for handler in self.handlers:
            handled, result = handler.handle(t=t)
            if handled:
                return True, result
        else:
            return False, None

#%% Common Usage ================================

class DescKeywords(Handler):
    """Checks for any of a list of phrases in the description (case insensitive)"""
    keywords: list[str]
    def __init__(self, keywords: list[str] | str, name: str) -> None:
        super().__init__(name=name)

        if isinstance(keywords, str):
            keywords = [keywords]
        assert all(isinstance(k, str) for k in keywords)
        self.keywords = keywords

    def handle(self, t: Transaction) -> tuple[bool, Any]:
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
    def __init__(self, keywords: str | list[str], low: money, high: money, *, income=False, name: str) -> None:
        super().__init__(keywords=keywords, name=name)

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
    
    def handle(self, t: Transaction) -> tuple[bool, Any]:
        handled, result = super().handle(t)
        if handled and self.low <= t.amount <= self.high:
            return True, result
        else:
            return False, None

class DescRegex(Handler):
    pattern: str
    def __init__(self, pattern: str, name: str) -> None:
        super().__init__(name=name)

        assert isinstance(pattern, str)
        self.pattern = pattern
    
    def handle(self, t: Transaction) -> tuple[bool, Any]:
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
    def __init__(self, pattern: str, low: money, high: money, *, income=False, name: str) -> None:
        super().__init__(name=name)

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
    
    def handle(self, t: Transaction) -> tuple[bool, Any]:
        desc = t.desc.lower()
        if re.search(self.pattern, desc) and self.low <= t.amount <= self.high:
            return True, None
        else:
            return False, None
