import pandas as pd
import numpy as np
import datetime
from ggplot import *
from logisticregression import Logistic
from pandasql import *

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
        self.drop("sub_grade")
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
        
lc = LendingClub("loandata.csv")
lc.adjust_fico()
lc.adjust_desc()
lc.adjust_dates()
lc.get_x(["fico_range_high","open_acc","funded","unemployed","int_rate","revol_util","dti"])
lc.interact(lc.data.loan_amnt, lc.data.grade)
lc.test_vars()

l = Logistic(lc.x.values, lc.y)
l.fit()

l.eval()

lc.plot("loan_amnt") #default the higher the larger the loan
lc.plot_facet("loan_amnt")
lc.plot_facet("revol_util")
lc.plot("dti")
lc.plot_facet("dti")

lc.plot("age")
lc.plot_facet("age")

lc.plot("annual_inc")
lc.plot_facet("annual_inc") #noticably more defaults when income is less than 60k
lc.plot("high_early") #earn money faster -> less default chances
lc.plot("inq_per_year")


df = lc.data
query = '''select a.purpose, a.grade, sum(a.loan_status) / count(a.purpose), count(a.grade) from df a group by a.purpose, a.grade'''
f = sqldf(query, locals())
pd.DataFrame.to_csv(f,"purpose.csv")

query = '''select a.grade, sum(a.loan_status) / count(a.grade), count(a.grade) from df a group by a.grade'''
g = sqldf(query, locals())
pd.DataFrame.to_csv(g, "grade.csv")

a = pd.crosstab([lc.data.grade,lc.data.inq_last_6mths],lc.data.loan_status)
a[2] = a[1]/(a[0]+a[1])
#p(D) increases across most grades as inquiries increase

a = pd.cut(lc.data.mths_since_last_record,10)
b = pd.DataFrame({"bin":a,"result":lc.data.loan_status,"grade":lc.data.grade})
c = pd.crosstab(b.bin,b.result)
c[2] = c[1]/c[0]

lc.data["mntly_inc"] = lc.data.annual_inc / 12
lc.data.dti = lc.data.dti / 100
lc.data["mntly_pay"] = lc.data.mntly_inc * lc.data.dti
lc.data.mntly_pay += lc.data.installment
lc.data["ndti"] = lc.data.mntly_pay / lc.data.mntly_inc
lc.data["dti_incr"] = (lc.data.ndti - lc.data.dti)
lc.data.dti_incr = lc.data.dti_incr.apply(lambda x: 0 if x == inf else x)
lc.data["dtindti"] = lc.data.dti_incr/lc.data.ndti
