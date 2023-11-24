# Project imports
from ...Base import HandlerChain, DescRegexAmount


# TODO attach a date
bluff_st = DescRegexAmount("^Check #[0-9]*", 1850, 1850, name="Bluff St Rent")

handler = HandlerChain(bluff_st, name="Rent")
