# Generat imports
from dash import Dash, html, Output, Input
from functools import partial


# Project imports
import GUI


# Wrappers around GUI elements
def log():
    from Validation.Log.xls_to_json import xls_to_json
    from Validation.Log import load_log_data
    xls_to_json()
    data = load_log_data()
    return GUI.Log(data)
def aggregate():
    from Validation.Aggregate.xls_to_json import xls_to_json
    from Validation.Aggregate import load_aggregate_data
    xls_to_json()
    data = load_aggregate_data()
    return GUI.Aggregate(data)
def buckets():
    from Validation.Buckets.xls_to_json import xls_to_json
    from Validation.Buckets import load_buckets_data
    xls_to_json()
    data = load_buckets_data()
    return GUI.Buckets(data)

def main():
    app = Dash(__name__)
    
    # FIXME what's the point of this?
    def discard_args(func, *_):
        return func()

    output = html.Section(html.Div("Select a tab to begin"), id='Output')

    # Define the "tabs"
    buttons = []
    for tag, callback in (
        ('Log', log),
        ('Aggregate', aggregate),
        ('Buckets', buckets),
    ):
        button = html.Button(tag, id=tag)
        buttons.append(button)
        
        # Add the arguments to the callback and wrap it to discard the Input
        callback = partial(discard_args, callback)

        app.callback(Output(output, 'children', allow_duplicate=True), Input(button, 'n_clicks'), prevent_initial_call=True)(callback)

    app.layout = html.Div([
        html.Section(buttons, id='Buttons'),
        output,
    ])

    app.run(debug=True)

if __name__ == "__main__":
    main()
