"""
Handles processing and construction of features.
"""

from math import sqrt
from scipy import sparse


class Featurizer():
    def __init__(self, features=[]):
        self.features = features

    def featurize(self, data):
        data = self._user_features(data)

        # Select only the specified features.
        data = data[self.features]

        return sparse.coo_matrix(data)

    def _user_features(self, data):
        """
        User (reputation) features
        """
        data['ONE'] = 1
        groups = data.sort('createDate').groupby(['userID'])

        # The `label` column is whether or not the comment was approved.
        data['userApprovalCount'] = groups.label.cumsum()
        data['userCommentCount'] = groups.ONE.cumsum()
        data['userRecommendationCount'] = groups.recommendationCount.cumsum()
        data['userRejectedCount'] = data['userCommentCount'] - data['userApprovalCount']
        data['userApprovalRatio'] = data['userApprovalCount']/data['userCommentCount'].apply(float)
        data['userAverageRecommendation'] = data['userRecommendationCount']/data['userCommentCount'].apply(float)
        data['userApprovalWilson'] = data.apply(self._confidence, axis=1)

        # Cleanup
        data = data.drop(['ONE'], axis=1)

        return data

    def _confidence(self, row):
        """
        Wilson Score Confidence Interval
        Adapted from: <https://possiblywrong.wordpress.com/2011/06/05/reddits-comment-ranking-algorithm/>
        """
        ups = row['userApprovalCount']
        downs = row['userRejectedCount']
        n = ups + downs
        z = 1.64485  # 95% confidence interval
        p_hat = float(ups)/n
        return (p_hat+z*z/(2*n)-z*sqrt((p_hat*(1-p_hat)+z*z/(4*n))/n))/(1+z*z/n)

