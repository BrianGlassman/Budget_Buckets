# General imports
import dash
import datetime
from typing import Sequence


# General aliases
Date = datetime.date


# Project imports
from Raw_Data.Parsing.USAAChecking.Transaction import Transaction
from Raw_Data.Parsing.USAAChecking import main as parse



table_style = {
    'style_header': {
        'backgroundColor': 'darkBlue',
        'color': 'white',
        'fontWeight': 'bold',
    },
    'style_data': {
        'backgroundColor': 'grey',
        'color': 'white',
    },
    'style_data_conditional': [{
        'if': {'state': 'selected'},
        'backgroundColor': 'lightGrey',
        'border': '1px solid white',
    }],
}


def create_table(transactions: Sequence[Transaction]):
    # Headers map {id: name}
    header: dict[str, str] = {}

    # Raw transaction fields
    raw_header = {
        'date': 'Date',
        'desc': 'Description',
        'amount': 'Amount',
    }
    header.update(raw_header)

    # Categorization fields
    cat_header = {
        'cat': 'Category',
        'comment': 'Comment',
        'dur': 'Duration',
    }
    header.update(cat_header)

    data = []
    for transaction in transactions:
        # Map values to header IDs (not names)
        table_row = {
            'date': transaction.date,
            'desc': transaction.desc,
            'amount': transaction.amount,
        }
        data.append(table_row)
    
    # Dash wants the column specification as a list of dicts
    columns = []
    for id, name in header.items():
        entry: dict[str, str|bool] = {'name': name, 'id': id}
        if id in cat_header:
            entry['editable'] = True
        columns.append(entry)
    
    table = dash.dash_table.DataTable(
        columns=columns,
        data=data,
        page_size=25,
        **table_style,
    )

    return table

if __name__ == "__main__":
    app = dash.Dash(__name__)

    transactions = parse()
    print(f"Loaded {len(transactions)} transactions")

    table = create_table(transactions)

    app.layout = dash.html.Div(table, style={'backgroundColor': 'lightBlue'})

    app.run(debug=True)
