# Project imports
from typing import Any as _Any
from Raw_Data.Parsing.USAAChecking.Transaction import Transaction
from ..Base import HandlerChain, DescAmount, DescRegex

note = DescAmount([
    "HONDA PMT 8004489307",
    "Honda Financial",
], 320, 320)

gas = DescAmount([
    "SHELL Service Station",
    "Chevron",
    "Circle K",
], 15, 35)

class CUParking(DescRegex):
    def __init__(self) -> None:
        super().__init__("CU (Fall|Spring|Summer) 202[123] Parking")
    
    def handle(self, t: Transaction) -> tuple[bool, _Any]:
        handled, result = super().handle(t)
        if handled and True:
            # TODO account = CU Bills
            return True, result
        else:
            return False, None

parking = HandlerChain(
    CUParking(),
    DescAmount([
        "ParkMobile",
        "CU Parking Remote",
    ], 0, 15),
)

handler = HandlerChain(note, gas)