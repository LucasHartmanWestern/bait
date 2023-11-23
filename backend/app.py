import hashlib
import datetime
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
from PIL import Image
import io
import db

app = Flask(__name__)
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = 'aaaa'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)



@app.route('/')
def flask_mongodb_atlas():
    return "flask mongodb atlas!"


#test to insert data to the data base
@app.route("/test")
def test():
    db.db.collection.insert_one({"name": "John"})
    return "Connected to the data base!"

@app.route("/api/v1/users", methods=["POST"])
def register():
	new_user = request.get_json() # store the json body request
	new_user["password"] = hashlib.sha256(new_user["password"].encode("utf-8")).hexdigest() # encrpt password
	doc = db.users_collection.find_one({"username": new_user["username"]}) # check if user exist
	if not doc:
		db.users_collection.insert_one(new_user)
		return jsonify({'msg': 'User created successfully'}), 201
	else:
		return jsonify({'msg': 'Username already exists'}), 409
      
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
    

@app.route("/api/v1/user", methods=["GET"])
@jwt_required
def profile():
    current_user = get_jwt_identity()
    user_from_db = db.users_collection.find_one({'username': current_user})

    if user_from_db:
        del user_from_db['_id'], user_from_db['password'] # delete what we don't want to show
        return jsonify({'profile': user_from_db}), 200
    
    else:
        return jsonify({'msg': 'Profile not found'}), 404


# to upload image to database. Request sends jwt of user & 
@app.route("/api/v1/image", methods=["POST"])
@jwt_required
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
         return jsonify({'msg': 'Profile not found'})
    
# if we want to receive an image from the database 

@app.route("/api/v1/images", methods=["POST"])
@jwt_required
def getImage():
    current_user = get_jwt_identity()
    user_from_db = db.users_collection.find_one({'username': current_user})

    if user_from_db:
        image = db.users_collection.find_one
        pil_img = Image.open(io.BytesIO(image['data']))
        return jsonify({'img': pil_img})
    else:
        return jsonify({'msg': 'Profile not found'})
        
      
        
if __name__ == '__main__':
    app.run(port=8000)
