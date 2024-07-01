"""
Process the input data
"""

# General imports
from copy import deepcopy
from typing import Any


# Project imports
from CategoryList import categories
from Validation.Buckets import Types


_column = Types.category_to_value[Types.money]
_column_t = Types.category_with_total_to_value[Types.money]
_crit_colum = Types.category_to_value[Types.is_critical]
def _generate_month(start: _column_t, transactions: _column_t, is_crit: _crit_colum, capacity: _column_t) -> Types.MonthFull:
    """
    start: Initial bucket value
        either from Initial setup or previous Transition
    transactions: Transaction totals for this month
    is_crit: Which buckets are critical (fill first)
    capacity: Bucket capacity
    """
    # FIXME shouldn't do this here
    # is_crit is actually strings, so convert to bool
    is_crit = {k:(v.lower() == 'true') for k,v in is_crit.items()} # type: ignore

    # Remove Total row to make data flow consistent
    def remove_total(column: _column_t) -> _column:
        """Return the column without the Total"""
        return {k:v for k,v in column.items() if k.lower() != "total"}
    start = remove_total(start)
    transactions = remove_total(transactions)
    capacity = remove_total(capacity)
    
    def add_columns(a: _column, b: _column) -> _column:
        # TODO stop forcing money to be a float
        assert a.keys() == b.keys()
        return {key: Types.money(float(a[key]) + float(b[key])) for key in a.keys()}
    
    def subtract_columns(a: _column, b: _column) -> _column:
        # TODO stop forcing money to be a float
        assert a.keys() == b.keys()
        return {key: Types.money(float(a[key]) - float(b[key])) for key in a.keys()}

    def scale_column(column: _column, scale: float) -> _column:
        # TODO stop forcing money to be a float
        return {key: Types.money(float(column[key]) * scale) for key in column.keys()}
    
    def sum_column(a: _column) -> Types.money:
        # TODO stop forcing money to be a float
        return Types.money(sum(float(v) for v in a.values()))
    
    def this_or_that(condition: _crit_colum, true_val, false_val) -> _column:
        """true_val and false_val can be columns or scalars"""
        # Reformat scalars into a column of scalars
        if not hasattr(true_val, 'keys'):
            true_val = {key:true_val for key in condition.keys()}
        if not hasattr(false_val, 'keys'):
            false_val = {key:false_val for key in condition.keys()}

        return {key:(true_val[key] if val else false_val[key]) for key, val in condition.items()}


    def compute_slush(after_t: _column_t, capacity: _column_t, cap_diff: _column) -> _column:
        # NOTE: this is the early method. At some point I changed to just max(cap_diff, 0) and started using is_crit for negative values
        assert capacity.keys() == after_t.keys() == cap_diff.keys()
        vals = {}
        for i in capacity.keys():
            # TODO stop forcing money to be a float
            if float(after_t[i]) < 0:
                # Negative bucket, immediately replenish from slush fund
                vals[i] = after_t[i]
            elif float(after_t[i]) > float(capacity[i]):
                # Bucket is over capacity, move excess to slush fund
                vals[i] = Types.money(-float(cap_diff[i]))
            else:
                # Do nothing
                vals[i] = 0
        return vals
    
    # Use {start} from arguments
    # Use {transactions} from arguments
    # Bucket value after transactions
    after_t: _column = add_columns(start, transactions)
    # Use {capacity} from arguments
    # Difference between bucket value and capacity
    cap_diff: _column = subtract_columns(capacity, after_t)
    # Movement from buckets to slush fund
    slush: _column = compute_slush(after_t=after_t, capacity=capacity, cap_diff=cap_diff)
    # Bucket values after removing slush funds
    before_fill: _column = subtract_columns(after_t, slush)
    # Difference between bucket value and capacity after removing slush funds
    s_cap_diff: _column = subtract_columns(capacity, before_fill)
    # Use {is_crit} from arguments (see NOTE in compute_slush)
    # Amount needed to fill critical buckets to full
    crit_to_fill: _column = this_or_that(is_crit, s_cap_diff, 0)
    # Bucket values after refilling critical buckets
    crit_filled: _column = add_columns(before_fill, crit_to_fill)
    # Amount needed to fill non-critical buckets to full
    nc_to_fill: _column = this_or_that(is_crit, 0, s_cap_diff)

    # Intermediate value: remaining slush fund after filling critical buckets
    # TODO stop forcing money to be a float
    slush_after_crit = Types.money(round(float(sum_column(slush)) - float(sum_column(crit_to_fill)), 2))

    # NC To Fill, but limited by slush fund
    # TODO stop forcing money to be a float
    # TODO once this actually uses money make sure the result is a float, not money-type
    scale_ratio = float(slush_after_crit) / float(sum_column(nc_to_fill))
    scaled: _column = scale_column(nc_to_fill, scale_ratio)
    # Bucket values after refilling non-critical buckets
    nc_filled: _column = add_columns(crit_filled, scaled)
    # Final bucket values
    final: _column = nc_filled
    # Difference between bucket value and capacity at the end of the month
    unfilled: _column = subtract_columns(capacity, final)
    # Percentage filled (use 100% for capacity=0)
    # FIXME has a "total", but it's not actually just the sum. Also this is a percentage, not Money, so not really a _column type
    # TODO stop forcing money to be a float
    percent_filled = {key:(float(final[key]) / float(capacity[key]) if capacity[key] != '0' else 1) for key in capacity}

    # Undo the string-to-bool conversion
    is_crit = {k:('True' if v else 'False') for k,v in is_crit.items()}

    def add_total(column: _column):
        """Adds the Total row"""
        column = deepcopy(column)
        column['total'] = sum_column(column)
        return column
    
    # TODO stop forcing money to be a float
    percent_filled['total'] = round(float(sum_column(final)) / float(sum_column(capacity)), 2)

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
        'Scaled': add_total(scaled),
        'NC Filled': nc_filled,
        'Final': add_total(final),
        'Unfilled': add_total(unfilled),
        '% Filled': percent_filled,
    }
    intermediate: dict[Any, Types.money] = {
        'Slush After Crit': slush_after_crit
    }
    # TODO stop forcing money to be a float
    error_checks = {
        "Available": "ERROR: Underwater" if float(sum_column(start)) < 0 else "good",
        "Internal": "ERROR: Unbalanced internal transfers" if (
            float(transactions['CC Payments']) != 0
            or
            float(transactions['Internal Transfers'])
        ) else "good",
        "Slush": "ERROR: No slush fund" if float(sum_column(slush)) < 0 else "good",
        "Crit To Fill": "ERROR: Can't refill critical buckets" if (
            float(sum_column(crit_to_fill)) > float(sum_column(slush))
        ) else "good",
        "Slush After Crit": "ERROR: Can't refill non-critical buckets" if float(slush_after_crit) < 0 else "good",
        "NC To Fill": "ERROR: Unused slush funds" if float(sum_column(nc_to_fill)) < float(slush_after_crit) else "good",
        "Scaled to Fill": "ERROR: Scaled doesn't match slush fund" if float(sum_column(scaled)) != float(slush_after_crit) else "good",
        "Final": "ERROR: Refilling changed the total" if float(sum_column(final)) != float(sum_column(after_t)) else "good"
    }
    return Types.MonthFull(columns=columns, intermediate=intermediate, error_checks=error_checks)

def handle(aggregate_data: list[dict], data: dict[str, Any]) -> Types.BucketsFull:
    # Reformat aggregate for easier reference
    transaction_lookup: dict[Types.month, Types.category_to_value[Types.money]]
    transaction_lookup = {item['start']:item['data'] for item in aggregate_data}

    # Initial - unchanged between Input and Full
    initial_dict: dict = data['initial']
    initial = Types.ValueCapacityCritical(
        value=initial_dict['value'],
        capacity=initial_dict['capacity'],
        is_critical=initial_dict['is_critical'],
    )

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
            is_crit = previous.is_critical

            # The month before the transition
            month: Types.month
            months[month] = month_obj = _generate_month(start, transaction_lookup[month], is_crit, capacity)

            # The transition itself
            end_previous = Types.ValueCapacityCritical(
                value=month_obj.columns['Final'],
                capacity=month_obj.columns['Capacity'],
                is_critical=month_obj.columns['Is Crit'],
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
                for key in end.value.keys():
                    if key == 'total': continue
                    # Unpack
                    value_delta, value_set, capacity_delta, capacity_set, crit_set = changes.get_row(key)
                    # Value
                    assert not (value_delta and value_set), "Can't use both delta and setter for value"
                    value[key] = value_set if value_set else end.value[key] + value_delta
                    # Capacity
                    assert not (capacity_delta and capacity_set), "Can't use both delta and setter for capacity"
                    capacity[key] = capacity_set if capacity_set else end.capacity[key] + capacity_delta
                    # Is_crit
                    is_crit[key] = crit_set if crit_set else end.is_critical[key]


                return Types.ValueCapacityCritical(
                    value=value,
                    capacity=capacity,
                    is_critical=is_crit,
                )
            start_next = generate_start_next(end_previous, changes)
            [float(v) for v in start_next.value.values()]
            error_checks: dict[Any, Types.error_check] = {'Total': 'ERROR: Totals changed' if (
                    # TODO stop forcing money to be a float
                    sum(float(v) for v in end_previous.value.values())
                    !=
                    sum(float(v) for v in start_next.value.values())
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
        break

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
    initial = Types.ValueCapacityCritical(
        value=initial_dict['value'],
        capacity=initial_dict['capacity'],
        is_critical=initial_dict['is_critical'],
    )

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
    transitions: dict = data['transitions']

    bucketsFull = Types.BucketsFull(
        initial=initial,
        months=months,
        transitions=transitions,
    )

    return bucketsFull
