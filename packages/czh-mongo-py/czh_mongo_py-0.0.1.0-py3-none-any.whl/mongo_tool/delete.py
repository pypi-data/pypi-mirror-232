import pymongo
import os
ip = str(os.environ.get('mongoship'))
port = int(os.environ.get('mongoshport'))

client = pymongo.MongoClient(host=ip, port=port)
db = client['test']
collection = db['students']


def deleteMany(filter):
    filter = eval(filter)
    exist = collection.find_one(filter)
    result = collection.delete_many(filter)
    return result

