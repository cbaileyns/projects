import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breushpagan
import numpy as np
import pandas as pd
from ggplot import *
from sklearn import cross_validation
from scipy.stats.stats import pearsonr
from statsmodels.stats.stattools import jarque_bera


class LinearRegression():
    def __init__(self, x, y, method="matrix", intercept=True):
        x = x.convert_objects(convert_numeric=True)
        y = y.convert_objects(convert_numeric=True)
        self.columns = x.columns
        self.x_train = None 
        self.y_train = None
        self.x_test = None
        self.y_test = None
        self.method = method
        self.intercept = intercept
        if intercept:
            self.add_intercept(x)
        self.split(x,y)
        self.yhat = None
        self.residuals = None
        self.ypred = None
        self.resids_is = None
        self.resids_oos = None
        
    def split(self, x, y):
        self.x_train, self.x_test, self.y_train, self.y_test = cross_validation.train_test_split(x, y, test_size=0.2)
    
    def add_intercept(self,x):
        x["const"] = np.ones(len(x))
    
    def fit_model(self):
        rslt = sm.OLS(self.y_train, self.x_train).fit()
        self.yhat = rslt.predict(self.x_train)
        self.ypred = rslt.predict(self.x_test)
        self.resids_is = self.y_train - self.yhat
        self.resids_oos = self.y_test - self.ypred
        print rslt.summary()
    
    def plot_insample_residuals(self, variable):
        i = 1 if type(self.columns) == str else list(self.columns).index(variable)
        print i
        print sum(self.x_train[:,i] == 0)
        df = pd.DataFrame(dict(x = self.x_train[:,i], y = self.resids_is))
        return ggplot(df, aes(x="x", y="y")) + geom_point()
    
    def plot_outofsample_residuals(self, variable):
        i = 1 if type(self.columns) == str else list(self.columns).index(variable)
        print i
        print sum(self.x_test[:,i] == 0)
        df = pd.DataFrame(dict(x = self.x_test[:,i], y = self.resids_oos))
        return ggplot(df, aes(x="x", y="y")) + geom_point()
    
    def get_cor(self,variable, p):
        i = 1 if type(self.columns) == str else list(self.columns).index(variable)
        result = pearsonr(self.x_train[:,i],self.resids_is)
        if result[1] > p:
            print "The errors are not correlated with the specificed endogenous variable"
            print "Computed correlation: " + str(round(result[0],4))
        else:
            print "The errors are correlated with the specificed endogenous variable"
            print "Computed correlation: " + str(round(result[0],4))
        
    def test_homosked(self,variable, p):
        i = 1 if type(self.columns) == str else list(self.columns).index(variable)
        result = het_breushpagan(self.resids_is,self.x_train[:,[0,i]])
        if result[1] > p or result[3] > p:
            print "The error variance is determined to be constant as the endogenous variable varies"
            print "LM Stat: " + str(round(result[0],4))
            print "F-value: " + str(round(result[2],4))
        else:
            print "The error variance changes with the endogenous variable"
            print "LM Stat: " + str(round(result[0],4))
            print "F-value: " + str(round(result[2],4))
    
    def plot_is_resid_pdf(self):
        return ggplot(pd.DataFrame(dict(x = self.resids_is)),aes(x="x")) + geom_density()

    def plot_oos_resid_pdf(self):
        return ggplot(pd.DataFrame(dict(x = self.resids_oos)),aes(x="x")) + geom_density()

    def test_error_normality(self, p):
        insamp = jarque_bera(self.resids_is)
        outsamp = jarque_bera(self.resids_oos)
        print "In sample JB stat: " + str(round(insamp[0],4))
        if insamp[1] > p:
            print "The errors are likely normal"
        else:
            print "The errors are unlikely to be normal"
        print "Out of sample JB stat: " + str(round(outsamp[1],4))
        if outsamp[0] > p:
            print "The errors are likely normal"
        else:
            print "The errors are unlikely to be normal"
