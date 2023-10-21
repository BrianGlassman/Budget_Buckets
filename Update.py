"""Script to help with adding new data"""
import datetime

from BaseLib import Sorting
from Classes import Record
from Handlers import Parsing

class Modes:
    last = 'last transactions'
    add_new = 'add new transactions'

# Get the last 3 days of transactions from each account
# (the last 3 days that had transactions, even if this spans more than 3 days)
def last_transactions(transactions: list[Record.RawRecord]):
    accounts = ['Credit Card', 'Checking', 'CU Bills']
    for account in accounts:
        print(f"   {account}:")
        ts = [x for x in transactions if x.account == account]
        ts = Sorting.by_date(ts)
        ts: list[Record.RawRecord]
        count = 0
        i = -1 ; t = ts[i]
        date = t.date
        while count < 3:
            while t.date == date:
                print(f"{t.date}, {t.desc}, {t.value}")
                i -= 1
                t = ts[i]
            else:
                # Day finished, get new date
                date = t.date
            count += 1

def choose(prompt, options: dict):
    choice = None
    print(prompt)
    while choice is None:
        for i, option in enumerate(options.keys()):
            print(f'{i+1}. {option}')
        choice = input()

        try:
            choice = int(choice) - 1
            return list(options.values())[choice]
        except:
            choice = None

if __name__ == "__main__":
    options = {
        "Display last transactions": Modes.last,
        "Process new transactions": Modes.add_new
    }
    mode = choose("Select mode:", options)

    if mode == Modes.last:
        transactions = Parsing.run()
        last_transactions(transactions=transactions)
    elif mode == Modes.add_new:
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
        if os.name == 'nt':
            # Windows
            downloads = 'D:\\Users\\Brian\\Downloads'
        else:
            # Assume Nix
            downloads = '/home/brian/Downloads'

        for account, info in mapper.items():
            dl_path = os.path.join(downloads, info['dl'])
            parser: Parsing.BaseParser = info['parser']
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

            # Sanitize personal information (PI)
            if account == 'Credit Card':
                for i, line in enumerate(new):
                    if 'AUTOMATIC PAYMENT - THANK YOU' in line:
                        # Possible match, check for PI
                        fields = line.split(',')
                        desc = fields[parser.fields.index('Description')].replace('"', '').replace("'", "")
                        if all(c.isnumeric() or c in ['"', "'"] for c in desc):
                            new[i] = line.replace(desc, 'USAA Credit Card')
                            print(f'Scrubbed PI:\n\t{line}\n\tto\n\t{new[i]}')
            
            # Skip pending transactions
            today = datetime.date.today()
            temp = []
            for line in new:
                fields = line.split(',')
                date = datetime.datetime.strptime(fields[0], '%Y-%m-%d').date()
                status = fields[parser.fields.index('Status')]
                if status == 'Pending':
                    assert (today - date).days <= 7, "Pending transaction found more than a week ago: " + line
                    print("Skipping pending transaction: " + line)
                else:
                    temp.append(line)
            new = temp ; del temp

            # Only copy new transactions (i.e. don't include ones that were already recorded)
            # Sometimes (ex. parking) duplicate transactions appear the same day so can't just throw away all duplicates
            options = {
                "Skip": 'skip',
                "Keep both": 'keep',
            }
            temp = []
            for line in new:
                if line in old:
                    prompt = "Possible duplicate line found: " + line
                    choice = choose(prompt, options)
                    if choice == 'skip':
                        pass
                    elif choice == 'keep':
                        temp.append(line)
                    else:
                        raise NotImplementedError()
                else:
                    temp.append(line)
            new = temp ; del temp

            # Write combined list back to file (newest at the top)
            with open(data_path, 'w') as f:
                f.write(header+'\n')
                f.writelines(x+'\n' for x in new)
                f.writelines(x+'\n' for x in old)
