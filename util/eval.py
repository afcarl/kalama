import json
from util.cryo import freezer
import numpy as np


def cross_validation_split(features, labels, test_size=0.4):
    """
    Splits a DataFrame into a random training and testing set.

    Args:
        | test_size (float)     -- what portion of the data to use for testing
    """

    # Shuffle the data.
    assert len(features) == len(labels)
    shuffled = np.random.permutation(len(features))
    labels   = labels[shuffled]
    features = features[shuffled]

    # Split the data.
    split = (int)(test_size * len(features))
    feat_test    = features[:split]
    feat_train   = features[split:]
    labels_test  = labels[:split]
    labels_train = labels[split:]

    return feat_train, labels_train, feat_test, labels_test


def report(config, X_train, X_test, scores):
    """
    Output a simple evaluation report.
    """
    out_dict = {k: getattr(config, k) for k in dir(config) if k[0] != '_'}
    out_dict['_scores'] = scores
    out_dict['_data'] = {
            'num_train': X_train.shape[0],
            'num_test':  X_test.shape[0]
    }
    out_dict['_freezer'] = freezer
    return json.dumps(out_dict, sort_keys=True, indent=4)
