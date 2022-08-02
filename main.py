from functools import total_ordering
import discord
from discord.ext import tasks
import time
import datetime
import requests
import pymongo
from dtoken import TOKEN
from colours import bcolours
import filterAuctionData
from pprint import pprint

MClient = pymongo.MongoClient('mongodb://localhost:27017')

client = discord.Bot()

DataStorage = MClient['DataStorage']
KeyStore = DataStorage['KeyStore']
AuctionData = DataStorage['AuctionData']
GuildData = DataStorage['GuildData']
PlayerData = DataStorage['PlayerData']
KeyInfo = DataStorage['KeyInfo']


# @tasks.loop(minutes=3)


@client.event
async def on_ready():
    print(f"{bcolours.Discord}Discord{bcolours.ENDC} Bot logged in")
    logChannel = await client.fetch_channel(1003720327467110462)
    await logChannel.send("Bot logged in successfully")


@client.slash_command(name="setkey", description="Sets your hypixel api key")
async def setkey(ctx, key: discord.Option(optional=True)):
    if key is None:
        error = discord.Embed(title="Stupid fucker", description="You gotta give me an API key")
        await ctx.respond(embed=error)
    else:
        if not filterAuctionData.exists(ctx):
            enterKey = filterAuctionData.add_api_key(ctx, key)
            if enterKey == 'Success':
                await ctx.respond(f"The API key has been set.")
            else:
                await ctx.respond(f"There was an error.")
        else:
            KeyStore.update_one({'gid': ctx.guild.id}, {'$set': {'key': key}})
            await ctx.respond(f"The API key has been updated.")


@client.slash_command(name="removekey", description="Removes your key from the database")
async def removekey(ctx):
    if filterAuctionData.exists(ctx):
        keyobj = KeyStore.find({'gid': ctx.guild.id})[0]
        print(f"{bcolours.PyMongo}MongoDB{bcolours.ENDC} Found {ctx.guild.name}'s key")
        gkey = keyobj['key']
        toDelete = {'gid': ctx.guild.id, 'key': gkey}
        KeyStore.delete_one(toDelete)
        print(f"{bcolours.PyMongo}MongoDB{bcolours.ENDC} Deleted {ctx.guild.name}'s key")
        await ctx.respond("Your API key has been removed from the database")


@client.slash_command(name="showkey", description="Shows your API key")
async def showkey(ctx):
    if filterAuctionData.exists(ctx):
        await ctx.respond(f"Your API key is: `{KeyStore.find({'gid': ctx.guild.id})[0]['key']}`")
    else:
        await ctx.respond(f"You do not have an API key set")


@client.slash_command(name="requestcount", description="Shows the number of requests your API key has made")
async def requestcount(ctx):
    if filterAuctionData.exists(ctx):
        guildKey = KeyStore.find({'gid': ctx.guild.id})
        apikey = guildKey[0]['key']
        totalQueries = requests.get(f"https://api.hypixel.net/key?key={apikey}").json()
        print(f"{bcolours.Request}Request{bcolours.ENDC} Request was successful")
        percentageUsed = (100/totalQueries['record']['limit']) * totalQueries['record']['queriesInPastMin']
        await ctx.respond(f"Your key has made `{totalQueries['record']['totalQueries']:,}` total requests\n`{totalQueries['record']['queriesInPastMin']:,}` were in the past minute\nYou have used `{percentageUsed:.2f}%` of your queries")
    else:
        await ctx.respond(f"Your do not have an API key set")

client.run(TOKEN)