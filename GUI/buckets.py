# General imports
import dash
from dash import html
from dash.dash_table import DataTable


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
    months = [make_month(*item) for item in data.months.items()]
    transitions = [make_transition(*item) for item in data.transitions.items()]

    mt = [val for pair in zip(months, transitions) for val in pair]

    combined = html.Div([
        html.Div([make_categories()], style={'display': 'inline-block'}),
        html.Div([make_initial(data.initial)], style={'display': 'inline-block'}),
        html.Div([
            html.Div([item], style={'display': 'inline-block'}) for item in mt
        ], style={'display': 'inline-block'}),
        ], style={'overflow-x': 'scroll', 'white-space': 'nowrap'},
    )
    return combined

def make_ValueCapacityCritical(data: Types.ValueCapacityCritical):
    header = [
        "Value",
        "Capacity",
        "Is Crit",
    ]

    table_data = [
        data.value.values(),
        data.capacity.values(),
        data.is_critical.values(),
    ]
    table_data = [
        dict((id, value) for id, value in zip(header, row))
        for row in zip(*table_data)
    ]

    # --- Table ---
    # Turn lists into a single dict
    columns = [{'name': h, 'id': h} for h in header]
    # Make the table
    table = DataTable(
        columns=columns,
        merge_duplicate_headers=True,
        style_header=dict(textAlign='center'),
        data=table_data,
        page_action='none',
    )
    return table

def make_ChangeSet(data: Types.ChangeSet):
    header = [
        "Val Diff",
        "Set Val",
        "Cap Diff",
        "Set Cap",
        "Is Crit",
    ]

    # Only stores changes, so have to fill in empty spaces
    def fill_empty(values: dict):
        return {category:values.get(category, '') for category in categories}

    table_data = [
        data.value_delta,
        data.value_set,
        data.capacity_delta,
        data.capacity_set,
        data.crit_set,
    ]
    table_data = [fill_empty(dct).values() for dct in table_data]
    table_data = [
        dict((id, value) for id, value in zip(header, row))
        for row in zip(*table_data)
    ]

    # --- Table ---
    # Turn lists into a single dict
    columns = [{'name': h, 'id': h} for h in header]
    # Make the table
    table = DataTable(
        columns=columns,
        merge_duplicate_headers=True,
        style_header=dict(textAlign='center'),
        data=table_data,
        page_action='none',
    )
    return table

def add_header(table: DataTable, new_row):
    """Adds a new row to the header of the table"""
    columns = table.columns # type: ignore # PyLance thinks there's no .columns, but there is

    # Allow passing a string to fill an entire row
    if isinstance(new_row, str):
        new_row = [new_row] * len(columns)
    
    for new_item, column in zip(new_row, columns):
        column['name'] = [new_item, column['name']]


def make_transition(month: str, data: Types.TransitionFull):
    end_previous = make_ValueCapacityCritical(data.end_previous)
    add_header(end_previous, "Previous Month")

    changes = make_ChangeSet(data.changes)
    add_header(changes, "Changes")

    start_next = make_ValueCapacityCritical(data.start_next)
    add_header(start_next, "Result")

    return html.Div([
        html.Div([end_previous], style={'display': 'inline-block'}),
        html.Div([changes], style={'display': 'inline-block'}),
        html.Div([start_next], style={'display': 'inline-block'}),
    ])

def make_month(month: str, data: Types.MonthFull):
    table_data = [d.values() for d in data.columns.values()]
    table_data = [
        dict((id, value) for id, value in zip(header, row))
        for row in zip(*table_data)
    ]

    # First cell is the month itself (using the whole row because it looks better)
    m, d, y = month.split('/')
    month = f"{m}/{y}"
    top = [month] * len(header)

    names = list(zip(top, header))
    tooltips = {i:d for i, d in zip(header, descriptions)}
    # FIXME tooltips get applied to the top two lines of the three-line header

    # --- Table ---
    # Turn lists into a single dict
    columns = [{'name': name, 'id': id} for name, id in zip(names, header)]
    # Make the table
    table = DataTable(
        columns=columns,
        tooltip_header=tooltips,
        merge_duplicate_headers=True,
        style_header=tt_indicator | dict(textAlign='center'),
        data=table_data,
        page_action='none',
    )
    return table

def make_initial(initial: Types.ValueCapacityCritical):
    """The initial setup before the first month"""
    table = make_ValueCapacityCritical(initial)
    add_header(table, 'WARNING: Approximate values')
    return table

def make_categories():
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
    table = DataTable(
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
    app.run(debug=True)
