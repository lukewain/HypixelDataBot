from h11 import Data
import pymongo

client = pymongo.MongoClient('mongodb://localhost:27017')

DataStorage = client['DataStorage']
KeyInfo = DataStorage['KeyInfo']

for i in KeyInfo.find():
    if i['record']['key'] == '4fe777d7-b24e-4d31-a470-ad16d46f9e67':
        print(i['record']['totalQueries'])