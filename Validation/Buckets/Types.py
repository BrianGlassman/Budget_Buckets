# General imports
from typing import Literal, TypeVar
from decimal import Decimal


"""Type definitions"""
category = str
category_with_total = category | Literal["total"]
# money = Decimal
money = str
# is_critical = bool
is_critical = str
# error_check = bool
error_check = str
month = str
all_months: list[month] = []
month_to_month = tuple[month, month] # [preceding month, subsequent month]
all_month_to_month: list[month_to_month] = [
    month_to_month(args)
    for args in zip(all_months[:-1], all_months[1:])
]

"""Shared section definitions"""
T = TypeVar('T')
category_to_value = dict[category, T]
category_with_total_to_value = dict[category_with_total, T]
class ValueCapacityCritical:
    value: category_with_total_to_value[money]
    capacity: category_with_total_to_value[money]
    is_critical: category_to_value[is_critical]
class ChangeSet:
    value_delta: category_with_total_to_value[money]
    value_set: category_with_total_to_value[money]
    capacity_delta: category_with_total_to_value[money]
    capacity_set: category_with_total_to_value[money]


"""DATA INPUT"""
class BucketsInput:
    """This is the data input version, not the validation or output version"""
    initial: ValueCapacityCritical
    transitions: dict[month_to_month, dict[Literal["changes"], ChangeSet]]


"""VALIDATION / HANDLER OUTPUT"""
class MonthFull:
    columns: dict[str, category_with_total_to_value[money]]
    intermediate: dict[Literal["Slush After Crit"], money]
    error_checks: dict[str, error_check]
class TransitionFull:
    """The transition between one month and the next
    This is the validation or output version, not the data input version"""
    end_previous: ValueCapacityCritical
    changes: ChangeSet
    start_next: ValueCapacityCritical
    error_checks: dict[Literal["Total"], error_check]

class BucketsFull:
    """This is the validation or output version, not the data input version"""
    initial: ValueCapacityCritical
    months: dict[month, MonthFull]
    transitions: dict[month_to_month, TransitionFull]
