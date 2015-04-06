"""
Cross-comparison of NYT comments vs Reddit comments for the same article (url).
"""

import math
import json
import praw
import config
import pandas as pd
from sampling.datastore import db

def main():
    r = praw.Reddit(user_agent='python:co.publicscience.reddit_comments:v0.1 (by /u/don_chow)')

    # Select assets with more than n comments.
    n = 500
    assets = load_assets()
    assets = assets[assets.commentCount > n]

    print('There are {0} assets with more than {1} comments'.format(len(assets), n))

    max_num = 20
    data = {}
    # See which assets are also on reddit.
    for d in list(assets.iterrows()):
        d = d[1]
        url = d.assetUrl
        body = d.assetBody

        print('Trying {0}'.format(url))
        results = [s for s in r.search(url)]

        if not results:
            print('\tNo results on reddit, skipping...')
            continue

        # Find the top submission.
        top_submission = max(results, key=lambda s: s.score)

        print('\tLoading comments for {0}...'.format(top_submission.title))
        top_submission.replace_more_comments()
        if len(top_submission.comments) <= 50:
            print('\tNot enough comments (only {0}), skipping...'.format(len(top_submission.comments)))
            continue

        data[url] = {
            'subject': body,

            # Load comments for the submission.
            'reddit': [parse_reddit_comment(c) for c in top_submission.comments],
            'nyt': get_nyt_comments(d.assetID)
        }

        with open(config.crosssample_path, 'w') as f:
            json.dump(data, f)

        if len(data) >= max_num:
            return


def load_assets():
    """
    Load assets from 2014.
    """
    query = """
    SELECT
        assetID,
        assetUrl,
        assetBody,
        (SELECT COUNT(*) FROM crnr_comment WHERE assets.assetID = crnr_comment.assetID) as commentCount
    FROM assets
    WHERE (YEAR(pubDate) = 2014)
    """
    return pd.read_sql(query, db)


def get_nyt_comments(asset_id):
    query = """
    SELECT
        commentID,
        commentBody,
        createDate,
        parentID,
        isReply,
        userDisplayName,
        recommendationCount
    FROM crnr_comment
    WHERE (assetID = {0}) AND
          (statusID = 2) AND
          (commentBody IS NOT NULL) AND
          (commentBody != '')
    """.format(asset_id)
    df = pd.read_sql(query, db)
    df['createDate'] = df['createDate'].map(lambda d: d.isoformat())
    return df.to_dict(orient='records')


def parse_reddit_comment(c):
    return {
        'id': c.id,
        'parent_id': c.parent_id,
        'is_root': c.is_root,
        'permalink': c.permalink,
        'replies': [parse_reddit_comment(r) for r in c.replies],
        'gilded': c.gilded,
        'author': None if c.author is None else c.author.name,
        'body': c.body,
        'body_html': c.body_html,
        'controversiality': c.controversiality,
        'created': c.created_utc,
        'ups': c.ups,
        'downs': c.downs,
        'score': c.score,
        'edited': c.edited,
        'distinguished': c.distinguished,
        'flair': c.author_flair_text
    }


def build_nyt_threads(nyt_comments):
    """
    The NYT comments data is flat, so rebuild the thread hierarchy.
    """

    # Rebuild as dict.
    nyt_comments = {c['commentID']:c for c in nyt_comments}

    max_depth = 0
    for c in nyt_comments.values():
        c['replies'] = []
        depth = 0

        # Calculate the depth of the comments
        # so we know in what order to assemble threads.
        c_ = c
        while not math.isnan(c_['parentID']):
            depth += 1
            try:
                c_ = nyt_comments[c_['parentID']]
            except KeyError:
                break

        if depth > max_depth:
            max_depth = depth

        c['depth'] = depth

    # Start by attaching the deepest comments to their parents,
    # then the go up a level and repeat.
    for i in range(max_depth, 0, -1):
        for c in nyt_comments.values():
            if c['depth'] == i:
                try:
                    nyt_comments[c['parentID']]['replies'].append(c)
                except KeyError:
                    break

    # Then just take the top-level stuff.
    threads = [c for c in nyt_comments.values() if c['depth'] == 0]

    return threads


def process_comments():
    print('Processing comments...')
    with open(config.crosssample_path, 'r') as f:
        comments = json.load(f)

    for key in comments.keys():
        comments[key]['nyt'] = build_nyt_threads(comments[key]['nyt'])

    with open(config.crosssample_path, 'w') as f:
        json.dump(comments, f)


if __name__ == '__main__':
    main()
    process_comments()
