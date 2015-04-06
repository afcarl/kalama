# Kalama

(work in progress)


## Dredd

The Dredd package is for ranking comments/discussions.

### Feature building

Set up featurizers in the `features` package.

Each module in the `features` package should include a `Featurizer` class which implements:

- `__init__(self, **kwargs)` (optional)
- `featurize(self, DataFrame: data, bool: train)`

Featurizers can then be included by writing the modules' names in `config.py`.

For example, if you have the module `features.text` which generates textual features,
you can include it in your `config.py` like so:

    features = {
        'text': {}
    }

The dict after the module name is for specifying kwargs to be passed to the `Featurizer` constructor.

### Models

Models are included as modules in the `models` package.

Each model module should include a `Model` class which implements:

- `train(self, ndarray: X_train, ndarray: y_train, **kwargs)`
- `evaluate(self, ndarray: X_test, ndarray: y_test, **kwargs)`

A model is then specified in `config.py`.

For example, if you have the module `models.logistic_regression`, you'd specify it in `config.py` like so:

    model = {
        'name': 'logistic_regression',
        'params': {},
        'eval': {}
    }

The `params` dict is for kwargs to be passed to the `Model` constructor and
the `eval` dict is for kwargs to be passed to `Model.evaluate`.

### Specifying the task

You can specify the task (i.e. target column/label in your data) for the model in `config.py`:

    label = 'editorsSelection'

### Running

After you have configured everything, you can run and evaluate Dredd like so:

    $ python main.py dredd

### Cryo

The `cryo` module provides a decorator, `cryo`, for memoizing heavy data processing functions.

The output of wrapped functions are "frozen" to disk, identified by a signature generated from the relevant config data. That way, if you modify the config and data already exists for that configuration, the existing data is loaded. This makes it easy, for example, to hot-swap features - already processed features are frozen and only new ones need to be calculated.

### Using the `cryo` decorator

The relevant config data is specified by a list of period-delimited key paths (`dep_keys`) in the `cryo` decorator.

For example, say you have the following config:

    bleh = {
        'foo': 'bar',
        'yo': 'sup'
    }

    other = {
        'hi': 'there'
    }

And say our data processing function's output varies depending on the values of `other` and `test['foo']`. Then our `dep_keys` would be `['other', , 'test.foo']`.

If that function is called again with the same config data and a frozen function result exists, then the existing result is "defrosted" and returned.

If any point during the pipeline some function is run, rather than defrosted, every function in subsequent stages will be re-run (the assumption is that each stage in the pipeline is dependent, so any change at one point invalidates all subsequent points).

### mmm...refreshing

If desired, you can force a refresh for a config, which will cause all functions to run, even if a frozen result already exists (the existing one will be overwritten):

    $ python main.py dredd --refresh

You can also refresh from a specific stage.

    $ python main.py dredd --refresh features


### Stages

The pipeline is broken into _stages_, so there's a consistent structure for `cryo` to rely on.

The stages are:

- _sampling_: samples relevant data from a larger dataset (i.e. pulling it out of a db)
- _features_:
    - splits sampled data into training/test sets
    - builds features for each dataset
- _model_:
    - builds model with the training data
    - evaluates the model on the test data



## Geiger

The Geiger package generates a gist for a set of comments/discussions.

Currently it uses Incremental Hierarchical Agglomerative Clustering so that a hierarchy can be maintained for a given set of comments and new comments can be incorporated in an online fashion.

For smaller comment sets (<~500) it performs at a reasonable speed (though definitely not fast enough to re-process comments on every request), for larger sets it can get quite slow.

Geiger's text vectorization pipeline can be trained using the command:

    $ python main.py train geiger


## Server

The server is for exploring comments. There are a few key routes:

- `/ludovico/<type>` - every 20s, show a random comment from the NYT sample according to `type` (`['picks', 'approved', 'all']`).
- `/compare/<int:id>` - compare the reddit and NYT comments for a given NYT article. This data is collected via `nyt_reddit.py`.
- `/comments/<int:id>` - see comments for a given NYT article. The data used is also that collected by `nyt_reddit.py`. Possible params include:
    - `sources` - which can be one of `['nyt', 'reddit', 'all']`. Defines which comment sets to use. Defaults to `all`.
    - `filter` - which can be one `['rchron', 'score', 'geiger']`. Defaults to `rchron`.
        - `rchron` - sort by reverse chronological order
        - `score` - sort by voting score. For NYT comments, this is based off the recommendation count, for reddit comments, this is based off the comment score. The scores are normalized across both sets.
        - `geiger` - uses the `geiger` package to select highest-rated comments from clustered comments, then sorts by score. As noted above, for large sets of comments (>500), this can get very slow.
