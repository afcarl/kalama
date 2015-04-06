import config
import importlib
from scipy import sparse
from sklearn import preprocessing
from sklearn.externals import joblib
from util.cryo import cryo


def featurize(data):
    """
    Build features the data.
    """
    scalr = preprocessing.StandardScaler()

    # Build features.
    feats = [f(data) for f in featurizers.values()]
    X = sparse.hstack(feats)
    X = scalr.fit_transform(X.todense())
    y = data[config.label].as_matrix()

    return X, y



def _cryo_func(path, featurizer):
    """
    Build separate cryo'd func for featurizing data.
    We don't cryo the aggregate features because we want to be able to hot-swap featurizers.
    """
    @cryo('features', path, ['sampling', path], dtype='other')
    def _featurize(data):
        return featurizer.featurize(data)

    return _featurize


# Load featurizers specified in the config.
featurizers = {}
for name, kwargs in config.features.items():
    # This assumes that the keys for feature configs are the same
    # as their module names, e.g. features.foo's config is at config.features['foo'].
    root = '.'.join(__name__.split('.')[:-1])
    path = 'features.{0}'.format(name)
    mod = importlib.import_module('{0}.{1}'.format(root, path))
    featurizer = mod.Featurizer(**kwargs)
    featurizers[name] = _cryo_func(path, featurizer)

