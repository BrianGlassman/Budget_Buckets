# General imports
import dash
import datetime
from typing import Sequence


# General aliases
Date = datetime.date


# Project imports
from Raw_Data.Parsing.USAAChecking.Transaction import Transaction
from Raw_Data.Parsing.USAAChecking import main as parse

if __name__ == "__main__":
    transactions = parse()

    out = []
    for t in transactions:
        out.append(f'{t.date},{t.desc},{t.amount},{t.balance_after}\n')
    
    with open('out.csv', 'w') as f:
        f.writelines(out)