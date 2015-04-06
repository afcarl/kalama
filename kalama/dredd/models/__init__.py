"""
Models modules should include a class named `Model`.
"""

import config
import importlib

# Load the model specified in the config.
Model = importlib.import_module('kalama.dredd.models.{0}'.format(config.model['name'])).Model
