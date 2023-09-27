import pymongo
import os
ip = str(os.environ.get('mongoship'))
port = int(os.environ.get('mongoshport'))

client = pymongo.MongoClient(host=ip, port=port)
db = client['test']
collection = db['students']


def updateOne(filter,json):
    filter = eval(filter)
    json = '{"$set": ' + json + '}'
    json = eval(json)
    result = collection.update_many(filter, json)
    return result


