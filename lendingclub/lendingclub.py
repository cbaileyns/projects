import pandas as pd
import numpy as np
import logisticregression

class LendingClub():
    
    def __init__(self, filelocation):
        self.data = pd.read_csv(filelocation,skiprows=1,encoding="utf-8")
        self.y = None
        self.x = None
        self.clean_data()
    
    def clean_data(self):
        self.data = self.data.query('loan_status == "Fully Paid" or loan_status == "Charged Off"')
        self.data.loan_status = self.data.loan_status.map({"Fully Paid":0, "Charged Off":1})  
        self.data.int_rate = self.data.int_rate.apply(lambda x: 0 if type(x) == float else np.float(x[:-1]))
        self.data.revol_util = self.data.revol_util.apply(lambda x: 0 if type(x) == float else np.float(x[:-1]))
        self.data["closed_acct"] = self.data.total_acc - self.data.open_acc
        self.data["funded"] = self.data.funded_amnt_inv / self.data.loan_amnt
        self.y = self.data.loan_status
        self.data["unemployed"] = self.data.emp_length == "n/a"
    
    def get_x(self, variables):
        self.x = self.data[variables]

lc = LendingClub("loandata.csv")
lc.get_x(["fico_range_high","open_acc","funded","unemployed","int_rate","revol_util"])

l = Logistic(lc.x, lc.y)
l.eval()
