# Pip modules
from flask import Flask, request
from bson import json_util
import json
from dotenv import load_dotenv
import os

# Local modules
import connector

load_dotenv()

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

# Example search with query parameters: ?user=steven1&pass=123movies&job=student
@app.route("/login/user/", methods=["POST"])
def create_new_user():
    # username should be encrypted before being sent as a query parameter and should be decrypted here
    user = request.args.get("user", type=str)
    # pwd should be encrypted before being sent as a query parameter and should be decrypted here
    pwd = request.args.get("pass", type=str)
    job = request.args.get("job", type=str)

    collection = new_connection.get_collection(DB_NAME, COLLECTION_NAME)

    new_user = { "user": user, "pass": pwd, "job": job }

    collection.insert_one(new_user)

    return f"Searching for: {user}, {pwd}, {job}"

@app.route("/login/user/<string:username>", methods=["GET"])
def get_user_data(username):
    collection = new_connection.get_collection(DB_NAME, COLLECTION_NAME)
    user = collection.find({"user": username})
    user = json_util.dumps(user)

    return user
        
    