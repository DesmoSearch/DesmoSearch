#when the !desmos command had no arguments ?=

import base64
import requests
from keep_alive import keep_alive

import discord
from discord.ext import commands
from discord import guild
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
import os
import requests
import json
import time
import re
from replit import db
import asyncio
import math

#https://stackoverflow.com/questions/38491722/reading-a-github-file-using-python-returns-html-tags
'''
url = 'https://raw.githubusercontent.com/DesmoSearch/DesmoSearch/main/data/thetitles.json'
req = requests.get(url)
if req.status_code == requests.codes.ok:
    req = req.json()
    print(len(req))
    db['thetitles']=req
else:
    print('Content was not found.')
'''

print(db.keys())
ParentGraphsList=db['ParentGraphsList']
thetitles=db['thetitles']
GraphsList=db['GraphsList']
objowner=db['objowner']
noofresults=5;

client = commands.Bot(command_prefix="_")
slash = SlashCommand(client, sync_commands=True)
token = os.environ.get("DISCORD_BOT_SECRET")

@client.event
async def on_ready():
  await client.change_presence(activity=discord.Game(name=f"on {len(client.guilds)} servers | {db['searches']} searches done!"))

@client.event
async def on_message(message): 
  pattern=re.compile(r"!desmos ([a-zA-Z0-9 ]{3,}|\/.*\/)")
  x=pattern.finditer(message.content)
  if message.author == client.user:
    return
  elif len(list(x))==1:
    db['searches']=db['searches']+1
    await on_ready()
    searchterm=[ii.group(1) for ii in pattern.finditer(message.content)][0]
    
    
    if "/" in searchterm:
      searchterm=searchterm[1:-1]
      
    print(f'"{searchterm}"')

    searchresult = [hash for hash, title in thetitles.items() if bool(re.search(searchterm, str(title))) or bool(re.search(searchterm, str(hash))) or bool(re.search(searchterm, str(objowner.get(str(hash),None))))]

    #https://gist.github.com/noaione/58cdd25a1cc19388021deb0a77582c97
    max_page=math.ceil(len(searchresult)/noofresults)
    first_run = True
    num = 1
    while True:
        if first_run:
            first_run = False
            msg = await message.channel.send(embed=createembed(num,searchterm,searchresult,max_page,message))

        reactmoji = []

        if max_page == 1 and num == 1:
            pass
        elif num == 1:
            reactmoji.append('⏩')
        elif num == max_page:
            reactmoji.append('⏪')
        elif num > 1 and num < max_page:
            reactmoji.extend(['⏪', '⏩'])

        reactmoji.append('✅')

        for react in reactmoji:
            await msg.add_reaction(react)
            

        def check_react(reaction, user):
            if reaction.message.id != msg.id:
                return False
            if user != message.author:
                return False
            if str(reaction.emoji) not in reactmoji:
                return False
            return True

        try:
            res, user = await client.wait_for('reaction_add', timeout=100.0, check=check_react)
        except asyncio.TimeoutError:
            return await msg.clear_reactions()
        if user != message.author:
            pass
        elif '⏪' in str(res.emoji):
            num = num - 1
            await msg.clear_reactions()
            await msg.edit(embed=createembed(num,searchterm,searchresult,max_page,message))
        elif '⏩' in str(res.emoji):
            num = num + 1
            await msg.clear_reactions()
            await msg.edit(embed=createembed(num,searchterm,searchresult,max_page,message))

        elif '✅' in str(res.emoji):
            #await message.delete()
            #return await msg.delete()
            return await msg.clear_reactions()

    
def createembed(num,searchterm,result,max_page,message):
  datahashes=result[noofresults*(num-1):noofresults*num+1]
  thedescription="".join(f'{(num-1)*noofresults+i+1}. [{thetitles[datahashes[i]]}](https://www.desmos.com/calculator/{datahashes[i]})\n'for i in range(len(datahashes)))
  embed = discord.Embed(color=0x19212d, title=str(len(result))+" graphs for \""+searchterm+"\"",description=thedescription)
  embed.set_author(name=str(message.author), icon_url=message.author.avatar_url)
  
  embed.set_footer(text="Page: "+str(num)+"/"+str(max_page))
  return embed
  


keep_alive()
client.run(token)
