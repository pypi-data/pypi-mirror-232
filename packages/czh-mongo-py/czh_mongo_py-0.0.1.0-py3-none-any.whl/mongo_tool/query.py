import pymongo
import os
ip = str(os.environ.get('mongoship'))
port = int(os.environ.get('mongoshport'))

client = pymongo.MongoClient(host=ip, port=port)
db = client['test']
collection = db['students']


def query(filter):
    # cursor = collection.find({"age": {"$gt": 18}})
    filter = eval(filter)
    cursor = collection.find(filter)
    return cursor
