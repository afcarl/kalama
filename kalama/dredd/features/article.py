import numpy as np
from util import text
from scipy.spatial.distance import cosine
from scipy.sparse import vstack


class Featurizer():
    def __init__(self, metric='cosine', hash=True):
        # Use a hashing vectorizer to reduce memory load.
        self.vectr = text.Vectorizer(hash=hash)
        self.metric = metric

    def featurize(self, data):
        """
        Calculate asset relevance by cosine distance.

        The vectorizer is trained on the assets rather than the comments.
        """
        # Get only unique assets.
        deduped = data.drop_duplicates(subset=['assetID'], inplace=False)

        print('Vectorizing assets...')

        # Vectorize assets.
        asset_vecs = self.vectr.vectorize(deduped['assetBody'], train=True)

        print('Mapping assets...')

        # Map asset ids to their vector's index.
        asset_map = {}
        asset_ids = list(deduped['assetID'])
        for i, id in enumerate(asset_ids):
            #asset_map[id] = uniq_asset_vecs[i]
            asset_map[id] = i

        # Map comments to their asset's vector index.
        comment_to_asset_indices = [asset_map[id] for id in data.assetID]

        print('Vectorizing comments...')
        comment_vecs = self.vectr.vectorize(data['commentBody'])

        print('Calculating distances...')
        # Is there a faster way to calculate row-wise distances?
        sims = [1 - cosine(comment_vecs[i], asset_vecs[asset_map[id]]) for i, id in enumerate(data.assetID)]
        sims = np.array(sims)

        # Not sure how these nans are resulting, but set them to 0.
        sims = np.nan_to_num(sims)

        # Make it 2D.
        return np.reshape(sims, (-1, 1))
