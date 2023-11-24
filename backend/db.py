from flask import Flask
from flask_pymongo import pymongo
from app import app
import hashlib

CONNECTION_STRING = "mongodb+srv://2andrewmalcolm:<astupidpassword>@cluster0.mv0wogx.mongodb.net/?retryWrites=true&w=majority"
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('baitdb')
users_collection = db["userInformation"]
#user_collection = pymongo.collection.Collection(db, 'user_collection')
