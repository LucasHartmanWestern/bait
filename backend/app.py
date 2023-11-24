import hashlib
import datetime
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
from PIL import Image
import io
import db
from openai import OpenAI
from datetime import datetime as dt
from jira import JIRA
from bson.binary import Binary

app = Flask(__name__)
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = 'aaaa'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
jira_connection = JIRA(
    basic_auth=('workspace_email', 'api_token'),
    server="https://lhartma8.atlassian.net"
)


client = OpenAI()


@app.route("/api/v1/login", methods=["POST"])
def login():
    login_details = request.get_json()
    user_from_db = db.users_collection.find_one({'username': login_details['username']})

    if user_from_db:
        encrypted_password = hashlib.sha256(login_details['password'].encode("utf-8")).hexdigest()
        if encrypted_password == user_from_db['password']:
            access_token = create_access_token(identity=user_from_db['username'])
            return jsonify(access_token=access_token), 200


    return jsonify({'msg': 'The username or password is incorrect'}), 401
    
@app.route("/api/v1/users", methods=["POST"])
def register():
    new_user = request.get_json()
    new_user["password"] = hashlib.sha256(new_user["password"].encode("utf-8")).hexdigest() # encrpt password
    doc = db.users_collection.find_one({"username": new_user["username"]}) # check if user exist
    
    if not doc:
        db.users_collection.insert_one(new_user)
        access_token = create_access_token(identity=new_user["username"])
        return jsonify(access_token=access_token), 201       
    else:
        return jsonify({'msg': 'Username already exists'}), 409

@app.route("/api/v1/user", methods=["GET"])
@jwt_required(locations=["headers"])
def profile():
    current_user = get_jwt_identity()
    user_from_db = db.users_collection.find_one({'username': current_user})

    if user_from_db["admin"] == "True":
        del user_from_db['_id'], user_from_db['password'] # delete what we don't want to show
        return jsonify({'profile': user_from_db}), 200

    else:
        return jsonify({'msg': 'Profile not found or not admin'}), 404
# this is only if we want to send just an image, but not currently in use
# @app.route("/api/v1/sendImage", methods=["POST"])
# @jwt_required(locations=["headers"])
# def sendImage():
#     current_user = get_jwt_identity()
#     user_from_db = db.users_collection.find_one({'username': current_user})

#     if user_from_db:
#         im = Image.open("./image.jpg")
#         image_bytes = io.BytesIO()
#         im.save(image_bytes, format='JPEG')

#         image = {
#             'data': image_bytes.getvalue()
#         }

#         db.users_collection.insert_one(image)
#         return jsonify({'msg': 'Image saved successfully'}), 200
#     else:
#          return jsonify({'msg': 'Profile not found'}), 404

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
    convo_details = request.get_json()
    jwtData = request.headers.get('Authorization')

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": convo_details["query"]}
        ]
    )

    convo_details["response"] = completion.choices[0].message.content
    current_user = get_jwt_identity()
    user_from_db = db.users_collection.find_one({'username': current_user})
    convo_details["username"] = current_user
    convo_details["model"] = "GPT"
    convo_details["timestamp"] = dt.now()
    convo_details["jwtData"] = jwtData

    if user_from_db:
        if convo_details["queryImage"] is None:
            db.convo_collection.insert_one(convo_details)
            return jsonify({'msg': 'Saved log'}), 200
        else:
            file_used = str(convo_details["queryImage"])
            with open(file_used, "rb") as f:
                encoded = Binary(f.read())

            convo_details["queryImage"] = encoded
            db.convo_collection.insert_one(convo_details)
            return jsonify({'msg': 'Saved log'}), 200
    else:
        return jsonify({'msg': 'Profile not found'}), 404

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
    
@app.route("/api/v1/sendToJira", methods=["GET"])
@jwt_required(locations=["headers"])
def makeJiraTicket():
    issue = request.get_json()
    current_user = get_jwt_identity()
    user_from_db = db.users_collection.find_one({'username':current_user})

    if user_from_db:
        allConvos = list(db.users_collection.find({'username': current_user}))
        convoDict = []
        for convo in allConvos:
            tempDict = {}
            tempDict["model"] = convo["model"]
            tempDict["timestamp"] = convo["timestamp"]
            tempDict["query"] = convo["query"]
            tempDict["response"] = convo["response"]
            convoDict.append(tempDict)
    
        issue_dict = {
        'project': {'key': 'CAP'},
        'summary': 'BAIT bug: ' + current_user,
        'description': 'Detailed ticket description.',
        'issuetype': {'name': 'Bug'},
        }  
        new_issue = jira_connection.create_issue(fields=issue_dict)

        return jsonify({'msg': 'JIRA ticket created'})
    
    else:
        return jsonify({'msg': 'Profile not found'})

if __name__ == '__main__':
    app.run(port=8000)
