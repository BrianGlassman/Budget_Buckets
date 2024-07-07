# General imports
import dash


# Project imports
from Validation.Log import LogItem


# File format
item_keys = ['Imported', 'Account', 'Override', 'Final', 'My Category', 'E', 'Comment']
# First line is meta-header
meta_header = (
    ['Imported - Untouched from base'] + ['']*5 +
    ['Account'] +
    ['Override - Changes from base'] + ['']*5 +
    ['Final - Values with overrides, to be used for calculation'] + ['']*5 +
    ['My Category', 'E', 'Comment']
)
# Second line is section headers
section_header_template = ["Date", "Description", "Original Description", "Category", "Amount", "Status"]
section_headers = (
    [x+'_i' for x in section_header_template] +
    ['Account'] +
    [x+'_o' for x in section_header_template] +
    section_header_template +
    ['My Category', 'E', 'Comment']
)

def Log(data: list[LogItem]):
    # --- Data ---
    table_data = []
    for item in data:
        row = []
        for key in item_keys:
            row.extend(item[key].values())
        table_data.append(dict((id, value) for id, value in zip(section_headers, row)))

    # --- Headers ---
    # First line is meta-header
    names = [[] for _ in meta_header]
    ids = ['' for _ in meta_header]
    for i, name in enumerate(meta_header):
        if name:
            # Update to new cell
            last = name
        else:
            # Re-use last cell
            name = last
        names[i].append(name)
    
    # Second line is section headers
    for i, name in enumerate(section_headers):
        names[i].append(name.replace('_i', '').replace('_o', ''))
        ids[i] = name

    # Turn lists into a single dict
    columns = [{'name': name, 'id': id} for name, id in zip(names, ids)]
    
    # --- Table ---
    table = dash.dash_table.DataTable(
        columns=columns,
        merge_duplicate_headers=True,
        style_header=dict(textAlign='center'),
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
