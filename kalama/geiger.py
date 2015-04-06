"""
Geiger clusters comments to generate a _gist_ of what's happening.

pip install numexpr cython
pip install git+git://github.com/ftzeng/galaxy
"""

import numpy as np
from galaxy.cluster.ihac import Hierarchy
from util.text import Vectorizer, strip_tags
from config import geiger_path
from util.logging import log
from sklearn.externals import joblib

def highlights(comments, min_size=5, dist_cutoff=0.5):
    """
    This takes a set of comments,
    clusters them, and then returns representatives from clusters above
    some threshold size.

    Args:
        | comments      -- list of Commentables
        | min_size      -- int, minimium cluster size to consider
        | dist_cutoff   -- float, the density at which to snip the hierarchy for clusters

    Future improvements:
        - Persist hierarchies instead of rebuilding from scratch (using Hierarchy.load & Hierarchy.save)
        - Tweak min_size and dist_cutoff for the domain.
    """
    v = joblib.load(geiger_path)
    vecs = v.vectorize([strip_tags(c.body) for c in comments], train=False)
    vecs = vecs.toarray()

    log.info('Clustering {0} comments...'.format(vecs.shape[0]))

    # Build the hierarchy.
    h = Hierarchy(metric='cosine', lower_limit_scale=0.9, upper_limit_scale=1.2)
    ids = h.fit(vecs)

    log.info('Processing resulting clusters...')

    # Build a map of hierarchy ids to comments.
    map = {ids[i]: c for i, c in enumerate(comments)}

    # Generate the clusters.
    clusters = h.clusters(distance_threshold=dist_cutoff, with_labels=False)

    # Filter to clusters of at least some minimum size.
    clusters = [c for c in clusters if len(c) >= min_size]

    # Get the clusters as comments.
    clusters = [[map[id] for id in clus] for clus in clusters]

    # From each cluster, pick the comment with the highest score.
    highlights = [max(clus, key=lambda c: c.score) for clus in clusters]

    # Suppress replies, show only top-level.
    for h in highlights:
        h.replies = []

    log.info('Done.')

    return highlights
