# Project imports
from typing import Any
from Raw_Data.Parsing.USAAChecking.Transaction import Transaction
from ..Base import HandlerChain, DescKeywords, DescAmount


spotify = HandlerChain(
    DescAmount("PAYPAL INST XFER", 10.81, 10.81),
    DescAmount("Spotify", 10.81, 10.81),
    DescAmount("Spotify", 5.40, 5.40), # Student discount
)

hbo = DescAmount("HBO Max", 17.31, 17.31)

books = DescAmount("Kindle", 0, 20)

games = DescAmount("STEAMGAMES.COM", 0, 80)

bars = DescAmount([
    "Boulderado License",
    "Outback Saloon",
    "Pearl St Pub and Cellar",
    "Pearl St Pub And Cellar",
    "Rayback Collective",
    "The Dark Horse",
], 0, 40)

big_fun = DescKeywords("Spirit Halloween")

handler = HandlerChain(spotify, hbo, books, games, bars, big_fun)
