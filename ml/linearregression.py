import statsmodels.api as sm
import sklearn.linear_model as lm
import numpy as np
from ggplot import *

class LinearRegression():
    def __init__(self, x, y, method="matrix", intercept=True):
        self.x = x.convert_objects(convert_numeric=True)
        self.y = y.convert_objects(convert_numeric=True)
        self.method = method
        self.intercept = intercept
        self.yhat = None
        self.residuals = None
        
    def fit_model(self):
        self.x = sm.add_constant(self.x)
        rslt = sm.OLS(self.y, self.x).fit()
        self.yhat = rslt.predict(self.x)
        self.residuals = self.y - self.yhat
        print rslt.summary()
    
    def plot_residuals(self, variable):
        df = pd.DataFrame(dict(x = variable, y = self.residuals))
        return ggplot(df, aes(x="x", y="y")) + geom_point()
    
    def add_poly(self, variable, degree):
        degree = list(degree)
        for p in degree:
            name = str(variable) + "_" + str(p)
            self.x[name] = self.x[variable]**p

class Linear():
    def __init__(self, x, y, method="Matrix", intercept=True):
        self.x = x.convert_objects(convert_numeric=True)
        self.y = y.convert_objects(convert_numeric=True)
    
    def fit_model(self):
        lin = lm.LinearRegression(fit_intercept=intercept)
        
