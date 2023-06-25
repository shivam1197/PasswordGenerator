
import random
import string
from random_word import RandomWords
import zxcvbn
from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS
from flask import make_response
import json
from bson.objectid import ObjectId
import bcrypt

app = Flask(__name__)
CORS(app, origins=["http://localhost:4200"])

client = MongoClient('mongodb://localhost:27017/')
db = client['password_db']
password_collection = db["passwords"]


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    client = MongoClient("mongodb://localhost:27017/")
    db = client["password_db"]
    collection = db["users"]

    user = {
        "email": email,
        "password": password
    }
    collection.insert_one(user)
    return jsonify({"msg": "User created successfully"})


@app.route('/check-password', methods=['POST'])
def check_password():
    data = request.get_json()
    email = data.get("email")
    website = data.get("website")
    password_data = password_collection.find_one(
        {"email": email, "website": website})
    if password_data:
        return jsonify({"password": password_data['password']})
    else:
        return jsonify({"password": None})


@app.route('/generate-password', methods=['POST'])
def generate_password() -> str:
    length = 20
    word = RandomWords().get_random_word()
    characters = string.ascii_letters + string.digits + string.punctuation
    password = word + ''.join(random.choice(characters)
                              for _ in range(length-len(word)))
    password = ''.join(random.sample(password, len(password)))
    password = ''.join(random.SystemRandom().choice(password)
                       for _ in range(length))
    strength = zxcvbn.zxcvbn(password)['score']
    if strength < 4:
        password = generate_password()
    return jsonify(password)


@app.route('/save-password', methods=['POST'])
def save_password():
    data = request.get_json()
    print("data", data)
    email = request.json['email']
    print("email", email)
    website = request.json["website"]
    password = request.json["password"]
    # password = request.json['password']
    db.passwords.insert_one(
        {'email': email, 'website': website, 'password': password})
    return jsonify({'message': 'Password saved successfully'})


@app.route('/get-password', methods=['GET'])
def get_password():
    email = request.args.get("email")
    website = request.args.get("website")
    password_data = password_collection.find_one(
        {"email": email, "website": website})
    print("password data", password_data)
    if password_data:
        password_data["_id"] = str(password_data["_id"])
        return make_response((json.dumps(password_data, indent=4)), 200)
    else:
        return make_response(("password not found"), 404)


if __name__ == '__main__':
    app.run(debug=True)
