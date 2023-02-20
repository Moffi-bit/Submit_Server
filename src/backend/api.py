# Pip modules
from flask import Flask, abort, redirect, request
from bson import json_util
import json
from dotenv import load_dotenv
import os
import gridfs
from werkzeug.utils import secure_filename

# Local modules
import connector
import file_utilities

load_dotenv()

# Useful links
# https://stackoverflow.com/questions/10434599/get-the-data-received-in-a-flask-request

MONGODB_HOST = os.getenv("HOST")
MONGODB_PORT = int(os.getenv("PORT"))
DB_NAME = os.getenv("DB")

new_connection = connector.Connector(MONGODB_HOST, MONGODB_PORT)

app = Flask(__name__)

@app.route("/")
def invalid_homepage_request():
    return abort(404)

@app.route("/login/")
def invalid_login_request():
    return abort(404)

@app.route("/login/user/", methods=["GET"])
def get_all_users():
    collection = new_connection.get_collection(DB_NAME, "users")
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

    collection = new_connection.get_collection(DB_NAME, "users")

    new_user = { "email": email, "user": user, "pass": pwd, "classes": "" }

    collection.insert_one(new_user)

    return f"Searching for: {email}, {user}, {pwd}"

# PATCH isn't included here because we may want to have that functionality to update all users
@app.route("/login/user/", methods=["PUT", "DELETE"])
def invalid_users_endpoint():
    return abort(404)

@app.route("/login/user/<string:username>", methods=["GET"])
def get_user_data(username):
    collection = new_connection.get_collection(DB_NAME, "users")
    user = collection.find({"user": username})
    user = json_util.dumps(user)

    return user
        
@app.route("/login/user/<string:username>", methods=["DELETE"])
def delete_user(username):
    collection = new_connection.get_collection(DB_NAME, "users")
    user = collection.delete_one({"user": username})

    return user

@app.route("/login/user/<string:username>/", methods=["PUT"])
def update_user(username):
    collection = new_connection.get_collection(DB_NAME, "users")
    email = request.form.get("email", type=str)
    # username should be encrypted (this would be the new username if they changed it)
    user = request.form.get("user", type=str)
    # pwd should be encrypted
    pwd = request.form.get("pass", type=str)

    # If they did not update all of their information, keep the un-updated information the same
    user = collection.update_one({"user": username}, {"$set": {"email": {email}, "user": {user}, "pass": {pwd}}})

    return user

@app.route("/login/user/<string:username>/", methods=["POST", "PATCH"])
def invalid_user_endpoint(username):
    return abort(404)

@app.route("/login/user/<string:username>/class/<string:class_name>/", methods=["POST"])
def add_user_class(username, class_name):
    collection = new_connection.get_collection(DB_NAME, "users")

    user = collection.update_one({"user": username}, {"$set": {"classes": {"$concat": [ "$classes", f".{class_name}"]}}})

    return user

@app.route("/login/user/<string:username>/class/<string:class_name>/", methods=["GET", "PUT", "PATCH", "DELETE"])
def invalid_class_endpoint(username, class_name):
    return abort(404)

@app.route("/login/user/<string:username>/class/<string:class_name>/project/<string:project>/", methods=["POST"])
def upload_user_project(username, class_name, project):
    collection = new_connection.get_collection(DB_NAME, "projects")

    if 'file' not in request.files:
        # If the user didn't upload a file return them back to the page they were at.
        return redirect(request.url)
    
    file = request.files.get("project")

    if file and file != "" and file_utilities.allowed_file(file.filename, project):
        file.filename = f"{username}-{class_name}-{project}"
        fs = gridfs.GridFS(new_connection, collection=collection)
        file_uploaded = fs.put(file)

        return abort(200) if file_uploaded else abort(400)
    
@app.route("/login/user/<string:username>/class/<string:class_name>/project/<string:project>/", methods=["GET"])
def get_user_project(username, class_name, project):
    collection = new_connection.get_collection(DB_NAME, "projects")
    fs = gridfs.GridFS(new_connection, collection=collection)

    if fs.exists(filename=f"{username}-{class_name}-{project}"):
        file_reference = fs.get(f"{username}-{class_name}-{project}")

        return file_reference.read()
    
    return abort(400)

@app.route("/login/user/<string:username>/class/<string:class_name>/project/<string:project>/", methods=["PUT", "PATCH", "DELETE"])
def invalid_project_endpoint(username, class_name, project):
    return abort(404)