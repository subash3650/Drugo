# services/db.py
from pymongo import MongoClient, errors
import os
from dotenv import load_dotenv
load_dotenv()

_client = None

def get_db_client():
    """
    Return a singleton MongoClient instance.
    """
    global _client
    if _client is None:
        uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
        _client = MongoClient(uri)
    return _client

def get_db(default_db_name: str = "drug_detect"):
    """
    Return a database handle.
    Try to use the default database from the connection string;
    if not present, fall back to `default_db_name`.
    This handles cases where the URI is mongodb://host:27017 (no DB).
    """
    client = get_db_client()
    try:
        # If the URI contained a database, this returns it.
        db = client.get_default_database()
        if db is None:
            # get_default_database() may return None in some cases,
            # so we explicitly handle that.
            db = client[default_db_name]
    except errors.ConfigurationError:
        # Raised when no default DB is defined in the URI; fall back.
        db = client[default_db_name]
    return db
