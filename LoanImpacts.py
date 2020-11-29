from Loan import Loan
from LoanPortfolio import LoanPortfolio
import pandas as pd


class LoanImpacts:
    """ Contributor Impacts to Loan class
    """

    def __init__(self, principal, rate, payment, extra_payment, contributions):
        self.principal = principal
        self.rate = rate
        self.payment = payment
        self.extra_payment = extra_payment
        self.contributions = contributions

    def compute_impacts(self):
        # setup a loan portfolio
        # loan_portfolio = LoanPortfolio()

        # loan with all contributions (mi)_all
        #
        loan_all = Loan(principal=self.principal, rate=self.rate,
                        payment=self.payment, extra_payment=self.extra_payment + sum(self.contributions))
        loan_all.check_loan_parameters()
        loan_all.compute_schedule()

        # loan with no contributions (mi)_0
        #
        loan_none = Loan(principal=self.principal, rate=self.rate,
                         payment=self.payment, extra_payment=self.extra_payment)
        loan_none.check_loan_parameters()
        loan_none.compute_schedule()

        micro_impact_interest_paid_all = \
            (loan_none.total_interest_paid - loan_all.total_interest_paid) / loan_all.total_interest_paid
        micro_impact_duration_all = -\
            (loan_none.time_to_loan_termination - loan_all.time_to_loan_termination) / loan_all.time_to_loan_termination

        # micro_impact_interest_paid_all = loan_none.total_interest_paid / loan_all.total_interest_paid
        # micro_impact_duration_all = loan_none.time_to_loan_termination / loan_all.time_to_loan_termination

#        print(f'\nIndex\tInterestPaid\tDuration\tMIInterest\tMIDuration')
#        print(f'ALL\t',
#              round(loan_all.total_interest_paid, 2), f'\t\t', loan_all.time_to_loan_termination)
#        print(f'0\t',
#              round(loan_none.total_interest_paid, 2), f'\t\t', loan_none.time_to_loan_termination, f'\t\t',
#              round(micro_impact_interest_paid_all, 4), f'\t\t', round(micro_impact_duration_all, 4))
        df = pd.DataFrame(columns=['Index','InterestPaid','Duration','MIInterest',
                                   'MIDuration'])
        list = ['ALL',round(loan_all.total_interest_paid, 2),
                loan_all.time_to_loan_termination,None,None]
        df.loc[len(df)] = list
        list = [0,round(loan_none.total_interest_paid, 2),
                loan_none.time_to_loan_termination,
                round(micro_impact_interest_paid_all, 4),
                round(micro_impact_duration_all, 4)]
        df.loc[len(df)] = list
        i = 2

        # iterate over each contribution (mi)_index
        #
        for index, contribution in enumerate(self.contributions):
            loan_index = Loan(principal=self.principal, rate=self.rate, payment=self.payment,
                              extra_payment=self.extra_payment + sum(self.contributions) - contribution)
            loan_index.check_loan_parameters()
            loan_index.compute_schedule()

            micro_impact_interest_paid = \
                (loan_index.total_interest_paid - loan_all.total_interest_paid) / loan_all.total_interest_paid
            micro_impact_duration = \
                (loan_index.time_to_loan_termination - loan_all.time_to_loan_termination) / loan_all.time_to_loan_termination

            # micro_impact_interest_paid = loan.total_interest_paid / loan_all.total_interest_paid
            # micro_impact_duration = loan.time_to_loan_termination / loan_all.time_to_loan_termination

#            print(index+1, f'\t',
#                  round(loan_index.total_interest_paid, 2), f'\t\t', loan_index.time_to_loan_termination, f'\t\t',
#                  round(micro_impact_interest_paid, 4), f'\t\t', round(micro_impact_duration, 4))
            list = [i-1,round(loan_index.total_interest_paid, 2),
                    loan_index.time_to_loan_termination,
                    round(micro_impact_interest_paid, 4),
                    round(micro_impact_duration, 4)]
            df.loc[len(df)] = list
            i += 1
        
        df = df.reset_index(drop=True)
        return df




