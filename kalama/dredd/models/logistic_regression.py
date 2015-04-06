import pandas as pd
from sklearn import linear_model
from sklearn import metrics


class Model():
    def __init__(self):
        self._m = linear_model.LogisticRegression('l2', class_weight={1: 1})

    def train(self, X_train, y_train):
        self._m.fit(X_train, y_train)

    def evaluate(self, X_test, y_test, threshold=None):
        if threshold is None: y_pred = self._m.predict(X_test)
        else:
            y_prob = self._m.predict_proba(X_test)

            # Get predictions for the positive (1) class.
            y_pred = y_prob[:,1]
            y_pred[y_pred > threshold] = 1
            y_pred[y_pred != 1] = 0
            y_pred = y_pred.astype(int)

        accuracy = metrics.accuracy_score(y_test, y_pred)
        precision = metrics.precision_score(y_test, y_pred)
        recall = metrics.recall_score(y_test, y_pred)
        roc_auc = metrics.roc_auc_score(y_test, y_pred)
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'roc_auc': roc_auc,
            'coef': list(self._m.coef_[0])
        }

    def rank(self, data_test, X_test):
        y_prob = self._m.predict_proba(X_test)[:,1]
        probs = pd.DataFrame(y_prob, columns=['score'])
        ranked = pd.concat([data_test, probs], axis=1)
        return ranked.sort('score', ascending=False)

