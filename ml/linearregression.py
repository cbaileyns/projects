import statsmodels.api as sm
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
        

df = toronto.frame[["price","sqft"]]
df = df[df.price != "350000"]
df = df[df.sqft != ""]

apartments = LinearRegression(df.sqft, df.price)
apartments.fit_model()
apartments.plot_residuals(apartments.x.sqft)
