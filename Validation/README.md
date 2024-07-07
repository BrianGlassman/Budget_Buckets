The idea here is to be able to exactly duplicate the calculations of my Excel sheet, without using a GUI
No improvements, no tweaks, just a direct copy

The data handling here should eventually get moved out so that it can be shared between Validation and the actual App

Order:
    Log
    Aggregate
    Buckets

Test
    Preferablly, use VSCode to run tests
    To run tests manually: python -m pytest
    To run tests manually with stdout: python -m pytest -s
    To generate coverage report: coverage run -m pytest
    To view a basic report: coverage report
    To generate an HTML report that allows inspecting files line-by-line:
        coverage html
        then open htmlcov/index.html in browser