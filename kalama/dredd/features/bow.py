from util import text


class Featurizer():
    def __init__(self):
        self.vectr = text.Vectorizer()

    def featurize(self, data):
        return self.vectr.vectorize(data['commentBody'], train=True)
