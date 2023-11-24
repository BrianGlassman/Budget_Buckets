# Project imports
from ...Base import HandlerChain, DescAmount


# TODO attach dates
internet = HandlerChain(
    DescAmount("Comcast", 40.41, 40.50, name="Comcast"),
    DescAmount("Comcast", 60.74, 60.74, name="Comcast"),
    DescAmount("VERIZON", 40, 70, name="Verizon"),
    name="Internet",
)

# TODO attach dates
phone = DescAmount([
    "T-Mobile",
    "Sprint"
], 30, 31, name="Phone")

# TODO attach dates
electric_gas = HandlerChain(
    DescAmount("Xcel Energy", 30, 120, name="Bluff St Xcel"),
    DescAmount("PGW WEBPAY", 10, 30, name="PGW"),
    DescAmount([
        'PECOENERGY',
        'PECO - WALLET',
        'PECO ENERGY',
    ], 20, 100, name="PECO"),
    name="Electric and Gas",
)

handler = HandlerChain(internet, phone, electric_gas, name="Utilities")
