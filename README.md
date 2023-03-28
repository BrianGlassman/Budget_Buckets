# Summary
WIP Budgeting tool that focuses on continuous operation rather than month-by-month discrete units

---

# Setup
1. Setup categories in Root/BucketInfo.csv - this is what categories stuff goes into, the max amount of money in that "bucket", and the max amount to add per month
2. Setup account names and data files in Root/AccountSetup.json. Accounts that have no recorded transactions should have an empty list
    - ex. Student loan transactions that are auto-generated when a loan is disbursed
    - If negative values are expenses, use GenericNeg parser
    - If positive values are expenses, use GenericPos parser
3. Put data files in Raw_Data, they should be CSVs with columns: Date, Description, Value
    - Any other columns get saved, but not used.

# Usage
Run the Main.exe to open the main GUI, from which other screens can be accessed
1. Configure - set which transactions to use for later steps
2. Template Viewer - GUI for viewing the templates that are used to categorize stuff
3. Load Data - loads and categorizes everything, you have to do this before you can use any of the greyed-out buttons
4. Predict Future Transactions - tries to predict how much you're going to spend, but probably doesn't work yet
5. Summary Table - a table of income and expenses by month
6. Categorizing - lets you view transactions and categorize them manually or add comments
7. Bucket Timeline - shows a timeline of how much money is in each category "bucket"

---

# Known Problems
1. To delete Create items, edit the JSON file directly
2. To delete Templates, edit the JSON file directly

Everything in TODO.txt