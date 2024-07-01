# General imports
from typing import Literal, TypeVar
from dataclasses import dataclass, asdict as dataclass_to_dict
from decimal import Decimal # Commented out while money is a string


"""Type definitions"""
category = str
category_with_total = category | Literal["total"]
# money = Decimal
money = str
is_critical = bool
# error_check = bool
error_check = str
month = str
all_months: list[month] = []
month_to_month = tuple[month, month] # [preceding month, subsequent month]
all_month_to_month: list[month_to_month] = [
    month_to_month(args)
    for args in zip(all_months[:-1], all_months[1:])
]

"""Type conversions"""
def to_is_critical(v: str) -> is_critical:
    if isinstance(v, str):
        lower = v.lower()
        if lower == 'true':
            return True
        elif lower == 'false':
            return False
        else:
            raise ValueError(f"Unknown string: {v}")
    else:
        raise TypeError(f"Unknown type: {type(v)}")

"""Shared section definitions"""
T = TypeVar('T')
category_to_value = dict[category, T]
category_with_total_to_value = dict[category_with_total, T]
@dataclass
class ValueCapacityCritical:
    value: category_with_total_to_value[money]
    capacity: category_with_total_to_value[money]
    is_critical: category_to_value[is_critical]
@dataclass
class ChangeSet:
    value_delta: category_to_value[money | None]
    value_set: category_to_value[money | None]
    capacity_delta: category_to_value[money | None]
    capacity_set: category_to_value[money | None]
    crit_set: category_to_value[is_critical | None]

    def get_row(self, key: category):
        """Returns value_delta, value_set, capacity_delta, capacity_set, crit_set for a given category"""
        return (
            self.value_delta.get(key, None),
            self.value_set.get(key, None),
            self.capacity_delta.get(key, None),
            self.capacity_set.get(key, None),
            self.crit_set.get(key, None),
        )


"""DATA INPUT"""
@dataclass(init=False)
class BucketsInput:
    """This is the data input version, not the validation or output version"""
    initial: ValueCapacityCritical
    transitions: dict[month, dict[Literal["changes"], ChangeSet]]
    '''Key is preceding month'''

    def __init__(self, initial: ValueCapacityCritical, transitions=None):
        self.initial = initial
        self.transitions = {} if transitions is None else transitions
    
    def asdict(self):
        return dataclass_to_dict(self)


"""VALIDATION / HANDLER OUTPUT"""
@dataclass
class MonthFull:
    columns: dict[str, category_with_total_to_value[money]]
    intermediate: dict[Literal["Slush After Crit"], money]
    error_checks: dict[str, error_check]
@dataclass
class TransitionFull:
    """The transition between one month and the next
    This is the validation or output version, not the data input version"""
    end_previous: ValueCapacityCritical
    changes: ChangeSet
    start_next: ValueCapacityCritical
    error_checks: dict[Literal["Total"], error_check]

@dataclass(init=False)
class BucketsFull:
    """This is the validation or output version, not the data input version"""
    initial: ValueCapacityCritical
    months: dict[month, MonthFull]
    transitions: dict[month, TransitionFull]
    '''Key is preceding month'''

    def __init__(self, initial: ValueCapacityCritical, *, months=None, transitions=None):
        self.initial = initial
        self.months = {} if months is None else months
        self.transitions = {} if transitions is None else transitions
    
    def asdict(self):
        return dataclass_to_dict(self)
