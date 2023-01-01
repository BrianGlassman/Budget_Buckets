import Parsing

parser = Parsing.USAAParser("USAA Credit Card", "cc.csv")
print('\n'.join(str(x) for x in parser.transactions))
