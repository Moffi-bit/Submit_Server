# Pip modules
import random
from flask import Flask, abort, redirect, request
from bson import json_util
import json
from dotenv import load_dotenv
import os
import gridfs
from werkzeug.utils import secure_filename
from datetime import datetime

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

@app.route("/login/user/", methods=["GET", "POST"])
def get_all_users():
    if request.method == "GET":
        collection = new_connection.get_collection(DB_NAME, "users")
        users = collection.find()
        users_json = []
        
        for user in users:
            users_json.append(user)

        users_json = json.dumps(users_json, default=json_util.default)

        return users_json

    if request.method == "POST":
        first = request.form.get("first", type=str)
        last = request.form.get("last", type=str)
        email = request.form.get("email", type=str)
        # username should be encrypted 
        user = request.form.get("user", type=str)
        # pwd should be encrypted
        pwd = request.form.get("pass", type=str)
        id = str(int(random.random() * random.randint(100000, 5000000) * datetime.now().microsecond))
        collection = new_connection.get_collection(DB_NAME, "users")

        new_user = { "id": id, "first": first, "last": last, "email": email, "user": user, "pass": pwd, "classes": "" }

        collection.insert_one(new_user)

        return f"Searching for: {id}, {first}, {last}, {email}, {user}, {pwd}"
    
    return abort(404)

@app.route("/login/user/<string:id>", methods=["GET", "DELETE", "PUT"])
def get_user_data(id):
    collection = new_connection.get_collection(DB_NAME, "users")

    if request.method == "GET":
        user = collection.find({"id": id})
        user = json_util.dumps(user)

        return user
    
    if request.method == "DELETE":
        user = collection.delete_one({"id": id})

        return user
    
    if request.method == "PUT":
        first = request.form.get("first", type=str)
        last = request.form.get("last", type=str)
        email = request.form.get("email", type=str)
        # username should be encrypted (this would be the new username if they changed it)
        user = request.form.get("user", type=str)
        # pwd should be encrypted
        pwd = request.form.get("pass", type=str)

        # If they did not update all of their information, keep the un-updated information the same
        user = collection.update_one({"id": id}, {"$set": {"first": first, "last": last, "email": email, "user": user, "pass": pwd}})

        return user
    
    return abort(404)

@app.route("/login/user/<string:id>/class/<string:class_id>/", methods=["POST"])
def add_user_class(id, class_id):
    if request.method == "POST":
        collection = new_connection.get_collection(DB_NAME, "users")

        user = collection.update_one({"user": id})

        return abort(200) if user else abort(400)
    
    return abort(404)

@app.route("/login/user/<string:id>/class/<string:class_id>/project/", methods=["POST"])
def upload_user_project(id, class_id, project):
    if request.method == "POST":
        collection = new_connection.get_collection(DB_NAME, "projects")
        project = request.form.get("project_name")

        if 'file' not in request.files:
            # If the user didn't upload a file return them back to the page they were at.
            return redirect(request.url)
        
        file = request.files.get("project")

        if file and file != "" and file_utilities.allowed_file(file.filename, project):
            file.filename = f"{id}-{class_id}-{project}"
            fs = gridfs.GridFS(new_connection, collection=collection)
            file_uploaded = fs.put(file)

            return abort(200) if file_uploaded else abort(400)
        
    return abort(404)  

@app.route("/login/user/<string:id>/class/<string:class_id>/project/<string:project>/", methods=["GET"])
def get_user_project(id, class_id, project):
    if request.method == "GET":
        collection = new_connection.get_collection(DB_NAME, "projects")
        fs = gridfs.GridFS(new_connection, collection=collection)

        if fs.exists(filename=f"{id}-{class_id}-{project}"):
            file_reference = fs.get(f"{id}-{class_id}-{project}")
            

            return str(file_reference.read())
    
    return abort(404)