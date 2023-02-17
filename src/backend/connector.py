from pymongo import MongoClient

class Connector():
    def __init__(self, host, port):
        self.connection = MongoClient(host, port)

    def get_collection(self, db_name, collection_name):
        return self.connection[db_name][collection_name]
    
    def close_connection(self):
        self.connection.close()