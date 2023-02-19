# Pip modules
from flask import Flask, request
from bson import json_util
import json
from dotenv import load_dotenv
import os

# Local modules
import connector

load_dotenv()

# Useful links
# https://stackoverflow.com/questions/10434599/get-the-data-received-in-a-flask-request

MONGODB_HOST = os.getenv("host")
MONGODB_PORT = int(os.getenv("port"))
DB_NAME = os.getenv("db")
COLLECTION_NAME = os.getenv("collection")

new_connection = connector.Connector(MONGODB_HOST, MONGODB_PORT)

app = Flask(__name__)

@app.route("/")
def home_page():
    return "<p>Welcome to our homepage!</p>"

@app.route("/login/user/", methods=["GET"])
def get_all_users():
    collection = new_connection.get_collection(DB_NAME, COLLECTION_NAME)
    users = collection.find()
    users_json = []
    
    for user in users:
        users_json.append(user)

    users_json = json.dumps(users_json, default=json_util.default)

    return users_json

@app.route("/login/user/", methods=["POST"])
def create_new_user():
    email = request.form.get("email", type=str)
    # username should be encrypted 
    user = request.form.get("user", type=str)
    # pwd should be encrypted
    pwd = request.form.get("pass", type=str)
    job = request.form.get("job", type=str)

    collection = new_connection.get_collection(DB_NAME, COLLECTION_NAME)

    new_user = { "email": email, "user": user, "pass": pwd, "job": job }

    collection.insert_one(new_user)

    return f"Searching for: {email}, {user}, {pwd}, {job}"

# PATCH isn't included here because we may want to have that functionality to update all users
@app.route("/login/user/", methods=["PUT", "DELETE"])
def invalid_users_endpoint():
    return "Resource not found.", 404

@app.route("/login/user/<string:username>", methods=["GET"])
def get_user_data(username):
    collection = new_connection.get_collection(DB_NAME, COLLECTION_NAME)
    user = collection.find({"user": username})
    user = json_util.dumps(user)

    return user
        
@app.route("/login/user/<string:username>", methods=["DELETE"])
def delete_user(username):
    collection = new_connection.get_collection(DB_NAME, COLLECTION_NAME)
    user = collection.delete_one({"user": username})

    return user

# This will also be done with search query paramters example: ?email=123@gmail.com&user=steven1&pass=123movies&job=student
@app.route("/login/user/<string:username>/", methods=["PUT"])
def update_user(username):
    collection = new_connection.get_collection(DB_NAME, COLLECTION_NAME)
    email = request.form.get("email", type=str)
    # username should be encrypted 
    user = request.form.get("user", type=str)
    # pwd should be encrypted
    pwd = request.form.get("pass", type=str)
    job = request.form.get("job", type=str)

    # If they did not update all of their information, keep the un-updated information the same
    user = collection.update_one({"user": username}, {"$set": {"email": {email}, "user": {user}, "pass": {pwd}, "job": {job}}})

    return user

@app.route("/login/user/<string:username>/", methods=["POST", "PATCH"])
def invalid_user_endpoint():
    return "Resource not found.", 404
    