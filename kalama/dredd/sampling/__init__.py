import pandas as pd
from .datastore import db

import config
from util.cryo import cryo
from util.logging import log

class Sampler():
    """
    Loads comments data from MySQL.

    Mostly pulled from
    https://github.com/nytm/ugc-safire/blob/master/otter/lib/reader.py
    """

    @cryo('sampling', 'sample', ['sampling'])
    def sample(self):
        log.info('Loading {0} users'.format(config.sampling['n_users']))
        return pd.read_sql(self.query_by_user(), db)

    def query_by_user(self):
        """
        Returns comment data for random subset of n_users.
        """

        return """
        SELECT {0}
        FROM crnr_comment
        JOIN ( {1} ) random_users
        ON (random_users.userID = crnr_comment.userID)

        LEFT JOIN ( {2} ) comment_taxonomy
        ON (comment_taxonomy.commentID = crnr_comment.commentID)

        LEFT JOIN ( {3} ) comment_assets
        ON (comment_assets.assetID = crnr_comment.assetID)

        WHERE
          (statusID = 2 OR statusId = 3) AND
          (commentBody IS NOT NULL) AND
          (commentBody != '') AND
          (assetBody IS NOT NULL) AND
          (assetBody != '')
        """.format(self.all_features(),
                   self.random_sample_of_users_query(),
                   self.comment_taxonomy_query(),
                   self.asset_query())

    def all_features(self):
        return """
        crnr_comment.commentID as commentID,
        crnr_comment.userID as userID,
        REPLACE(commentBody, '\r\n', '\n') as commentBody,
        crnr_comment.createDate as createDate,
        crnr_comment.recommendationCount as recommendationCount,
        crnr_comment.replyCount as replyCount,
        crnr_comment.assetID as assetID,
        crnr_comment.parentID as parentID,
        crnr_comment.editorsSelection as editorsSelection,
        crnr_comment.isReply as isReply,
        commentType,
        CHAR_LENGTH(commentBody) as commentLength,
        userDisplayName,
        userLocation,
        taxonomyList,
        assetBody,
        crnr_comment.statusID as statusID,
        CASE
          WHEN statusID = 2 THEN 1
          WHEN statusID = 3 THEN 0
        END AS label
        """

    def random_sample_of_users_query(self):
        return """
        SELECT
          distinct(userID)
        FROM crnr_comment
        ORDER BY RAND() limit {0}
        """.format(config.sampling['n_users'])

    def comment_taxonomy_query(self):
        return """
        SELECT
          commentID,
          GROUP_CONCAT(taxonomyNode SEPARATOR ',') as taxonomyList
        FROM crnr_taxonomy
        RIGHT JOIN crnr_comment_taxonomy_asset_user_map
        ON (crnr_taxonomy.taxonomyID = crnr_comment_taxonomy_asset_user_map.taxonomyID)
        GROUP BY commentID
        """

    def asset_query(self):
        return """
        SELECT assetBody, assetID
        FROM assets
        """
