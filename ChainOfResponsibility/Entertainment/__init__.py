# Project imports
from typing import Any
from Raw_Data.Parsing.USAAChecking.Transaction import Transaction
from ..Base import HandlerChain, DescAmount


spotify = DescAmount('PAYPAL INST XFER', 10.80, 10.82)

books = DescAmount('Kindle', 0, 20)

games = DescAmount('STEAMGAMES.COM', 0, 70)

handler = HandlerChain(spotify, books, games)
