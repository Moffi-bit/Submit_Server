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

def get_all_of_a_collection(collection):
    items = collection.find()
    items_json = []
        
    for item in items:
        items_json.append(item)

    items_json = json.dumps(items_json, default=json_util.default)

    return items_json

@app.route("/user/", methods=["GET", "POST"])
def user_crud():
    collection = new_connection.get_collection(DB_NAME, "users")

    if request.method == "GET":
        return get_all_of_a_collection(collection)

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

    if request.method == "GET":
        return get_all_of_a_collection(collection)
    
    if request.method == "POST":
        name = request.form.get("name", type=str)
        period = request.form.get("period", type=str)

        class_id = other_utilities.generate_id()

        new_class = { "id": class_id, "name": name, "period": period, "assignments": [], "sections": [] }

        collection.insert_one(new_class)

        return class_id

    return abort(404)

@app.route("/assignment/", methods=["GET", "POST"])
def assignment_crud():
    collection = new_connection.get_collection(DB_NAME, "assignments")

    if request.method == "GET":
        return get_all_of_a_collection(collection)

    if request.method == "POST":
        class_id = request.form.get("class", type=str)
        points = request.form.get("points", type=str)

        id = other_utilities.generate_id()
        
        # can add more data to assignments with time
        new_assignment = {"id": id, "class": class_id, "points": points}

        collection.insert_one(new_assignment)

        return id
    
    return abort(404)

@app.route("/section/", methods=["GET", "POST"])
def section_crud():
    collection = new_connection.get_collection(DB_NAME, "sections")
    class_collection = new_connection.get_collection(DB_NAME, "classes")

    if request.method == "GET":
        return get_all_of_a_collection(collection)

    if request.method == "POST":
        class_id = request.form.get("class_id", type=str)
        section_id = other_utilities.generate_id()

        if class_collection.find_one({"id": class_id}) != None:
            class_collection.update_one({"id": class_id}, {"$addToSet": {"sections": {"$each": {[section_id]}}}})

        new_section = {"id": section_id, "class_id": class_id, "instructors": [], "tas": [], "students": [] }

        collection.insert_one(new_section)

        return section_id
    
    return abort(404)

@app.route("/file/", methods=["GET", "POST"])
def file_crud():
    collection = new_connection.get_collection(DB_NAME, "files")

    if request.method == "GET":
        return get_all_of_a_collection(collection)
    
    if request.method == "POST":
        name = request.form.get("project_name")

        if 'file' not in request.files:
            # If the user didn't upload a file return them back to the page they were at.
            return redirect(request.url)
        
        file = request.files.get("file")

        if file and file != "" and file_utilities.allowed_file(file.filename, name):
            
            return abort(200)
        
    return abort(404)  

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

@app.route("/user/<string:id>/class/", methods=["GET"])
def specific_user_crud_all_classes():
    users_collection = new_connection.get_collection(DB_NAME, "users")

    if request.method == "GET":
        if users_collection.find_one({"id": id}) != None:
            return

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