import pymongo
import requests
import time
from colours import bcolours

MClient = pymongo.MongoClient('mongodb://localhost:27017')

DataStorage = MClient['DataStorage']
KeyStore = DataStorage['KeyStore']
AuctionData = DataStorage['AuctionData']
KeyInfo = DataStorage['KeyInfo']

#Check if user has api key
def check_api_key(key):
    data = requests.get(f'https://api.hypixel.net/key?key={key}').json()
    print(f'{bcolours.Request}Request{bcolours.ENDC} Request was successful')
    #Get the owner's username
    data['ownerName'] = requests.get(f'https://sessionserver.mojang.com/session/minecraft/profile/{data["record"]["owner"]}').json()['name']
    KeyInfo.insert_one(data)
    print(f'{bcolours.PyMongo}MongoDB{bcolours.ENDC} Inserted infomation from this API call')
    if data['success']:
        return True
    else:
        return False

#Adds the api key to the database
def add_api_key(ctx, key):
    if check_api_key(key):
        info = {'gid': ctx.guild.id, 'GuildName': ctx.guild.name, 'key': key}
        KeyStore.insert_one(info)
        return 'Success'
    elif not check_api_key(key):
        print(f'{bcolours.FAIL}Python{bcolours.ENDC} API key is not valid')
        return 'Error'
    else:
        return 'Error'


def exists(ctx):
    gid = ctx.guild.id
    guildObj = KeyStore.find({'gid': gid})
    try:
        gkey = guildObj[0]['key']
        return True
    except IndexError or KeyError:
        return False