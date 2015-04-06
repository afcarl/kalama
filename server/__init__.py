import json
import numpy as np
import pandas as pd
from operator import itemgetter
from flask import Flask, render_template, request

import config
from kalama.geiger import highlights
from util.morph import morph_comments

app = Flask(__name__, static_folder='static', static_url_path='')


data = None
@app.route('/ludovico/')
@app.route('/ludovico/<type>')
def ludovico(type='picks'):
    """
    Displays a random comment of the specified type.
    """

    global data
    data = pd.read_csv('notebooks/comments.csv')
    # Randomize data.
    c = data.reindex(np.random.permutation(data.index))

    if type == 'picks':
        c = c[data.editorsSelection == 1].iloc[0].to_dict()
    elif type == 'approved':
        c = c[data.label == 1].iloc[0].to_dict()
    else:
        c = c.iloc[0].to_dict()

    if c['editorsSelection'] == 1:
        status = 'pick'
    elif c['label'] == 1:
        status = 'approved'
    else:
        status = 'rejected'

    return render_template('index.html', comment=c['commentBody'], asset=c['assetBody'], status=status)


@app.route('/compare/')
@app.route('/compare/<int:id>')
def compare(id=0):
    with open(config.crosssample_path, 'r') as f:
        all_comments = json.load(f)

    comments = sorted(all_comments.items(), key=itemgetter(0))[id][1]
    return render_template('compare.html', nyt=comments['nyt'], reddit=comments['reddit'])


@app.route('/comments/')
@app.route('/comments/<int:id>')
def view_comments(id=0):
    with open(config.crosssample_path, 'r') as f:
        all_comments = json.load(f)

    sources = request.args['sources'].split(',') if 'sources' in request.args else ['nyt', 'reddit']
    filter = request.args['filter'] if 'filter' in request.args else 'rchron'

    # Keep some consistency to the sorting. Heiiiinous
    raw_comments = sorted(all_comments.items(), key=itemgetter(0))[id][1]
    subject = raw_comments['subject']

    # Convert from raw comment dicts into Commentable objects.
    comments = []
    for source in sources:
        comments += morph_comments(raw_comments[source], source)

    if filter == 'rchron':
        comments.sort(key=lambda c: c.created_at, reverse=True)
    elif filter == 'score':
        comments.sort(key=lambda c: c.score, reverse=True)
    elif filter == 'dredd_comment':
        pass
    elif filter == 'dredd_discussion':
        pass
    elif filter == 'geiger':
        comments = highlights(comments)
        comments.sort(key=lambda c: c.score, reverse=True)

    return render_template('comments.html', subject=subject, comments=comments)
