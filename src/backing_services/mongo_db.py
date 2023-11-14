import pymongo

from utils.project_config import project_config
from utils.constants import DatabaseConfig

class MongoDatabase:
    def __init__(self):
        self._db_url = project_config.DB_URL
        self._client = pymongo.MongoClient(project_config.DB_URL)

        self._db = self._client[DatabaseConfig.DB_NAME]
        self._collection = self._db[DatabaseConfig.COLLECTION_NAME]

    def insert_one(self, data):
        return self._collection.insert_one(data)
    
    def delete_one(self, query):
        return self._collection.delete_one(query)
    
    def find_all(self):
        return self._collection.find()
    
db_connect = MongoDatabase()