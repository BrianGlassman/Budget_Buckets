# Project imports
from ..Base import HandlerChain, DescAmount

internet = DescAmount([
    'VERIZON',
    'COMCAST',
    ], 40, 70)

electric = DescAmount([
    'PGW WEBPAY',
    'PECOENERGY',
    'PECO - WALLET',
    'PECO ENERGY',
    'XCEL ENERGY-PSCO',
], 20, 100)

handler = HandlerChain(internet, electric)
