import pymongo
import os
ip = str(os.environ.get('mongoship'))
port = int(os.environ.get('mongoshport'))

client = pymongo.MongoClient(host=ip, port=port)
db = client['test']
collection = db['students']


def insertOne(file_data):
    with open(file_data, 'r') as file_js:
        file_data = file_js.read()
    print(file_data)
    file_data = eval(file_data)
    result = collection.insert_one(file_data)
    return result


