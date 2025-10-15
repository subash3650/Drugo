from pymongo import MongoClient, errors
import os
from dotenv import load_dotenv
load_dotenv()

_client = None

def get_db_client():
    global _client
    if _client is None:
        uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
        _client = MongoClient(uri)
    return _client

def get_db(default_db_name: str = "drug_detect"):
    client = get_db_client()
    try:
        db = client.get_default_database()
        if db is None:
            db = client[default_db_name]
    except errors.ConfigurationError:
        db = client[default_db_name]
    return db
