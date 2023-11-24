# Project imports
from ...Base import HandlerChain, DescKeywords, DescAmount


salary = DescKeywords([
    "AGUSTAWESTLAND P DIRECT DEP",
], name="Salary")

rewards = DescAmount("CASH REWARDS CREDIT", 0, 30, income=True, name="Cash Rewards")

interest = DescAmount("INTEREST PAID", 0, 10, income=True, name="Interest")

handler = HandlerChain(salary, rewards, interest, name="Income")
