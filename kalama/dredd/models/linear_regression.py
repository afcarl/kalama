from sklearn import linear_model
from sklearn import metrics


class Model():
    def __init__(self):
        self._m = linear_model.LinearRegression()

    def train(self, X_train, y_train):
        self._m.fit(X_train, y_train)

    def evaluate(self, X_test, y_test):
        y_pred = self._m.predict(X_test)

        r2 = metrics.r2_score(y_test, y_pred)
        return {
            'r2': r2
        }
