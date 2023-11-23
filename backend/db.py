from flask import Flask
from flask_pymongo import pymongo
from app import app
import hashlib

CONNECTION_STRING = "mongodb+srv://bcowleyadam:awvLMgRsZYwtLoxA@testproject1.qcpy2vf.mongodb.net/?retryWrites=true&w=majority"
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('flask_mongodb_atlas')
users_collection = db["flask-mongodb-atlas"]
#user_collection = pymongo.collection.Collection(db, 'user_collection')
