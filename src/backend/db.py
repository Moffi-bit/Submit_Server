from dotenv import load_dotenv
import os

from backend.connector import Connector

load_dotenv()

MONGODB_HOST = os.getenv("HOST")
MONGODB_PORT = int(os.getenv("PORT"))
DB_NAME = os.getenv("DB")

new_connection = Connector(MONGODB_HOST, MONGODB_PORT)

def submit_multiple_users():
    collection = new_connection.get_collection(DB_NAME, "users")

    demo_users = [
        {"email": "demo123@gmail.com", "user": "demo123", "pass": "demo123pass", "classes": ""},
        {"email": "steven79@gmail.com", "user": "steve12", "pass": "stevepass", "classes": ""},
        {"email": "moneymike@gmail.com", "user": "mmike", "pass": "demo$1mike", "classes": ""},
        {"email": "john79@gmail.com", "user": "johncena", "pass": "johnpass", "classes": ""},
    ]

    collection.insert_many(demo_users)
    new_connection.close_connection()

if __name__ == "__main__":
    submit_multiple_users()