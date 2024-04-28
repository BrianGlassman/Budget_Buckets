The idea here is to be able to exactly duplicate the calculations of my Excel sheet, without using a GUI
No improvements, no tweaks, just a direct copy

The data handling here should eventually get moved out so that it can be shared between Validation and the actual App

Steps:
1. In Excel, manually export each tab as a CSV
1. Run `csv_to_json.py` on each CSV to generate the JSON file
    - This also checks that the incoming format is as-expected and enforces a consistent output format
1. Run the `Validation.py` to validate the results