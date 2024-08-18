# General imports
import openpyxl
from openpyxl.worksheet._read_only import ReadOnlyWorksheet

# Project imports

"""
Opens all the necessary Excel files with openpyxl
Makes the path(s) available for stale-checks

So mostly this file exists to track file paths and sheet names
"""

# Loading
excel_path = 'Budget_Buckets.xlsm'
years = ['2023', '2024']
wb = openpyxl.load_workbook(filename=excel_path, read_only=True, data_only=True)
logs: dict[str, ReadOnlyWorksheet] = {year:wb[f"Log {year}"] for year in years}
aggregates: dict[str, ReadOnlyWorksheet] = {year:wb[f"Aggregate {year}"] for year in years}
buckets: ReadOnlyWorksheet = wb["Buckets"]

# Type checking, just to be sure
for sheet in list(logs.values()) + list(aggregates.values()) + [buckets]:
    assert isinstance(sheet, ReadOnlyWorksheet), type(sheet)
