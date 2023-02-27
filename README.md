# Summary
WIP Budgeting tool that focuses on continuous operation rather than month-by-month discrete units

---

# Setup
1. Setup categories in Root/BucketInfo.csv - this is what categories stuff goes into, the max amount of money in that "bucket", and how much to add per month
1. Setup account names in Root/Constants.py
1. Put data files in Raw_Data, they should be CSVs with columns Date, Description, Value. Negative values are expenses, positive values are income. Any other columns get saved, but not used.
1. Setup which files to pull data from in Parsing/ParseSettings.csv

# Usage
Run the Main.exe to open the main GUI, from which other screens can be accessed
1. Configure - set which transactions to use for later steps
1. Template Viewer - GUI for viewing the templates that are used to categorize stuff
1. Load Data - loads and categorizes everything, you have to do this before you can use any of the greyed-out buttons
1. Predict Future Transactions - tries to predict how much you're going to spend, but probably doesn't work yet
1. Summary Table - a table of income and expenses by month
1. Categorizing - lets you view transactions and categorize them manually or add comments
1. Bucket Timeline - shows a timeline of how much money is in each category "bucket"

---

# Known Problems
1. To delete Create items, edit the JSON file directly
1. To delete Templates, edit the JSON file directly

Everything in TODO.txt