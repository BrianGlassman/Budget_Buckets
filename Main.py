# General imports
import pickle


# Project imports
from Raw_Data.Parsing.USAAChecking import main as parse_statements
from ChainOfResponsibility import handler


def get_statement_transactions(reload=True):
    pkl = 'pickle/statement_transactions.pkl'
    if reload:
        print("Parsing statement transactions")
        transactions = parse_statements()
        print("Saving to file")
        with open(pkl, 'wb') as f:
            pickle.dump(transactions, f)
    else:
        print("Loading statement transactions from file")
        with open(pkl, 'rb') as f:
            transactions = pickle.load(f)
    return transactions

for t in get_statement_transactions(False)[0:50]:
    handled, result = handler.handle(t)
    if handled:
        print("  handled: " + str(t))
    else:
        print("UNHANDLED: " + str(t))
