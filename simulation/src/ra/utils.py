import pickle
import base64

def serialize(data):
    return pickle.dumps(data)

def encode(data):
    return base64.b64encode(data).decode()

def decode(data):
    return base64.b64decode(data)