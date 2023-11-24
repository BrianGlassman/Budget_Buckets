# General imports
import os


# Project imports
from ..Base import HandlerChain


handler = HandlerChain.from_package(__file__, __package__, name="Top Level")
