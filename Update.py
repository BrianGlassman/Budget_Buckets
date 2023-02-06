"""Script to help with adding new data"""

import Parsing
import Record
from Root import Sorting

class Modes:
    last = 'last transactions'
    add_new = 'add new transactions'

# Get the last 3 transactions from each account
def last_transactions(transactions: list[Record.RawRecord]):
    accounts = ['Credit Card', 'Checking', 'CU Bills']
    for account in accounts:
        print(f"   {account}:")
        ts = [x for x in transactions if x.account == account]
        ts = Sorting.by_date(ts)
        ts: list[Record.RawRecord]
        for t in ts[-3:]:
            print(f"{t.date}, {t.desc}, {t.value}")

if __name__ == "__main__":
    mode = Modes.add_new

    if mode == Modes.last:
        transactions = Parsing.run()
        last_transactions(transactions=transactions)

    if mode == Modes.add_new:
        import os
        mapper = {
            'Credit Card': {
                'dl': 'cc.csv',
                'parser': Parsing.USAAParser,
                'data': '2023_cc.csv',
            },
            'Checking': {
                'dl': 'chk.csv',
                'parser': Parsing.USAAParser,
                'data': '2023_chk.csv',
            }
            # TODO handle CU Bills
        }
        # TODO add setting for Windows
        downloads = '/home/brian/Downloads'

        for account, info in mapper.items():
            dl_path = os.path.join(downloads, info['dl'])
            parser = info['parser'] ; parser: Parsing.BaseParser
            data_path = os.path.join('Raw_Data', info['data'])
            header = ','.join(parser.fields)

            # Read in the old data
            with open(data_path, 'r') as f:
                old = [line.strip() for line in f.readlines()]
            assert old[0] == header
            old = old[1:]

            # Read in the new data
            with open(dl_path, 'r') as f:
                new = [line.strip() for line in f.readlines()]
            assert new[0] == header
            new = new[1:]

            # Check for duplicates
            # Sometimes (ex. parking) duplicate transactions appear the same day so can't just use set intersection
            # There's a problem if num_dupes(new+old) != num_dupes(old) + num_dupes(new)
            def num_dupes(t): return len(t) - len(set(t))
            old_dupes = num_dupes(old) ; new_dupes = num_dupes(new)
            comb_dupes = num_dupes(old+new)
            if comb_dupes == old_dupes + len(new):
                print(f"WARNING: all {account} new transactions already exist")
                continue
            elif comb_dupes != old_dupes + new_dupes:
                raise RuntimeError(f"New set includes duplicated transactions")

            # Write combined list back to file (newest at the top)
            with open(data_path, 'w') as f:
                f.write(header+'\n')
                f.writelines(x+'\n' for x in new)
                f.writelines(x+'\n' for x in old)
