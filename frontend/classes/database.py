from pymongo import MongoClient
from bson import json_util
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

    def update_one(self, collection, filter, data):
        if isinstance(data, dict):
            values = {"$set": data}
        else:
            values = {"$set": data.__dict__}

        return self.db[collection].update_one(filter, values)

    def update_many(self, collection, filter, data):
        if isinstance(data, dict):
            values = {"$set": data}
        else:
            values = {"$set": data.__dict__}

        return self.db[collection].update_many(filter, values)

    def delete(self, collection, filter):
        return self.db[collection].delete_one(filter)

    def find_one(self, collection, filter, sort):
        if sort:
            result = self.db[collection].find_one(filter, sort=[sort])
        else:
            result = self.db[collection].find_one(filter)

        if result is None:
            return False
        else:
            return result

    def find(self, collection, filter):
        return list(self.db[collection].find(filter))
