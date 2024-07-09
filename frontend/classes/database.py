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

    def update(self, collection, filter, data):
        newvalues = {"$set": data.__dict__}
        return self.db[collection].update_one(filter, newvalues)

    def update_many(self, collection, filter, data):
        newvalues = {"$set": data.__dict__}
        return self.db[collection].update_many(filter, newvalues)

    def delete(self, collection, filter):
        return self.db[collection].delete_one(filter)

    def find(self, collection, filter):
        return list(self.db[collection].find(filter))
