# Project imports
from ...Base import HandlerChain, DescKeywords


pharmacy = DescKeywords([
    "CVS/PHARM",
], name="Pharmacy")

insurance = DescKeywords([
    "MOLINA HEALTHCARE"
], name="Medical Insurance")

handler = HandlerChain(pharmacy, insurance, name="Medical")