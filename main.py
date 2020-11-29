#from Helper import *
#from Loan import *
#from LoanPortfolio import *
import Helper
import Loan
import LoanPortfolio

loans = LoanPortfolio()


def compute_schedule(principal, rate, payment, extra_payment):

    loan = None
    try:
        loan = Loan(principal=principal, rate=rate, payment=payment, extra_payment=extra_payment)
        loan.check_loan_parameters()
        loan.compute_schedule()
    except ValueError as ex:
        print(ex)
    loans.add_loan(loan)
    Helper.plot(loan)
    Helper.print(loan)

    print(round(loan.total_principal_paid, 2), round(loan.total_interest_paid, 2),
          round(loan.time_to_loan_termination, 0))

    if loans.get_loan_count() == 3:
        loans.aggregate()
        Helper.plot(loans)
        Helper.print(loans)


if __name__ == '__main__':
    compute_schedule(12000.0, 4.0, 70.0, 12.0)
#    compute_schedule(5000.0, 2.0, 20.0, 6.0)
#    compute_schedule(10000.0, 3.0, 60.0, 7.0)
