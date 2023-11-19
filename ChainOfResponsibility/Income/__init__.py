# Project imports
from ..Base import HandlerChain, DescKeywords, DescAmount


salary = DescKeywords([
    "AGUSTAWESTLAND P DIRECT DEP",
])

rewards = DescAmount("CASH REWARDS CREDIT", 0, 30, income=True)

interest = DescAmount("INTEREST PAID", 0, 10, income=True)

handler = HandlerChain(salary, rewards, interest)
