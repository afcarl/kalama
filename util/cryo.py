"""
The `cryo` module memoizes large data processing functions.

It provides the `cryo` decorator which can be used to wrap any function which returns
data (as a dataframe or a numpy array). The returned data is saved for that particular
config and reloaded as needed, skipping redundant processing.
"""

import os
import json
import hashlib
from functools import wraps

import pandas as pd
from sklearn.externals import joblib

import config
from util.logging import log

stages = [('sampling', False), ('features', False), ('model', False)]
freezer = []


def cryo(stage, path, dep_keys, dtype='dataframe'):
    """
    Decorator for freezing/unfreezing as necessary.

    Use this on functions which process and return data.
    The decorator will load existing data if it is available,
    and the underlying function will not be called.

    Otherwise, it will run the function then freeze and return the result.

    If any one cryo call requires freshly processing the data, any data later in the
    pipeline is invalidated, so all subsequent calls will also reprocess the data.

    Args:
        | stage (str)       -- the stage name
        | path (str)        -- the path the frozen data will be stored at
        | dep_keys (list)   -- list of config keys this stage depends on
        | dtype (str)       -- the expected returned dtype: ['dataframe', 'other']
    """
    def cryo_dec(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            global freezer
            sig = _signature(dep_keys)
            fpath = _build_path(dtype, path, sig)

            freezer.append(fpath)

            if _preserved(fpath) and not _refresh(stage):
                log.info('Defreezing {0} (sig:{1})...'.format(path, sig))
                return _defreeze(fpath)

            else:
                log.info('Running {0}...'.format(path))
                data = f(*args, **kwargs)

                log.info('Freezing {0} (sig:{1})...'.format(path, sig))
                # TO DO this needs to set the refresh flag for the stage.
                _freeze(data, fpath)
                return data
        return decorated
    return cryo_dec


def _freeze(data, fpath):
    fdir = os.path.dirname(fpath)
    if not os.path.exists(fdir):
        os.makedirs(fdir)

    if isinstance(data, pd.DataFrame):
        data.to_csv(fpath, mode='w', encoding='utf-8')
    else:
        joblib.dump(data, fpath)


def _defreeze(fpath):
    ext = os.path.splitext(fpath)[1]
    if ext == '.csv':
        return pd.read_csv(fpath, index_col=0, lineterminator='\n')
    else:
        return joblib.load(fpath)


def _preserved(fpath):
    return os.path.exists(fpath)


def _build_path(dtype, path, sig):
    ext = '.csv' if dtype == 'dataframe' else '.pkl'
    return os.path.join(config.data_root, path, sig) + ext


def _signature(dep_keys):
    """
    Builds a hash signature for a particular config.
    THe hash signature is based on a serialized form of the config.

    The signature is built from the config values at the specified `dep_keys`.
    """
    conf = {}
    for key in dep_keys:
        keys = key.split('.')
        d = getattr(config, keys[0])
        for subkey in keys[1:]:
            d = d[subkey]
        conf[key] = d
    conf = json.dumps(conf, sort_keys=True).encode('utf-8')
    return hashlib.md5(conf).hexdigest()


def _refresh(stage):
    """
    Checks if the stage previous to the passed one was refreshed.
    If true, refresh this stage as well.
    """
    names = [s[0] for s in stages]
    i = names.index(stage)

    # If the first stage, just return its own value.
    if i == 0:
        return stages[i][1]

    # Otherwise, return the value of the previous stage.
    elif stages[i][1] or stages[i-1][1]:
        stages[i] = (stage, True)
        return True
