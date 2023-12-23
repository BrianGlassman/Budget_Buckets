from datetime import date as Date
from dateutil.relativedelta import relativedelta

base = {
    "Nature Conservancy": -30,
    "Phone": -35,
    "Rent": -1850,
    "Parking": -100,
    "Utilities": -100,
    "Insurance": -150,
    "Average Other": -878,
    # TODO electric (guestimated as part of utilities)
}
base = sum(v for v in base.values())

salary = 5579

#%% Loans
class Loan:
    def __init__(self, balance, rate, min) -> None:
        self.balance = balance
        self.rate = rate
        self.min = min
    def interest(self):
        """Apply interest for 30 days\n
        Formula reverse-engineered from Aidvantage interest calculator"""
        val = self.balance * self.rate * (30 / 365.25)
        val = round(val, 2)
        self.balance += val
        return val
    def pay(self, amt: float):
        assert amt <= self.balance
        self.balance -= amt
def apply_interest(loans: dict[str, Loan]):
    total = 0
    for loan in loans.values():
        if loan.balance > 0 and loan.rate > 0:
            total += loan.interest()
    return total
def pay_loans(loans: dict[str, Loan], amt: float):
    """Pay off loans, prioritized by interest, accounting for minimums. Return the remaining funds"""
    for loan in loans.values():
        if loan.min:
            pay = min(loan.min, loan.balance)
            loan.pay(pay)
            amt -= pay
    assert amt > 0, "Couldn't make minimum payments"

    ordered_loans = sorted((loan for loan in loans.values() if loan.balance > 0), key=lambda loan: loan.rate, reverse=True)
    for loan in ordered_loans:
        if loan.balance > amt:
            # Make a partial payment
            loan.pay(amt)
            return 0.0
        else:
            # Pay off entirely
            amt -= loan.balance
            loan.pay(loan.balance)

        if amt == 0: break
    return amt

#%% Operation
income = salary
expenses = base
available = salary + base # Sum because base is already negative

def main(extra: float) -> tuple[dict[Date, float], float]:
    loans = {
        "Jill": Loan(9000, 0, 0),
        "Alan": Loan(10000, 0, 0),
        "Fed 1-01": Loan(20775.61, 5.280/100, 223.48),
        "Fed 1-02": Loan(19410.61, 6.540/100, 237.43),
    }

    min_payment = sum(loan.min for loan in loans.values()) + 0.01 # Rounding errors
    total = min_payment + extra
    assert total <= available
    
    debt = {}
    interest = 0
    paid_off = {}

    date = Date(2023, 12, 1)
    while len(paid_off) < len(loans):
        date = date + relativedelta(months=1)

        interest += apply_interest(loans)

        leftover = pay_loans(loans, total)

        if date == Date(2024, 1, 1):
            # Apply excess starting balance
            loans["Fed 1-02"].pay(12233-10000)

        for name, loan in loans.items():
            if name not in paid_off and loan.balance == 0:
                # print(f"Paid off {name} by {date}")
                paid_off[name] = date
        
        debt[date] = sum(loan.balance for loan in loans.values())
    return debt, round(interest, 2)

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    min_payment = 460.91 + 0.01 # Rounding errors
    data = {amt: main(amt) for amt in [0, 500, 1000, 1500, available-min_payment]}

    for amt, (d, interest) in data.items():
        plt.plot(d.keys(), d.values(), '.-', label=f"{amt} -> {interest}") # type: ignore
    
    plt.grid()
    plt.legend()
    plt.xlabel('Date')
    plt.ylabel('Debt [$]')
    plt.legend()
    plt.show()
