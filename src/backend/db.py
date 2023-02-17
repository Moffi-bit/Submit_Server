import json
from pymongo import MongoClient
from bson import json_util
from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_HOST = os.getenv("host")
MONGODB_PORT = os.getenv("port")
DB_NAME = os.getenv("db")
COLLECTION_NAME = os.getenv("collection")

def submit_multiple_users():
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collection = connection[DB_NAME][COLLECTION_NAME]

    demo_users = [
        { "name": "Amy", "address": "Apple st 652"},
        { "name": "Hannah", "address": "Mountain 21"},
        { "name": "Michael", "address": "Valley 345"},
        { "name": "Sandy", "address": "Ocean blvd 2"},
        { "name": "Betty", "address": "Green Grass 1"},
        { "name": "Richard", "address": "Sky st 331"},
        { "name": "Susan", "address": "One way 98"},
        { "name": "Vicky", "address": "Yellow Garden 2"},
        { "name": "Ben", "address": "Park Lane 38"},
        { "name": "William", "address": "Central st 954"},
        { "name": "Chuck", "address": "Main Road 989"},
        { "name": "Viola", "address": "Sideway 1633"}
    ]

    collection.insert_many(demo_users)
    connection.close()

if __name__ == "__main__":
    submit_multiple_users()