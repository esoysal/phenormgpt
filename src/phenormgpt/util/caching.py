import os
import json
import pickle
from config.config import CACHE_DIR

os.makedirs(CACHE_DIR, exist_ok=True)

def save_to_cache(filename: str, object):
    filepath = os.path.join(CACHE_DIR, filename)
    with open(filepath, 'wb') as file:
        pickle.dump(object, file)

def load_from_cache(filename: str):
    filepath = os.path.join(CACHE_DIR, filename)
    with open(filepath, 'rb') as file:
        object = pickle.load(file)
    return object

def save_json_to_cache(filename: str, object):
    filepath = os.path.join(CACHE_DIR, filename)
    with open(filepath, 'w') as file:
        json.dump(object , file)

def load_json_from_cache(filename: str):
    filepath = os.path.join(CACHE_DIR, filename)
    with open(filepath, 'r') as file:
        object = json.load(file)
    return object