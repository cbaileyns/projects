import pandas as pd
import numpy as np
import datetime
from ggplot import *
from logisticregression import Logistic
from pandasql import *
import datetime

class LendingClub():
    
    def __init__(self, filelocation):
        self.data = pd.read_csv(filelocation,skiprows=1,encoding="utf-8")
        self.y = None
        self.x = None
        self.clean_data()
    
    def drop(self,var):
        self.data.drop(var,axis=1,inplace=True)
    
    def clean_data(self):
        self.data.drop(self.data.columns[37:],axis=1,inplace=True)
        self.data.drop(self.data.columns[0:2],axis=1,inplace=True)
        self.data = self.data.query('loan_status == "Fully Paid" or loan_status == "Charged Off"')
        self.data.loan_status = self.data.loan_status.map({"Fully Paid":0, "Charged Off":1})  
        self.data.int_rate = self.data.int_rate.apply(lambda x: 0 if type(x) == float else np.float(x[:-1]))
        self.data.revol_util = self.data.revol_util.apply(lambda x: 0 if type(x) == float else np.float(x[:-1]))
        self.data.annual_inc = self.data.annual_inc.apply(lambda x: 200000 if x > 200000 else x)
        #self.data["closed_acct"] = self.data.total_acc - self.data.open_acc
        self.data["funded"] = self.data.funded_amnt_inv / self.data.loan_amnt
        self.y = self.data.loan_status
        self.data["unemployed"] = self.data.emp_length == "n/a"
        self.drop("funded_amnt")
        self.data.sub_grade = self.data.sub_grade.apply(lambda x: x[1])
        self.drop("emp_title")
        self.drop("pymnt_plan")
        self.drop("url")
        self.drop("title")
        self.drop("fico_range_low")
        self.data["low_inc"] = self.data.annual_inc.apply(lambda x: 1 if x < 60000 else 0)
    
    def get_x(self, variables):
        self.x = self.data[variables]
        
    def adjust_fico(self):
        a = self.data.fico_range_high
        a = a - min(a) + 1
        a = (a / max(a))
        self.data.fico_range_high = np.log(1/a)
    
    def adjust_desc(self):
        self.data.desc = self.data.desc.apply(lambda x: 0 if type(x) == float else max(0,len(x) - 31))
    
    def adjust_dates(self):
        self.data.earliest_cr_line = self.data.earliest_cr_line.apply(lambda x: datetime.datetime.strptime(x, "%b-%Y"))
        self.data.issue_d = self.data.issue_d.apply(lambda x: datetime.datetime.strptime(x, "%b-%Y"))
        self.data["age"] = self.data.issue_d - self.data.earliest_cr_line
        self.data.age = self.data.age.convert_objects(convert_timedeltas=True)
        self.data.age = self.data.age.apply(lambda x: np.timedelta64(x,"D").astype(float) / 365)

    def plot(self, var):
        return ggplot(self.data, aes(x=var, fill="loan_status")) + geom_density()
    
    def plot_facet(self, var):
        return ggplot(self.data, aes(x=var, fill="loan_status")) + geom_density() + facet_grid("grade")

    def interact(self, cts, dscrt):
        self.x = self.x.join(pd.DataFrame({v:cts*pd.get_dummies(dscrt)[v] for v in unique(dscrt)}))
        
    def test_vars(self):
        self.data["high_early"] = self.data.annual_inc / self.data.age        
        self.data["inq_per_year"] = self.data.open_acc / self.data.age
        self.data["good_renewable"] = self.data.grade.map({"A":1,"B":1,"C":1,"D":0,"E":0,"F":0,"G":0}) * self.data.purpose.apply(lambda x: 1 if x == "renewable_energy" else 0)
        self.data["small_biz"] = self.data.purpose.apply(lambda x: 1 if x == "small_business" else 0)
        self.data["wedding"] = self.data.purpose.apply(lambda x: 1 if x == "wedding" else 0)
        self.data["mntly_inc"] = self.data.annual_inc / 12
        self.data.dti = self.data.dti / 100
        self.data["mntly_pay"] = self.data.mntly_inc * self.data.dti
        self.data.mntly_pay += self.data.installment
        self.data["ndti"] = self.data.mntly_pay / self.data.mntly_inc
        self.data["dti_incr"] = (self.data.ndti - self.data.dti)
        self.data.dti_incr = self.data.dti_incr.apply(lambda x: 0 if x == inf else x)
        self.data["dtindti"] = self.data.dti_incr/self.data.ndti
        self.data["fico_decline"] = 850 - self.data.fico_range_high
        self.data["fico_decline_py"] = self.data.fico_decline / self.data.age
        self.data["la"] = self.data.loan_amnt.apply(lambda x: 1 if x > 14000 else 0)
        self.data.term = self.data.term.apply(lambda x: 1 if x == " 60 months" else 0)
        self.data["lowfunded"] = self.data.funded.apply(lambda x: 1 if x <0.9 else 0)
        self.data["ca"] = self.data.state_addr == "CA"
        self.data["fl"] = self.data.state_addr == "FL"
        self.data["mrtg"] = self.data.home_ownership == "MORTGAGE"
            
lc = LendingClub("loandata.csv")
lc.test_vars()
lc.adjust_fico()
lc.adjust_desc()
lc.adjust_dates()
