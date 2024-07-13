# General imports
import dash
from dash import html


# Project imports
from CategoryList import categories
from Validation.Buckets import Types


# File format
# Second row is descriptions
descriptions = (
    "Initial bucket value",
    "Transaction totals for this month",
    "Bucket value after transactions",
    "Bucket capacity",
    "Difference between bucket value and capacity",
    "Movement from buckets to slush fund",
    "Bucket values after removing slush funds",
    "Difference between bucket value and capacity after removing slush funds",
    "Which buckets are critical (fill first)",
    "Amount needed to fill critical buckets to full",
    "Bucket values after refilling critical buckets",
    "Amount needed to fill non-critical buckets to full",
    "Make sure Scaled avoids rounding problems",
    "NC To Fill, but limited by slush fund",
    "Bucket values after refilling non-critical buckets",
    "Final bucket values",
    "",
)
# Third row is header
header = (
    "Start",
    "Transactions",
    "After T",
    "Capacity",
    "Cap Diff",
    "Slush",
    "Before Fill",
    "S Cap Diff",
    "Is Crit",
    "Crit To Fill",
    "Crit Filled",
    "NC To Fill",
    "Pre Scale",
    "Scaled",
    "NC Filled",
    "Final",
    "Unfilled",
)

# Style to indicate a tooltip is present
tt_indicator = {'textDecoration': 'underline', 'textDecorationStyle': 'dotted'}


def Buckets(data: Types.BucketsFull):
    # for item in data.months.items():
    #     make_month(*item, ids, names, table_data)
    item = next(iter(data.months.items()))

    # Turn lists into a single dict
    # --- Table ---
    combined = html.Div([
        html.Div([make_categories()], style={'display': 'inline-block'}),
        html.Div([make_initial(data.initial)], style={'display': 'inline-block'}),
        html.Div([make_month(*item)], style={'display': 'inline-block'}),
        ],
        style={'overflow-x': 'scroll', 'white-space': 'nowrap'},
    )
    return combined

def make_month(month: str, data: Types.MonthFull):
    width = 17
    # table_data: list of rows
    # Can't do [{}]*# because it re-uses the dict
    # Add an extra row for the total
    # table_data: list[dict] = [{} for _ in range(len(categories) + 1)]
    # for c, (header, column) in enumerate(data.columns.items()):
    #     for r, (category, value) in enumerate(column.items()):
    #         table_data[r][header] = value

            

    table_data = [d.values() for d in data.columns.values()]
    table_data = [
        dict((id, value) for id, value in zip(header, row))
        for row in zip(*table_data)
    ]
        

    # First cell is the month itself
    # Rest of that row is blank
    top = [month] + [''] * (width - 1)

    names = list(zip(top, header))
    tooltips = {i:d for i, d in zip(header, descriptions)}
    # FIXME tooltips get applied to the top two lines of the three-line header

    # --- Table ---
    # Turn lists into a single dict
    columns = [{'name': name, 'id': id} for name, id in zip(names, header)]
    # Make the table
    table = dash.dash_table.DataTable(
        columns=columns,
        tooltip_header=tooltips,
        merge_duplicate_headers=True,
        style_header=tt_indicator | dict(textAlign='center'),
        data=table_data,
        page_action='none',
    )
    return table

def make_initial(initial: Types.ValueCapacityCritical) -> dash.dash_table.DataTable:
    """The initial setup before the first month"""
    names = [
        ['WARNING: Approximate values']*3,
        ['Value', 'Capacity', 'Is Crit'],
    ]
    ids = names[-1].copy()
    names = list(zip(*names))

    table_data = [
        initial.value.values(),
        initial.capacity.values(),
        initial.is_critical.values(),
    ]
    table_data = [
        dict((id, value) for id, value in zip(ids, row))
        for row in zip(*table_data)
    ]

    # --- Table ---
    # Turn lists into a single dict
    columns = [{'name': name, 'id': id} for name, id in zip(names, ids)]
    # Make the table
    table = dash.dash_table.DataTable(
        columns=columns,
        merge_duplicate_headers=True,
        style_header=dict(textAlign='center'),
        data=table_data,
        page_action='none',
    )
    return table

def make_categories() -> dash.dash_table.DataTable:
    """The category list at the far left"""
    names = ['Dir', 'Broad', 'Specific', 'Key']
    ids = names.copy()
    names = [['', name] for name in names]

    # TODO handle Dir, Broad, and Specific columns, not just Key (category)
    table_data = []
    for cat in categories:
        row = ['']*3 + [cat]
        table_data.append(dict((id, value) for id, value in zip(ids, row)))

    # --- Table ---
    # Turn lists into a single dict
    columns = [{'name': name, 'id': id} for name, id in zip(names, ids)]
    # Make the table
    table = dash.dash_table.DataTable(
        columns=columns,
        merge_duplicate_headers=True,
        style_header=dict(textAlign='center'),
        data=table_data,
        page_action='none',
    )
    return table

if __name__ == "__main__":
    # Data handling
    from Validation.Buckets import load_buckets_data
    data = load_buckets_data()

    # Dash
    app = dash.Dash(__name__)
    app.layout = dash.html.Div(Buckets(data))
    app.run(debug=False)
