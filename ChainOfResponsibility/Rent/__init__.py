# Project imports
from ..Base import HandlerChain, DescRegexAmount


bluff_st = DescRegexAmount("^Check #[0-9]*", 1850, 1850)

handler = HandlerChain(bluff_st)
