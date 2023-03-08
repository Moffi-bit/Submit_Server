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
import other_utilities

load_dotenv()

# Useful links
# https://stackoverflow.com/questions/10434599/get-the-data-received-in-a-flask-request

MONGODB_HOST = os.getenv("HOST")
MONGODB_PORT = int(os.getenv("PORT"))
DB_NAME = os.getenv("DB")

new_connection = connector.Connector(MONGODB_HOST, MONGODB_PORT)

app = Flask(__name__)

@app.route("/user/", methods=["GET", "POST"])
def user_crud():
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
        id = other_utilities.generate_id()

        new_user = { "id": id, "first": first, "last": last, "email": email, "user": user, "pass": pwd, "classes": [] }
        collection.insert_one(new_user)

        return id
    
    return abort(404)

@app.route("/class/", methods=["GET", "POST"])
def class_crud():
    collection = new_connection.get_collection(DB_NAME, "classes")
    sections_collection = new_connection.get_collection(DB_NAME, "sections")

    if request.method == "GET":
        classes = collection.find()
        classes_json = []
        
        for curr_class in classes:
            classes_json.append(curr_class)

        classes_json = json.dumps(classes_json, default=json_util.default)

        return classes_json
    
    if request.method == "POST":
        name = request.form.get("name", type=str)
        period = request.form.get("period", type=str)

        class_id = other_utilities.generate_id()
        section_id = other_utilities.generate_id()

        new_class = { "id": class_id, "name": name, "period": period, "assignments": [], "sections": [] }
        new_section = {"id": section_id, "class_id": class_id, "instructors": [], "tas": [], "students": [] }

        collection.insert_one(new_class)
        sections_collection.insert_one(new_section)

        return class_id, section_id

    return abort(404)

@app.route("/assignment/")
def assignment_crud():
    collection = new_connection.get_collection(DB_NAME, "assignments")

    if request.method == "POST":
        class_id = request.form.get("class", type=str)
        points = request.form.get("points", type=str)

        id = other_utilities.generate_id()
        
        # can add more data to assignments with time
        new_assignment = {"id": id, "class": class_id, "points": points}


@app.route("/user/<string:id>", methods=["GET", "DELETE", "PUT"])
def specific_user_crud(id):
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

@app.route("/user/<string:id>/class/<string:class_id>/", methods=["PUT"])
def specific_user_and_class_crud(id, class_id):
    users_collection = new_connection.get_collection(DB_NAME, "users")
    section_collection = new_connection.get_collection(DB_NAME, "sections")

    if request.method == "PUT":
        role = request.form.get("role", type=str)

        users_collection.update_one({"id": id}, {"$addToSet": { "classes": {"$each": {[f"{class_id}"]}}}})
        section_collection.update_one({"class_id": class_id}, {"$addToSet": {f"{role}": {"$each": {[f"{id}"]}}}})

        return abort(200)
    
    return abort(404)

@app.route("/user/<string:id>/class/<string:class_id>/project/", methods=["POST"])
def project_crud(id, class_id):
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

@app.route("/user/<string:id>/class/<string:class_id>/project/<string:project>/", methods=["GET"])
def specific_project_crud(id, class_id, project):
    if request.method == "GET":
        collection = new_connection.get_collection(DB_NAME, "projects")
        fs = gridfs.GridFS(new_connection, collection=collection)

        if fs.exists(filename=f"{id}-{class_id}-{project}"):
            file_reference = fs.get(f"{id}-{class_id}-{project}")
            

            return str(file_reference.read())
    
    return abort(404)