sampling = {
    'n_users': 200000
}

#model = {
    #'name': 'logistic_regression',
    #'params': {},
    #'eval': {
        #'threshold': 0.85
    #}
#}
#label = 'label'
#label = 'editorsSelection'

model = {
    'name': 'linear_regression',
    'params': {},
    'eval': {}
}
label = 'recommendationCount'
test_size = 0.2

# keys = module names to use.
# value = dict of kwargs to pass to the module's `featurize` func.
features = {
    'user': {
        'features': [
            'userApprovalWilson',
            'userAverageRecommendation'
        ]
    },
    'bow': {},
    'article': {
        'metric': 'cosine',
        'hash': True
    },
    'identity': {
        'features': ['commentLength']
    }
}



data_root = 'data/'

db = {
    'host': 'localhost',
    'db': 'otter',
    'user': 'root',
    'passwd': 'password',
    'port': 3306
}




# ---

geiger_path = 'data/geiger/geiger_vec.pkl'
dredd_path = 'data/dredd/dredd_model.pkl'
crosssample_path = 'data/crosssample/comments.json'
