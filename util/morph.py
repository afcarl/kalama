"""
Converts from other comment structures (e.g. NYT or Reddit) to Kalama commentable objects.
"""

from datetime import datetime
from util.text import html_decode
from kalama.models import Commentable


def morph_comments(comments, source):
    """
    Morphs a set of raw comments (in dict form) into Commentables.
    This preserves thread structure.
    """
    map = {
        'nyt': {
            'commentBody': 'body',
            'createDate': 'created_at',
            'commentID': 'id',
            'userDisplayName': 'author',
            'recommendationCount': 'score'
        },
        'reddit': {
            'body_html': 'body',
            'created': 'created_at',
            'id': 'id',
            'author': 'author',
            'score': 'score'
        }
    }
    morphed = [morph(c, map[source]) for c in comments]
    return normalize_scores(morphed)


def morph(comment, map, reply_key='replies'):
    """
    Morph a single raw comment into a Commentable.
    """
    c = Commentable()

    for k, v in map.items():
        val = comment[k]
        if v == 'created_at':
            raw = comment[k]
            if isinstance(comment[k], float): # Epoch
                val = datetime.fromtimestamp(raw)
            else:
                val = datetime.strptime(raw, '%Y-%m-%dT%H:%M:%S')
        elif v == 'body':
            val = html_decode(val)

        setattr(c, v, val)

    c.replies = []
    for r in comment[reply_key]:
        reply = morph(r, map)
        reply.parent = c
        c.replies.append(reply)

    return c


def normalize_scores(comments):
    """
    Normalize scores of a list of Commentables.
    """

    # Flatten threads.
    flat = [c for c in _flatten(comments)]

    best = max(flat, key=lambda c: c.score).score
    for c in flat:
        c.score /= best
    return comments


def _flatten(comments):
    for c in comments:
        for r in _flatten(c.replies):
            yield r
        yield c
