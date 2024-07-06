The idea here is to be able to exactly duplicate the calculations of my Excel sheet, without using a GUI
No improvements, no tweaks, just a direct copy

The data handling here should eventually get moved out so that it can be shared between Validation and the actual App

Steps:
1. In Excel, manually export each tab as a CSV
1. Run `xls_to_json.py` to generate the JSON files
    - This also checks that the incoming format is as-expected and enforces a consistent output format
1. Run the `test_*.py` scripts to validate the results (or use Pytest)

For PyTest, use "python -m pytest" (can add "-s" to show console output)