"""
Process the input data
"""

# General imports
from copy import deepcopy
from typing import Any


# Project imports
from BaseLib.money import Money
from Validation.Buckets import Types


# Logging
from BaseLib.logger import delegate_print as print

_column = Types.category_to_value[Money]
_column_t = Types.category_with_total_to_value[Money]
_crit_colum = Types.category_to_value[Types.is_critical]
def _generate_month(start: _column_t, transactions: _column_t, prev_crit: _crit_colum, capacity: _column_t) -> Types.MonthFull:
    """
    start: Initial bucket value
        either from Initial setup or previous Transition
    transactions: Transaction totals for this month
    is_crit: Which buckets are critical (fill first)
    capacity: Bucket capacity
    """
    # Remove Total row to make data flow consistent
    def remove_total(column: _column_t) -> _column:
        """Return the column without the Total"""
        return {k:v for k,v in column.items() if k.lower() != "total"}
    start = remove_total(start)
    transactions = remove_total(transactions)
    capacity = remove_total(capacity)
    
    def add_columns(a: _column, b: _column) -> _column:
        assert a.keys() == b.keys()
        return {key: a[key] + b[key] for key in a.keys()}
    
    def subtract_columns(a: _column, b: _column) -> _column:
        assert a.keys() == b.keys()
        return {key: a[key] - b[key] for key in a.keys()}

    def scale_column(column: _column, scale: float) -> _column:
        return {key: Money.from_dollars(column[key].to_dollars() * scale) for key in column.keys()}
    
    def sum_column(a: _column) -> Money:
        return sum(a.values(), Money(0, 0))
    
    def this_or_that(condition: _crit_colum, true_val, false_val) -> _column:
        """true_val and false_val can be columns or scalars"""
        # Reformat scalars into a column of scalars
        if not hasattr(true_val, 'keys'):
            true_val = {key:true_val for key in condition.keys()}
        if not hasattr(false_val, 'keys'):
            false_val = {key:false_val for key in condition.keys()}

        return {key:(true_val[key] if val else false_val[key]) for key, val in condition.items()}


    # def compute_slush(after_t: _column_t, capacity: _column_t, cap_diff: _column) -> _column:
    #     assert capacity.keys() == after_t.keys() == cap_diff.keys()
    #     vals = {}
    #     for i in capacity.keys():
    #         if after_t[i] < 0:
    #             # Negative bucket, immediately replenish from slush fund
    #             vals[i] = after_t[i]
    #         elif after_t[i] > capacity[i]:
    #             # Bucket is over capacity, move excess to slush fund
    #             vals[i] = -cap_diff[i]
    #         else:
    #             # Do nothing
    #             vals[i] = 0
    #     return vals
    def compute_slush(cap_diff: _column) -> _column:
        return {k:max(-v, Types.Money(0, 0)) for k,v in cap_diff.items()}
    
    def compute_crit(prev_crit: _crit_colum, after_t: _column) -> _crit_colum:
        assert prev_crit.keys() == after_t.keys()
        return {k:(prev_crit[k] or after_t[k] < 0) for k in prev_crit.keys()}
    
    # Use {start} from arguments
    # Use {transactions} from arguments
    # Bucket value after transactions
    after_t: _column = add_columns(start, transactions)
    # Use {capacity} from arguments
    # Difference between bucket value and capacity
    cap_diff: _column = subtract_columns(capacity, after_t)
    # Movement from buckets to slush fund
    slush: _column = compute_slush(cap_diff=cap_diff)
    # Bucket values after removing slush funds
    before_fill: _column = subtract_columns(after_t, slush)
    # Difference between bucket value and capacity after removing slush funds
    s_cap_diff: _column = subtract_columns(capacity, before_fill)
    # Use {is_crit} from arguments (see NOTE in compute_slush)
    # Which buckets are critical (fill first)
    is_crit: _crit_colum = compute_crit(prev_crit, after_t)
    # Amount needed to fill critical buckets to full
    crit_to_fill: _column = this_or_that(is_crit, s_cap_diff, Money(0, 0))
    # Bucket values after refilling critical buckets
    crit_filled: _column = add_columns(before_fill, crit_to_fill)
    # Amount needed to fill non-critical buckets to full
    nc_to_fill: _column = this_or_that(is_crit, Money(0, 0), s_cap_diff)

    # Intermediate value: remaining slush fund after filling critical buckets
    slush_after_crit = sum_column(slush) - sum_column(crit_to_fill)

    # NC To Fill, but limited by slush fund
    scale_ratio: float = slush_after_crit / sum_column(nc_to_fill)
    pre_scale: _column = scale_column(nc_to_fill, scale_ratio)

    # Because of rounding, there's sometimes a slight disagreement. Balance with Unexpected Fund
    scaled = deepcopy(pre_scale)
    if (diff := (sum_column(pre_scale) - slush_after_crit)) != 0:
        assert abs(diff.to_dollars()) < 0.05, f"Large difference encountered: {diff}"
        scaled['Unexpected Fund'] -= diff

    # Bucket values after refilling non-critical buckets
    nc_filled: _column = add_columns(crit_filled, scaled)
    # Final bucket values
    final: _column = nc_filled
    # Difference between bucket value and capacity at the end of the month
    unfilled: _column = subtract_columns(capacity, final)

    def add_total(column: _column):
        """Adds the Total row"""
        column = deepcopy(column)
        column['total'] = sum_column(column)
        return column
    
    columns = {
        'Start': add_total(start),
        'Transactions': add_total(transactions),
        'After T': add_total(after_t),
        'Capacity': add_total(capacity),
        'Cap Diff': add_total(cap_diff),
        'Slush': add_total(slush),
        'Before Fill': before_fill,
        'S Cap Diff': s_cap_diff,
        'Is Crit': is_crit,
        'Crit To Fill': add_total(crit_to_fill),
        'Crit Filled': crit_filled,
        'NC To Fill': add_total(nc_to_fill),
        'Pre Scale': add_total(pre_scale),
        'Scaled': add_total(scaled),
        'NC Filled': nc_filled,
        'Final': add_total(final),
        'Unfilled': add_total(unfilled),
    }
    intermediate: dict[Any, Money] = {
        'Slush After Crit': slush_after_crit
    }
    error_checks = {
        "Available": "ERROR: Underwater" if sum_column(start) < 0 else "good",
        "Internal": "ERROR: Unbalanced internal transfers" if (
            transactions['CC Payments'] != 0
            or
            transactions['Internal Transfers'] != 0
        ) else "good",
        "Slush": "ERROR: No slush fund" if sum_column(slush) < 0 else "good",
        "Crit To Fill": "ERROR: Can't refill critical buckets" if (
            sum_column(crit_to_fill) > sum_column(slush)
        ) else "good",
        "Slush After Crit": "ERROR: Can't refill non-critical buckets" if slush_after_crit < 0 else "good",
        "NC To Fill": "ERROR: Unused slush funds" if sum_column(nc_to_fill) < slush_after_crit else "good",
        "Scaled to Fill": "ERROR: Scaled doesn't match slush fund" if sum_column(scaled) != slush_after_crit else "good",
        "Final": "ERROR: Refilling changed the total" if sum_column(final) != sum_column(after_t) else "good"
    }
    assert not (failures := [v for v in error_checks.values() if v != "good"]), failures
    return Types.MonthFull(columns=columns, intermediate=intermediate, error_checks=error_checks)

def handle(aggregate_data: list[dict], data: dict[str, Any]) -> Types.BucketsFull:
    # Reformat aggregate for easier reference
    transaction_lookup: dict[Types.month, Types.category_to_value[Money]]
    transaction_lookup = {item['start']:item['data'] for item in aggregate_data}

    # Initial - unchanged between Input and Full
    initial_dict: dict = data['initial']
    initial = Types.ValueCapacityCritical(**initial_dict)

    # Months and Transitions
    months: dict = {}
    transitions: dict = {}
    # Start with the initial settings (will be overwritten by each month)
    previous = initial
    for month, transition in data['transitions'].items():
        try:
            # Unpack
            start = previous.value
            capacity = previous.capacity
            prev_crit = previous.is_critical

            # The month before the transition
            month: Types.month
            months[month] = month_obj = _generate_month(start, transaction_lookup[month], prev_crit, capacity)

            # The transition itself
            end_previous = Types.ValueCapacityCritical(
                value=month_obj.columns['Final'],
                capacity=month_obj.columns['Capacity'],
                is_critical=prev_crit,
            )
            changes = Types.ChangeSet(
                value_delta=transition['changes']['value_delta'],
                value_set=transition['changes']['value_set'],
                capacity_delta=transition['changes']['capacity_delta'],
                capacity_set=transition['changes']['capacity_set'],
                crit_set=transition['changes']['crit_set'],
            )
            def generate_start_next(end: Types.ValueCapacityCritical, changes: Types.ChangeSet) -> Types.ValueCapacityCritical:
                value = {}
                capacity = {}
                is_crit = {}
                # Handle data
                for key in end.value.keys():
                    if key == 'total': continue
                    # Unpack
                    value_delta, value_set, capacity_delta, capacity_set, crit_set = changes.get_row(key)
                    # Value
                    if value_delta and value_set: raise ValueError("Can't use both delta and setter for value")
                    elif value_set: value[key] = value_set
                    elif value_delta: value[key] = end.value[key] + value_delta
                    else: value[key] = end.value[key]
                    # Capacity
                    if capacity_delta and capacity_set: raise ValueError("Can't use both delta and setter for capacity")
                    elif capacity_set: capacity[key] = capacity_set
                    elif capacity_delta: capacity[key] = end.capacity[key] + capacity_delta
                    else: capacity[key] = end.capacity[key]
                    # Is_crit
                    is_crit[key] = crit_set if crit_set else end.is_critical[key]
                
                # Handle total
                value['total'] = sum(value.values())
                capacity['total'] = sum(capacity.values())

                return Types.ValueCapacityCritical(
                    value=value,
                    capacity=capacity,
                    is_critical=is_crit,
                )
            start_next = generate_start_next(end_previous, changes)
            error_checks: dict[Any, Types.error_check] = {'Total': 'ERROR: Totals changed' if (
                    sum(end_previous.value.values()) != sum(start_next.value.values())
                ) else 'good'}
            transitions[month] = transition_obj = Types.TransitionFull(
                end_previous=end_previous,
                changes=changes,
                start_next=start_next,
                error_checks=error_checks,
            )

            # Update the tracker for the next loop
            previous = transition_obj.start_next
        except Exception:
            print(f"Failed for {month}")
            raise

    bucketsFull = Types.BucketsFull(
        initial=initial,
        months=months,
        transitions=transitions,
    )

    return bucketsFull

def handle_validation(data: dict[str, Any]) -> Types.BucketsFull:
    """Converts a raw dict into a BucketsFull"""
    data = deepcopy(data)

    # Initial
    initial_dict: dict = data['initial']
    initial = Types.ValueCapacityCritical(**initial_dict)

    # Months
    months: dict[Types.month, Types.MonthFull] = {
        k:Types.MonthFull(
            columns=v['columns'],
            intermediate=v['intermediate'],
            error_checks=v['error_checks'],
        )
        for k,v in data['months'].items()
    }

    # Transitions
    transitions: dict[Types.month, Types.TransitionFull] = {
        k:Types.TransitionFull(
            end_previous=Types.ValueCapacityCritical(**v['end_previous']),
            changes=Types.ChangeSet(**v['changes']),
            start_next=Types.ValueCapacityCritical(**v['start_next']),
            error_checks=v['error_checks'],
        )
        for k,v in data['transitions'].items()
    }

    bucketsFull = Types.BucketsFull(
        initial=initial,
        months=months,
        transitions=transitions,
    )

    return bucketsFull
