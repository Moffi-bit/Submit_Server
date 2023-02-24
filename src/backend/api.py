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
    collection = new_connection.get_collection(DB_NAME, "users")

    if request.method == "GET":
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

        new_user = { "id": id, "first": first, "last": last, "email": email, "user": user, "pass": pwd, "classes": [] }
        collection.insert_one(new_user)

        return id
    
    return abort(404)

@app.route("/login/class/", methods=["GET", "POST"])
def add_new_class():
    collection = new_connection.get_collection(DB_NAME, "classes")

    if request.method == "GET":
        classes = collection.find()
        classes_json = []
        
        for user in classes:
            classes_json.append(user)

        classes_json = json.dumps(classes_json, default=json_util.default)

        return classes_json
    
    if request.method == "POST":
        name = request.form.get("name", type=str)
        id = str(int(random.random() * random.randint(100000, 5000000) * datetime.now().microsecond))

        new_class = { "id": id, "name": name, "instructors": [], "tas": [], "students": [] }

        collection.insert_one(new_class)

        return id

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

@app.route("/login/user/<string:id>/class/<string:class_id>/", methods=["PUT"])
def add_user_class(id, class_id):
    users_collection = new_connection.get_collection(DB_NAME, "users")
    class_collection = new_connection.get_collection(DB_NAME, "classes")

    if request.method == "PUT":
        role = request.form.get("role", type=str)
        users_collection.update_one({"id": id}, {"$addToSet": { "classes": {"$each": {[f"{class_id}"]}}}})
        class_collection.update_one({"id": id}, {"$addToSet": {f"{role}": {"$each": {[f"{id}"]}}}})

        return abort(200)
    
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