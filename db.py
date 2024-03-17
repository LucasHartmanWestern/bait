from flask import Flask
from flask_pymongo import pymongo
import hashlib

CONNECTION_STRING = "mongodb+srv://brennanca:Bunnysex69@cluster0.mv0wogx.mongodb.net/?retryWrites=true&w=majority"
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('baitdb')
users_collection = db["userInformation"]
convo_collection = db["conversationData"]
feedback_collection = db["forumData"]
#user_collection = pymongo.collection.Collection(db, 'user_collection')