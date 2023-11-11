# General imports
import datetime
from pypdf import PdfReader

# General aliases
Date = datetime.date
strptime = datetime.datetime.strptime


# Dict like {y: {x: [text]}}
content_type = dict[float, dict[float, list]]
general: content_type = {}
def add_content(target: content_type, text, x, y):
    if not text: return
    if y not in target: target[y] = {}
    if x not in target[y]: target[y][x] = []
    target[y][x].append(text)
def sort_content(target: content_type):
    """Sort by coordinates"""
    return sorted(
        {y: sorted(
            x_dict.items(), key=lambda item: item[0]
            )
            for y, x_dict in target.items()
        }.items(),
        key=lambda item: item[0], reverse=True)

class Table:
    date: datetime.date # Statement date, used for picking the right parser
    top: float
    bot: float
    content: content_type
    data: dict
    columns: list
    def __init__(self, date: datetime.date) -> None:
        self.date = date
        self.content = {}
    def add(self, text, x, y):
        add_content(self.content, text, x, y)
    def contains(self, x, y) -> bool:
        return self.bot <= y <= self.top
    def print(self):
        print(', '.join(f'{k}: {v}' for k,v in self.data.items()))

class AccountTable(Table):
    top = 565
    header_y = 555.36
    columns = ['Account', 'Type', 'Statement Period']
    bot = 530
    def add(self, text, x, y):
        if y == self.header_y: return
        else: add_content(self.content, text, x, y)
    def process(self):
        """Combine all the data into one line, then parse"""
        data = {}
        for x_dict in self.content.values():
            data.update(x_dict)
        data = [item[1] for item in sorted(data.items(), key=lambda item: item[0])]
        assert all(len(d)==1 for d in data), data
        data = [d[0].strip() for d in data]

        # Special handling because it splits start and end into two
        num, typ, start, end = data
        data = [num, typ, ' '.join((start, end))]

        self.data = {k:d for k,d in zip(self.columns, data)}

class SummaryTable(Table):
    top = 520
    data_y = 493.2
    columns = ['Previous Balance', '# of Debits', 'Total of Debits', '# of Deposits', 'Total of Deposits', 'Service Charges', 'New Balance']
    bot = 490
    def add(self, text, x, y):
        if y == self.data_y: add_content(self.content, text, x, y)
        else: return
    def process(self):
        """Combine all the data into one line, then parse"""
        data = {}
        for x_dict in self.content.values():
            data.update(x_dict)
        data = [item[1] for item in sorted(data.items(), key=lambda item: item[0])]
        assert all(len(d)==1 for d in data), data
        data = [d[0].strip() for d in data]
        self.data = {k:d for k,d in zip(self.columns, data)}

def main(filepath: str, date: Date, show=True):
    account_table = AccountTable(date)
    summary_table = SummaryTable(date)
    reader = PdfReader(filepath)
    
    def visitor(text: str, cm: list, tm: list, font_dict: dict, font_size: dict):
        """cm - current matrix to move from user coordinate space (also known as CTM)
        tm - current matrix from text coordinate space"""
        text = text.strip()
        _, _, _, _, x, y = tm
        if account_table.contains(x, y):
            account_table.add(text, x, y)
        elif summary_table.contains(x, y):
            summary_table.add(text, x, y)
        else:
            add_content(general, text, x, y)

    raw = reader.pages[0].extract_text(visitor_text=visitor)
    # raw = '\n'.join(page.extract_text(visitor_text=visitor) for page in reader.pages)

    account_table.process()
    summary_table.process()

    if show:
        print("Account:")
        account_table.print()
        print("Summary:")
        summary_table.print()
        # print("General:")
        # print(sort_content(general))
    else:
        print(f"{summary_table.data['Previous Balance']} --> {summary_table.data['New Balance']}")
    
    return summary_table.data['Previous Balance'], summary_table.data['New Balance']

if __name__ == "__main__":
    import os
    data_dir = os.path.join('Raw_Data', 'Statements', 'Checking')
    last = None # "new" balance from the last statement
    prev = None # "previous" balance from the current statement
    new = None # "new" balance from the current statement
    for filename in os.listdir(data_dir):
        date = strptime(filename.split('_')[0], '%Y%m%d').date()
        # TODO write parsers for later dates
        if date >= Date(2021, 2, 1):
            continue
        print(filename)
        
        try:
            prev, new = main(os.path.join(data_dir, filename), date, show=False)
        except Exception as e:
            print(repr(e))
        
        if last is not None:
            assert last == prev, "last statement new != current statement previous, is there a statement missing?"
        last = new
