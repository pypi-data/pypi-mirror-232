import numpy as np
from rsidatasciencetools.config.baseconfig import get_stdout_logger


class CaseGenerator(object):
    def __init__(self,amt_rng=None,
                 base_no_accts=2, base_no_contact_attempts=1,
                 rng=None, debug=0, logger=None, seed=None):
        self.seed = np.random.randint(0,np.iinfo(np.int32).max) if (seed is None)  and (rng is None) else seed
        self.rng = rng if rng is not None else np.random.RandomState(seed=self.seed)
        self.amt = np.array([100,10000]) if amt_rng is None else amt_rng
        self.base_no_contact_attempts = base_no_contact_attempts
        self.base_no_accts = base_no_accts
        self.debug = debug
        self.logger = get_stdout_logger(self.__class__.__name__,self.debug) if logger is None else (
            logger(self.__class__.__name__, self.debug) if callable(logger) else logger)
        
    def get_sample(self, default_risk=0.05, base_willingness_prob=0.9):
        assert default_risk < 0.5
        draw = self.rng.uniform()
        will_default = draw < default_risk
        willingness_prob = base_willingness_prob - self.rng.uniform(high=0.3)*int(will_default)
        pmt_plan = draw < default_risk*2
        no_accts = self.base_no_accts + self.rng.randint(0, 2+3*int(will_default))
        # pays_off_periodically = draw > default_risk*3
        amt_current_owed = self.rng.uniform(
            max(min(2*self.amt[0],self.amt[1]/2),self.amt[0]+np.diff(list(reversed(self.amt)))/2),
            2*self.amt[-1]) if will_default else self.rng.uniform(*self.amt)
        amt_rolling = np.cumsum(self.rng.uniform(size=3))
        amt_rolling /= amt_rolling[-1]
        amt_rolling *= amt_current_owed

        # if pays_off_periodically:
        #     for i in range(2):
        #         amt_rolling[i] = max(0, amt_rolling[i] - 0.5*self.rng.uniform()*amt_current_owed)
        no_late_pmts = []
        for iter in range(3):
            no_late_pmts.append(
                (self.rng.uniform(
                        high=default_risk*2+will_default*(1-default_risk*2-0.1),size=3) > default_risk).sum() * int(
                    amt_rolling[iter] > 0) + (
                0 if len(no_late_pmts) == 0 else no_late_pmts[iter-1]))
        on_time_payments = np.array([3,6,12]) - np.array(no_late_pmts)

        attempt_contact = []
        for iter in range(3):
            attempt_contact.append(no_late_pmts[iter]*(self.base_no_contact_attempts + 2*int(amt_rolling[iter] > self.amt[1]/2)) + (
                0 if len(attempt_contact) == 0 else attempt_contact[iter-1]))
        contact = []
        for iter in range(3):
            contact.append((
                self.rng.uniform(size=attempt_contact[iter]) < (willingness_prob-min(
                default_risk*2,(1-willingness_prob)/2))).sum() + (
                0 if len(contact) == 0 else contact[iter-1])
            )

        return dict(
            late_payments_90days=no_late_pmts[0],
            late_payments_180days=no_late_pmts[1],
            late_payments_360days=no_late_pmts[2],
            ontime_payments_90days=on_time_payments[0],
            ontime_payments_180days=on_time_payments[1],
            ontime_payments_360days=on_time_payments[2],
            od_90days=np.round(amt_rolling[0],2),
            od_180days=np.round(amt_rolling[1],2),
            od_360days=np.round(amt_rolling[2],2),
            od_now=np.round(amt_current_owed),
            has_used_payment_plan=pmt_plan,
            contact_90days=contact[0],
            contact_180days=contact[1],
            contact_360days=contact[2],
            no_accts=no_accts,
            target_resolved=not(will_default)
    ) 