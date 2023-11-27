import hashlib
import datetime

from bson import ObjectId
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from pymongo import MongoClient
from PIL import Image
import io
import db
from openai import OpenAI
from datetime import datetime as dt
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app)
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = 'aaaa'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)

load_dotenv()
client = OpenAI(api_key=os.environ.get('OPEN_AI_API_KEY'))

@app.route("/api/v1/users", methods=["POST"])
def register():
    try:
        new_user = request.get_json() # store the json body request
        new_user["password"] = hashlib.sha256(new_user["password"].encode("utf-8")).hexdigest() # encrpt password
        doc = db.users_collection.find_one({"username": new_user["username"]}) # check if user exist
        if not doc:
            db.users_collection.insert_one(new_user)
            return jsonify({'msg': 'User created successfully'}), 201
        else:
            return jsonify({'msg': 'Username already exists'}), 409

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/v1/login", methods=["POST"])
def login():
    try:
        login_details = request.get_json()
        user_from_db = db.users_collection.find_one({'username': login_details['username']})

        if user_from_db:
            encrypted_password = hashlib.sha256(login_details['password'].encode("utf-8")).hexdigest()
            if encrypted_password == user_from_db['password']:
                access_token = create_access_token(identity=user_from_db['username'])
                return jsonify(access_token=access_token), 200
            else:
                return jsonify({'error': 'The username or password is incorrect'}), 401
        else:
            return jsonify({'error': 'The username or password is incorrect'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/v1/user", methods=["GET"])
@jwt_required(locations=["headers"])
def profile():
    current_user = get_jwt_identity()
    user_from_db = db.users_collection.find_one({'username': current_user})

    if user_from_db:
        del user_from_db['_id'], user_from_db['password'] # delete what we don't want to show
        return jsonify({'profile': user_from_db}), 200

    else:
        return jsonify({'msg': 'Profile not found'}), 404

@app.route("/api/v1/sendImage", methods=["POST"])
@jwt_required(locations=["headers"])
def sendImage():
    current_user = get_jwt_identity()
    user_from_db = db.users_collection.find_one({'username': current_user})

    if user_from_db:
        im = Image.open("./image.jpg")
        image_bytes = io.BytesIO()
        im.save(image_bytes, format='JPEG')

        image = {
            'data': image_bytes.getvalue()
        }

        db.users_collection.insert_one(image)
        return jsonify({'msg': 'Image saved successfully'}), 200
    else:
         return jsonify({'msg': 'Profile not found'}), 404

@app.route("/api/v1/sendFeedback", methods=["POST"])
@jwt_required(locations=["headers"])
def sendFeedbackForm():
    current_user = get_jwt_identity()
    user_from_db = db.users_collection.find_one({'username': current_user})
    feedback = request.get_json()
    feedback["timestamp"] = dt.now()
    feedback["username"] = current_user

    if user_from_db:
        db.users_collection.insert_one(feedback)
        return jsonify({'msg': 'Inserted successfully'}), 200

    else:
        return jsonify({'msg': 'Profile not found'}), 404

@app.route("/api/v1/getAllFeedback", methods=["GET"])
@jwt_required(locations=["headers"])
def getAllFeedbackForms():
    allFeedback = list(db.users_collection.find({}))
    listFeedback = []

    if allFeedback:
        for feedback in allFeedback:
            tempDict = {}
            tempDict["_id"] = str(feedback["_id"])
            tempDict["username"] = allFeedback["username"]
            tempDict["timestamp"] = allFeedback["timestamp"]
            tempDict["text"] = allFeedback["text"]
            listFeedback.append(tempDict)

        return jsonify(listFeedback), 200

    else:
        return jsonify({'msg': 'Profile not found'}), 404

@app.route("/api/v1/logConvo", methods=["POST"])
@jwt_required(locations=["headers"])
def saveConvo():
    try:
        convo_details = request.get_json()
        jwtData = request.headers.get('Authorization')

        completion = client.chat.completions.create(
            model="gpt-4",
            messages=convo_details["messages"]
        )

        convo_details["response"] = completion.choices[0].message.content
        current_user = get_jwt_identity()
        user_from_db = db.users_collection.find_one({'username': current_user})
        convo_details["username"] = current_user
        convo_details["model"] = "GPT-3.5 turbo"
        convo_details["timestamp"] = dt.now()
        convo_details["jwtData"] = jwtData

        if user_from_db:
            db.users_collection.insert_one(convo_details)

            # Convert the document for JSON serialization
            serializable_convo_details = {
                key: str(value) if isinstance(value, (ObjectId, datetime.datetime)) else value
                for key, value in convo_details.items()
            }
            return jsonify(serializable_convo_details), 200
        else:
            return jsonify({'msg': 'Profile not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/v1/getAllConvo", methods=["GET"])
@jwt_required(locations=["headers"])
def getAllConvo():
    current_user = get_jwt_identity()
    user_from_db = db.users_collection.find_one({'username': current_user})

    if user_from_db:
        convos = list(db.users_collection.find({}))
        convoDict = []
        for convo in convos:
            tempDict = {}
            tempDict["_id"] = str(convo["_id"])
            tempDict["username"] = convo["username"]
            tempDict["model"] = convo["model"]
            tempDict["timestamp"] = convo["timestamp"]
            tempDict["query"] = convo["query"]
            tempDict["queryImage"] = convo["queryImage"]
            tempDict["response"] = convo["response"]
            tempDict["jwtData"] = convo["jwtData"]
            convoDict.append(tempDict)

        return jsonify(convoDict), 200
    else:
        return jsonify({'msg': 'Profile not found'}), 404

@app.route("/api/v1/getAllNames", methods=["GET"])
@jwt_required(locations=["headers"])
def getAllNames():
    current_user = get_jwt_identity()
    user_from_db = db.users_collection.find_one({'username': current_user})

    if user_from_db:
        names = list(db.users_collection.find())
        convoDict = []
        for convo in names:
            tempDict = {}
            tempDict["username"] = convo["username"]
            tempDict["timestamp"] = convo["timestamp"]
            convoDict.append(tempDict)

        return jsonify(convoDict), 200
    else:
         return jsonify({'msg': 'Profile not found'}), 404

if __name__ == '__main__':
    app.run(port=8000)
