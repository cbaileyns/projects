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
        
    def adjust_fico(self):
        a = self.data.fico_range_high
        a = a - min(a) + 1
        a = (a / max(a))
        self.data.fico_range_high = log(1/a)
    
    def adjust_desc(self):
        self.data.desc = self.data.desc.apply(lambda x: 0 if type(x) == float else max(0,len(x) - 31))
    
    def adjust_dates(self):
        self.data.earliest_cr_line = self.data.earliest_cr_line.apply(lambda x: datetime.datetime.strptime(x, "%b-%Y"))
        self.data.issue_d = self.data.issue_d.apply(lambda x: datetime.datetime.strptime(x, "%b-%Y"))
        self.data["age"] = self.data.issue_d - self.data.earliest_cr_line
        self.data.age = self.data.age.convert_objects(convert_timedeltas=True)
        self.data.age = self.data.age.apply(lambda x: np.timedelta64(x,"D").astype(float) / 365)
        

credit years... how many open lines in this time??


lc = LendingClub("loandata.csv")
lc.adjust_fico()
lc.adjust_desc()
lc.adjust_dates()
lc.get_x(["fico_range_high"])#,"open_acc","funded","unemployed","int_rate","revol_util"

l = Logistic(lc.x, lc.y)
l.eval()
