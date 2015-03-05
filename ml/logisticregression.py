import sklearn.linear_model as lm
from sklearn import cross_validation
import pandas as pd
import numpy as np

class Logistic():
    
    def __init__(self, x, y):
        self.x_test = None
        self.y_test = None
        self.x_train = None
        self.y_train = None
        self.split(x,y)
        self.yhat = None

    def fit(self):
        logit = lm.LogisticRegression()
        model = logit.fit(self.x_train, self.y_train)
        self.yhat = model.predict(self.x_test)        
        
    def split(self,x,y):
        self.x_train, self.x_test, self.y_train, self.y_test = cross_validation.train_test_split(x, y, test_size=0.2)
    
    def eval(self):
        y = pd.DataFrame({'y':self.y_test,'x':self.yhat})
        tp = len(y.query('x == 1 & y == 1'))
        fp = len(y.query('x == 1 & y == 0'))
        fn = len(y.query('x == 0 & y == 1'))
        tn = len(y.query('x == 0 & y == 0'))
        print 'There are: ' + str(tp) + ' true positives'
        print 'There are: ' + str(fp) + ' false positives'
        print 'There are: ' + str(fn) + ' false negatives'
        print 'There are: ' + str(tn) + ' true negatives'
        
