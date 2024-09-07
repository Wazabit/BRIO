from pymongo import MongoClient
from os import environ as env
from dotenv import find_dotenv, load_dotenv


class Database(object):
    ENV_FILE = find_dotenv()
    if ENV_FILE:
        load_dotenv(ENV_FILE)

    def __init__(self):
        self.client = MongoClient(env.get("ATLAS_URI"))
        self.db = self.client[env.get("DB_NAME")]

    def insert(self, collection, data):
        return self.db[collection].insert_one(data.__dict__)

    def update_one(self, collection, condition, data):
        if isinstance(data, dict):
            values = {"$set": data}
        else:
            values = {"$set": data.__dict__}

        return self.db[collection].update_one(condition, values)

    def update_many(self, collection, condition, data):
        if isinstance(data, dict):
            values = {"$set": data}
        else:
            values = {"$set": data.__dict__}

        return self.db[collection].update_many(condition, values)

    def delete(self, collection, condition):
        return self.db[collection].delete_one(condition)

    def find_one(self, collection, condition, sort):
        if sort:
            result = self.db[collection].find_one(condition, sort=[sort])
        else:
            result = self.db[collection].find_one(condition)

        if result is None:
            return False
        else:
            return result

    def find(self, collection, filter, projection=None, sort=None):
        if projection and sort:
            return list(self.db[collection].find(filter, projection=[projection], sort=[sort]))
        elif sort:
            return list(self.db[collection].find(filter, sort=[sort]))
        else:
            return list(self.db[collection].find(filter))

    def aggregate(self, collection, pipeline):
        return list(self.db[collection].aggregate(pipeline))
