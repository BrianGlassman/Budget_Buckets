# Project imports
from ..Base import HandlerChain, DescKeywords


pharmacy = DescKeywords([
    "CVS/PHARM",
])

insurance = DescKeywords([
    "MOLINA HEALTHCARE"
])

handler = HandlerChain(pharmacy, insurance)