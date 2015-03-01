import statsmodels.api as sm
import numpy as np

class LinearRegression():
    def __init__(self, x, y, method="matrix", intercept=True):
        self.x = x
        self.y = y
        self.method = method
        self.intercept = intercept
        
    def fit_model(self):
        self.x = sm.add_constant(self.x)
        rslt = sm.OLS(self.y, self.x)
        print rslt.summary()
        

x = toronto.frame[["price","sqft"]]
x = x[x.sqft != ""]

apartments = LinearRegression(x.sqft, x.price)
