# Project imports
from typing import Any
from Raw_Data.Parsing.USAAChecking.Transaction import Transaction
from ...Base import HandlerChain, DescKeywords, DescAmount


spotify = HandlerChain(
    DescAmount(["PAYPAL INST XFER", "PAYPAL           INST XFER"], 10.81, 10.81, name='Spotify - Paypal'),
    DescAmount("Spotify", 10.81, 10.81, name='Spotify - Normal'),
    DescAmount("Spotify", 5.40, 5.40, name='Spotify - Student'),
    name="Spotify",
)

hbo = DescAmount("HBO Max", 17.31, 17.31, name="HBO")

books = DescAmount("Kindle", 0, 20, name="Kindle")

games = DescAmount("STEAMGAMES.COM", 0, 80, name="Steam")

bars = DescAmount([
    "Boulderado License",
    "Outback Saloon",
    "Pearl St Pub and Cellar",
    "Pearl St Pub And Cellar",
    "Rayback Collective",
    "The Dark Horse",
], 0, 40, name="Bars")

big_fun = DescKeywords("Spirit Halloween", name="Spirit Halloween")

handler = HandlerChain(spotify, hbo, books, games, bars, big_fun, name="Entertainment")
