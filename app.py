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
from jira import JIRA
from bson.binary import Binary
from dotenv import load_dotenv
import os
import importlib.util
import sys
import json

sys.path.append("nlp_model")
spec = importlib.util.spec_from_file_location("rbmodel", "nlp_model/rbmodel.py")
nlp_app = importlib.util.module_from_spec(spec)

app = Flask(__name__)
CORS(app)
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = 'aaaa'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)

load_dotenv()
client = OpenAI(api_key=os.environ.get('OPEN_AI_API_KEY'))
jira_connection = JIRA(
    basic_auth=(os.environ.get('JIRA_EMAIL'), os.environ.get('JIRA_KEY')),
    server=os.environ.get('JIRA_ADDRESS')
)

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

    if user_from_db["admin"] == "True":
        del user_from_db['_id'], user_from_db['password'] # delete what we don't want to show
        return jsonify({'profile': user_from_db}), 200

@app.route("/api/v1/sendFeedback", methods=["POST"])
@jwt_required(locations=["headers"])
def sendFeedbackForm():
    current_user = get_jwt_identity()
    user_from_db = db.users_collection.find_one({'username': current_user})
    feedback = request.get_json()
    feedback["timestamp"] = dt.now()
    feedback["username"] = current_user

    if user_from_db:
        db.feedback_collection.insert_one(feedback)
        return jsonify({'msg': 'Inserted successfully'}), 200

    else:
        return jsonify({'msg': 'Profile not found'}), 404

@app.route("/api/v1/getAllFeedback", methods=["GET"])
@jwt_required(locations=["headers"])
def getAllFeedbackForms():
    current_user = get_jwt_identity()
    user_from_db = db.users_collection.find_one({'username': current_user})

    if user_from_db["admin"] == "True":

        allFeedback = list(db.feedback_collection.find({}))
        listFeedback = []
    
        for feedback in allFeedback:
            tempDict = {}
            tempDict["_id"] = str(feedback["_id"])
            tempDict["username"] = feedback["username"]
            tempDict["timestamp"] = feedback["timestamp"]
            tempDict["text"] = feedback["text"]
            listFeedback.append(tempDict)
            
        return jsonify(listFeedback), 200
    
    else:
	    return jsonify({'msg': 'Profile not found or user is not admin'}), 404


@app.route("/api/v1/logConvo", methods=["POST"])
@jwt_required(locations=["headers"])
def saveConvo():
    # try:
        convo_details = request.get_json()
        jwtData = request.headers.get('Authorization')
        spec.loader.exec_module(nlp_app)

        # model = "gpt-4-vision-preview" # more expensive, use while demoing
        model = "gpt-3.5-turbo" # less expensive, use while testing
        img = ''
        if "queryImage" in convo_details and convo_details["queryImage"]:
            img = convo_details["queryImage"]

        print(convo_details["messages"][-1]['content'][-1]['text'])

        pdf = None
        if "pdf" in convo_details:
            pdf = convo_details.pop("pdf")
            
        nlp_resp = nlp_app.get_response(convo_details["messages"][-1]['content'][-1]['text'], img)
        reply = None

        if isinstance(nlp_resp,str):
            convo_details["response"] = nlp_resp
        else:
            current_chat = convo_details["messages"]
            current_chat.append(nlp_resp)
            print(current_chat)
            completion2 = client.chat.completions.create(
                model=model,
                messages=convo_details["messages"],
                max_tokens=1024
            )

            reply = completion2.choices[0].message.content
            print(reply)
            if "$$TRUE$$" in reply:
                text= nlp_resp["content"][0]["text"]
                parts = text.split('\n')
                pdf=parts[1].replace(" ","_")
                reply = reply.replace("$$TRUE$$", " ")
                convo_details["pdf"]= pdf
        
        if reply:
            convo_details["response"] = reply
        current_user = get_jwt_identity()
        user_from_db = db.users_collection.find_one({'username': current_user})
        convo_details["username"] = current_user
        convo_details["model"] = model
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
    #
    # except Exception as e:
    #     return jsonify({'error': str(e)}), 500

@app.route("/api/v1/getAllConvo", methods=["GET"])
@jwt_required(locations=["headers"])
def getAllConvo():
    current_user = get_jwt_identity()
    user_from_db = db.users_collection.find_one({'username': current_user})
    print("here")

    if user_from_db["admin"] == "True":
        convos = list(db.convo_collection.find({}))
        convoDict = []
        for convo in convos:
            tempDict = {}
            tempDict["_id"] = str(convo["_id"])
            tempDict["username"] = convo["username"]
            tempDict["model"] = convo["model"]
            tempDict["timestamp"] = convo["timestamp"]
            tempDict["query"] = convo["query"]
            #tempDict["queryImage"] = convo["queryImage"]
            tempDict["response"] = convo["response"]
            tempDict["jwtData"] = convo["jwtData"]
            convoDict.append(tempDict)

        print(convoDict)
        return jsonify(convoDict), 200
    else:
        return jsonify({'msg': 'Profile not found'}), 404

@app.route("/api/v1/getAllNames", methods=["GET"])
@jwt_required(locations=["headers"])
def getAllNames():
    current_user = get_jwt_identity()
    user_from_db = db.users_collection.find_one({'username': current_user})

    if user_from_db["admin"] == "True":
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
    
@app.route("/api/v1/sendToJira", methods=["POST"])
@jwt_required(locations=["headers"])
def makeJiraTicket():
    try:
        issue = request.get_json()
        current_user = get_jwt_identity()
        user_from_db = db.users_collection.find_one({'username':current_user})

        if user_from_db:
            allConvos = list(db.users_collection.find({'username': current_user}))
            formatted_message_history = format_message_history(allConvos)

            issue_dict = {
                'project': {'key': 'BELL'},
                'summary': 'BAIT bug',
                'description': f'{issue["description"]}\n\n\n{formatted_message_history}',
                'issuetype': {'name': 'Emailed request'},
                'reporter': {'name': current_user}
            }
            new_issue = jira_connection.create_issue(fields=issue_dict)

            return jsonify({'msg': 'JIRA ticket created'})
        else:
            return jsonify({'msg': 'Profile not found'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def format_message_history(allConvos):
    formatted_messages = []

    time = allConvos[len(allConvos) - 1].get("timestamp")
    if (time):
        formatted_messages.append(f'====== Conversation on {time} ======\n\n')

        messages = allConvos[len(allConvos) - 1].get("messages")
        if messages:
            for message in messages[2:]:
                role = message.get("role", "Unknown role")
                content = message.get("content", [{"type": "text", "text": "No content"}])

                for msg in content:
                    text = msg.get("text", "No text")
                    formatted_message = f'{role}: "{text}"\n\n'
                    if len(''.join(formatted_messages)) + len(formatted_message) > 30000:
                        break
                    formatted_messages.append(formatted_message)

    return ''.join(formatted_messages)[:30000]

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
