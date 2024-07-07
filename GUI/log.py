# General imports
import dash


# Project imports
from Validation.Log import LogItem


meta_header = (
    ['Imported - Untouched from base'] + ['']*5 +
    ['Account'] +
    ['Override - Changes from base'] + ['']*5 +
    ['Final - Values with overrides, to be used for calculation'] + ['']*5 +
    ['My Category', 'E', 'Comment']
)

section_header_template = ["Date", "Description", "Original Description", "Category", "Amount", "Status"]
section_headers = (
    [x+'_i' for x in section_header_template] +
    ['Account'] +
    [x+'_o' for x in section_header_template] +
    section_header_template +
    ['My Category', 'E', 'Comment']
)

def Log(data: list[LogItem]):
    table_data = []
    # First line is meta-header
    # TODO

    # Second line is section headers
    # TODO
    
    # Remaining lines are data
    for item in data:
        row = []
        for key in ['Imported', 'Account', 'Override', 'Final', 'My Category', 'E', 'Comment']:
            row.extend(item[key].values())
        table_data.append(dict((header, value) for header, value in zip(section_headers, row)))

    # Dash wants a list of column dicts
    columns = [{'name': name, 'id': name} for name in section_headers]
    
    table = dash.dash_table.DataTable(
        columns=columns,
        data=table_data,
        page_size=50,
        # page_action='none', # Can uncomment to show everything on one page, but then it gets pretty slow
    )
    return table

if __name__ == "__main__":
    # Data handling
    from Validation.Log import load_log_data
    data = load_log_data()

    # Dash
    app = dash.Dash(__name__)
    app.layout = dash.html.Div(Log(data))
    app.run(debug=False)
