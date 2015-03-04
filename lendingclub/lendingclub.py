import pandas as pd
import numpy as np

class LendingClub():
    
    def __init__(self, filelocation):
        self.data = pd.read_csv(filelocation,skiprows=1,encoding="utf-8")
        self.y = None
        self.x = None
    
    def clean_data(self):
        self.data = self.data.query('loan_status == "Fully Paid" or loan_status == "Charged Off"')
        self.data.loan_status = self.data.loan_status.map({"Fully Paid":0, "Charged Off":1})  
        self.data.int_rate = self.data.int_rate.apply(lambda x: np.nan if x in ['-'] else np.float(x[:-1]))
        self.data.revol_util = self.data.revol_util.apply(lambda x: np.nan if x in ['-'] else np.float(x[:-1]))
        self.data["closed_acct"] = self.data.total_acct - self.data.open_acct
        self.data["funded"] = self.data.funded_amnt_inv / self.data.loan_amnt
        self.y = self.data.loan_status
        self.data["unemployed"] = self.data.emp_length == "n/a"
