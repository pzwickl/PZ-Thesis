"""Module that imports the json module and monkey-patches it so
JSONEncoder.default() automatically pickles any Python objects
encountered that aren't standard JSON data types.
"""
from json import JSONEncoder
import pickle

def _default(self, obj):
    return {'_python_object': pickle.dumps(obj)}

_default.default = JSONEncoder.default # save default
JSONEncoder.default = _default # replacement