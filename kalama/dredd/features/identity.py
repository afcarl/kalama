from scipy import sparse


class Featurizer():
    """
    The identity featurizer selects the specified features
    from the original data, without affecting them.
    """
    def __init__(self, features=[]):
        self.features = features

    def featurize(self, data):
        # TO DO this would need to create the necessary indicator values
        # for non-numerical data.
        return sparse.coo_matrix(data[self.features])
