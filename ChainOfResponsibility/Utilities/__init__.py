# Project imports
from ..Base import HandlerChain, DescAmount

internet = HandlerChain(
    DescAmount("Comcast", 40.41, 40.50),
    DescAmount("Comcast", 60.74, 60.74),
    DescAmount("VERIZON", 40, 70),
)

phone = DescAmount([
    "T-Mobile",
    "Sprint"
], 30, 31)

electric_gas = HandlerChain(
    DescAmount("Xcel Energy", 30, 120), # Bluff St
    DescAmount("PGW WEBPAY", 10, 30),
    DescAmount([
        'PECOENERGY',
        'PECO - WALLET',
        'PECO ENERGY',
    ], 20, 100),
)

handler = HandlerChain(internet, phone, electric_gas)
