import sys
import click
import config
import pandas as pd
from server import app
from sklearn.externals import joblib
from kalama.dredd import models, features
from kalama.dredd.sampling import Sampler
from util.logging import log
from util import eval, cryo
from util.text import Vectorizer, strip_tags, html_decode


@click.group()
def cli():
    pass


@cli.command()
@click.option('--refresh', default=None)
def dredd(refresh):
    """
    Evaluate Dredd's performance on a task.
    """
    if refresh is not None:
        stage = refresh
        names = [s[0] for s in cryo.stages]
        i = names.index(stage)
        cryo.stages[i] = (stage, True)

    data = Sampler().sample()
    log.info('Data set includes {0} examples...'.format(data.shape[0]))


    log.info('Building features...')
    X, y = features.featurize(data)
    log.info('Using {0} features...'.format(X.shape[1]))

    X_train, y_train, X_test, y_test = eval.cross_validation_split(X, y, test_size=config.test_size)
    log.info('Training on {0} examples...'.format(X_train.shape[0]))
    log.info('Testing on {0} examples...'.format(X_test.shape[0]))


    log.info('Training model...')
    m = models.Model(**config.model['params'])
    m.train(X_train, y_train)

    log.info('Testing model...')
    scores = m.evaluate(X_test, y_test, **config.model['eval'])
    print(eval.report(config, X_train, X_test, scores))

    #for c in m.rank(data_test, X_test).head().iterrows():
        #print('[{0}] {1}'.format(c[1].score, c[1].commentBody))


@cli.command()
def build_notebook_data():
    """
    Prepare the sample data for use in an iPython notebook.
    """
    data = Sampler().sample()
    user_rep = features.user.Featurizer(**config.features['user']).featurize(data).todense()

    asset_relevance = features.article.Featurizer().featurize(data)
    data['assetRelevance'] = asset_relevance

    data.to_csv('notebooks/comments.csv', mode='w', encoding='utf-8')


@cli.command()
@click.argument('model', type=click.Choice(['geiger', 'dredd']))
def train(model):
    """
    Trains the specified model on the sampler data.
    """
    if model == 'geiger':
        data = Sampler().sample()
        v = Vectorizer()
        comments = [strip_tags(html_decode(c)) for c in data['commentBody'].to_dict().values()]
        v.vectorize(comments, train=True)
        joblib.dump(v, 'geiger_vec.pkl')

    elif model == 'dredd':
        data = Sampler().sample()
        print('Data set includes {0} examples...'.format(data.shape[0]))

        print('Building features...')
        X, y = features.featurize(data)
        print('Using {0} features...'.format(X.shape[1]))

        X_train, y_train, X_test, y_test = eval.cross_validation_split(X, y, test_size=0.0)
        print('Training on {0} examples...'.format(X_train.shape[0]))

        print('Training model...')
        m = models.Model(**config.model['params'])
        m.train(X_train, y_train)

        joblib.dump(m, 'dredd_model.pkl')


@cli.command()
def run_server():
    """
    Run the demo server.
    """
    app.run(debug=True, port=5001)


if __name__ == '__main__':
    cli()