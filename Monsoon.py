# Python 3.6
import discord
from discord.ext import commands
import re
import sys
import os
from pathlib import Path
import json
import secrets
import random
import time
import dropbox

if len(sys.argv) >= 2:
    TOKEN = sys.argv[1]
else:
    TOKEN = os.environ['MONSOON_TOKEN']

if len(sys.argv) == 3:
    DROPBOX_TOKEN = sys.argv[2]
else:
    DROPBOX_TOKEN = os.environ['DROPBOX_TOKEN']

dbx = dropbox.Dropbox(DROPBOX_TOKEN)

json_config_file_name = 'config.json'
greeting_file_name = 'greeting.txt'
dbxFolderName = '/MonsoonData'

monsoon = commands.Bot(command_prefix='monsoon.', max_messages=20000000)





@monsoon.event
async def on_ready():
    print('Logged in as')
    print(monsoon.user.name)
    print(monsoon.user.id)
    print('------')
    game = discord.CustomActivity(name="monsoon.rain-ffxiv.com")
    await monsoon.change_presence(activity=game)
    #random.seed(time.time())

@monsoon.event
async def on_member_join(member):
    greetingString = await get_greeting(member.guild)
    if greetingString and greetingString.strip():
        await member.send(greetingString)
    #await member.send(("__**Welcome to the Rain discord!**__\nI am Rain's management bot, so please **do not reply** directly to me."
    #                   "\n**Please review our rules at http://rules.rain-ffxiv.com.**\nPlease direct any questions or concerns to @Okashii#0001 or oka@rain-ffxiv.com." 
    #                   "\n\n**If you are here temporarily**, for instance, if you were invited as a pug for FFXIV, then you can ignore the rest of this message."
    #                   "\n\n__**Please type one of the following into the welcome-and-recruitment channel and await a reply from one of our Officers:**__"
    #                   "\n\n**monsoon.request Guest Starring**\nIf you are a friend of one of our FC members and also play FFXIV"
    #                   "\n\n**monsoon.request Rain**\nIf you are a member of our FC or wish to become one."
    #                   "\n\n**monsoon.request VRC**\nIf you are joining our VR Chat community."
    #                   "\n\n**monsoon.request ARK**\nIf you play or wish to play on one of our Ark Survival Evolved servers."))




def dropbox_upload_config(guild, file_name):
    with open(Path(guild.name, file_name), 'rb') as f:
        dbx.files_upload(f.read(),dbxFolderName+'/'+str(guild.name)+'/'+file_name, mode=dropbox.files.WriteMode.overwrite, mute=True)

def dropbox_download_config(guild, file_name):
    dbx.files_download_to_file(Path(guild.name, file_name), dbxFolderName+'/'+str(guild.name)+'/'+file_name)





async def setup_roles(guild):
    if not os.path.exists(str(guild.name)):
        try:
            os.makedirs(str(guild.name))
            dropbox_download_config(guild, json_config_file_name)
        except:
            default_roles = dict()
            default_roles['admin'] = secrets.token_urlsafe(24)
            default_roles['names']=[]
            default_roles['assignable']=[]
            os.makedirs(str(guild.name))
            with open(Path(guild.name, json_config_file_name), 'w+') as roles_file:
                json.dump(default_roles, roles_file)
            dropbox_upload_config(guild, json_config_file_name)

async def get_roles(guild):
    await setup_roles(guild)
    with open(Path(guild.name, json_config_file_name), 'r') as roles_file:
        roles = json.load(roles_file)
    return roles

async def update_roles(guild, roles):
    with open(Path(guild.name, json_config_file_name), 'w+') as roles_file:
        json.dump(roles, roles_file)
    dropbox_upload_config(guild, json_config_file_name)

async def setup_greeting(guild):
    #greetingString = greetingString.replace('\\n','\n') 
    if not os.path.exists(str(guild.name)):
        try:
            os.makedirs(str(guild.name))
            dropbox_download_config(guild, greeting_file_name)
        except:
            default_greeting = ''
            os.makedirs(str(guild.name))
            with open(Path(guild.name, greeting_file_name), 'w+') as greet_file:
                greet_file.write(default_greeting)
            dropbox_upload_config(guild, json_config_file_name)

async def get_greeting(guild):
    await setup_greeting(guild)
    with open(Path(guild.name, greeting_file_name), 'r') as greet_file:
        greetingString = greet_file.read()
    return greetingString

async def update_greeting(guild, greetingString):
    greetingString = greetingString.replace('\\n','\n')
    with open(Path(guild.name, greeting_file_name), 'w+') as greet_file:
        greet_file.write(greetingString)
    dropbox_upload_config(guild, greeting_file_name)




async def is_author_guild_admin(ctx):
    if not ctx.message.author.guild_permissions.administrator:
        await ctx.message.channel.send( "You do not have sufficient permissions.")
        return False
    else:
        return True

async def member_has_role(member, roleName, channel):
    try:
        if roleName.lower() in [y.name.lower() for y in member.roles]:
            return True
        return False
    except:
        await channel.send(("Failure to verify roles. Ask oka@rain-ffxiv.com to troubleshoot."))
        raise

async def is_in_guild_roles(roles, role_string):
    return await do_roles_match(roles, role_string, role_string)

async def is_in_list_string(listStringToCheck, stringToCheck):
    if stringToCheck.lower() in [y.lower() for y in listStringToCheck]:
        return True
    return False

async def do_roles_match(roles, role_string, real_role_string):
    role = discord.utils.get(roles, name=role_string)
    real_role = discord.utils.get(roles, name=real_role_string)
    roles_match = False
    if role is None:
        roles_match = False
    elif real_role is None:
        roles_match = False
    elif role.id == real_role.id:
        roles_match = True
    return [roles_match, role, real_role]

def parseStringArgsComma(stringArgs):
    stringArgs = ' '.join(stringArgs)
    listArgs = stringArgs.split(",")
    for i,s in enumerate(listArgs):
        listArgs[i]=s.lstrip().rstrip()
    return listArgs

def stripMention(mention):
    if mention.startswith('<@') and mention.endswith('>'):
        mention = mention[2:-1]
        if mention.startswith('!'):
            mention = mention[1:]
    return mention



@monsoon.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == monsoon.user:
        return
    await monsoon.process_commands(message)





@monsoon.command()
async def info(ctx):
    await ctx.send(("Hello, I am Monsoon.  I am a bot built to help moderate your server. \n"
                    "For more info, you can visit my website at http://monsoon.rain-ffxiv.com\n"
                    "If you have any issues, email oka@rain-ffxiv.com\n\n"
                    "__**General commands:**__\n"
                    " - **monsoon.info** - that's this command!\n"
                    " - **moonsoon.print_assignable_roles** - Prints all the roles that you can assign to or revoke from other users.\n"
                    " - **monsoon.request *role name*** - Notifies people with permission to assign the requested role that you wish to be assigned to that role.\n\n"
                    "__**Privileged commands:**__\n"
                    " - **monsoon.edit_role *@user, role name*** - assigns the role to the mentioned user. Be sure to include the comma, and make sure you are using an @mention for the user's name.\n"
                    " - **monsoon.edit_role *@user, role name, revoke*** - revokes the role from the mentioned user. Be sure to include the comma, and make sure you are using an @mention for the user's name.\n\n"
                    "__**Administrator commands:**__\n"
                    " - **monsoon.edit_assignable_role *first role name, second role name*** - gives members with the first role permission to assign or revoke the second role to/from other members. Don't forget the comma!\n"
                    " - **monsoon.edit_assignable_role *first role name, second role name, revoke*** - members with the first role LOSE their permission to assign or revoke the second role to/from other members. Don't forget the comma!\n"
                    " - **monsoon.edit_greeting *The greeting you want to send new members*** - when a member joins the server, they will get a private message from the bot according to the message you set with this command.\n"
                    " - **monsoon.preview_greeting** - get a preview of the greeting that you have set. If no greeting is set, you will not get a message.\n\n"))

@monsoon.command()
async def print_assignable_roles(ctx):
    try:
        commander = ctx.message.author
        roles = await get_roles(ctx.message.guild)
        '''adminCheck = await is_author_guild_admin(ctx)
        if adminCheck==False:
            return
        else:'''
        nameList = roles['names']
        for i,roleName in enumerate(nameList):
            roleMatch = await member_has_role(ctx.message.author,roleName,ctx.message.channel)
            if not roleMatch:
                continue
            count = len(roles['assignable'][i])
            if count > 0:
                if count == 1:
                    await ctx.message.channel.send( ("{}: you have the {} role, which has {} role that can be assigned: {}".format(ctx.message.author.mention, roleName, count, roles['assignable'][i])))
                elif count > 1:
                    await ctx.message.channel.send( ("{}: you have the {} role, which has {} roles that can be assigned: {}".format(ctx.message.author.mention, roleName, count, roles['assignable'][i])))

    except:
        await ctx.message.channel.send( ("Failure to verify. Ask oka@rain-ffxiv.com to troubleshoot."))
        raise

@monsoon.command()
async def request(ctx, *stringArgs):
    successFlag = False
    listArgs = parseStringArgsComma(stringArgs)
    rolenameArg = listArgs[0]
    [isInguildRoles, roleArg, garbage] = await is_in_guild_roles(ctx.message.guild.roles, rolenameArg)
    if not isInguildRoles:
        await ctx.message.channel.send( ("Specified role {} does not exist!".format(rolenameArg)))
        return
    try:
        roles = await get_roles(ctx.message.guild)
        indexOfRole = -1
        for i,listOfRoles in enumerate(roles['assignable']):
            isRoleInList = await is_in_list_string(listOfRoles, rolenameArg)
            if isRoleInList:
                [isRoleInguildRoles, elevatedRole, garbage] = await is_in_guild_roles(ctx.message.guild.roles, roles['names'][i])
                authorRoleMatch = await member_has_role(ctx.message.author,roles['names'][i],ctx.message.channel)
                if authorRoleMatch:
                    await ctx.message.channel.send( "{}, you can assign this role to yourself. Type monsoon.edit_role {}, {}".format(ctx.message.author.mention, ctx.message.author.mention, roleArg.name))
                else:
                    await ctx.message.channel.send( "{}, please assign {} the {} role.".format(elevatedRole.mention,ctx.message.author.mention,roleArg.name))
                successFlag = True
                break
        if not successFlag:
            adminUser = ctx.message.guild.get_member(int(stripMention(roles['admin']))) #discord.utils.get(ctx.message.guild.members, id=stripMention(roles['admin']))
            await ctx.message.channel.send( "{}, please assign {} the {} role.".format(adminUser.mention, ctx.message.author.mention,roleArg.name))
    except:
        await ctx.message.channel.send( ("Failure to verify. Ask oka@rain-ffxiv.com to troubleshoot."))
        raise

@monsoon.command()
async def edit_greeting(ctx, *stringArgs):
    hasPermission = await is_author_guild_admin(ctx)
    if not hasPermission:
        await ctx.message.channel.send( ("You do not have permission to edit the assignable roles. "
                                                         "You must be an administrator of the discord guild {}.".format(ctx.message.guild.name)))
        return
    greetingString = ' '.join(stringArgs)
    await update_greeting(ctx.message.guild, greetingString)

@monsoon.command()
async def preview_greeting(ctx):
    hasPermission = await is_author_guild_admin(ctx)
    if not hasPermission:
        await ctx.message.channel.send( ("You do not have permission to edit the assignable roles. "
                                                         "You must be an administrator of the discord guild {}.".format(ctx.message.guild.name)))
        return
    greetingString = await get_greeting(ctx.message.guild)
    if greetingString and greetingString.strip():
        await ctx.message.author.send(greetingString)

@monsoon.command()
async def edit_assignable_role(ctx, *stringArgs):
    hasPermission = await is_author_guild_admin(ctx)
    if not hasPermission:
        await ctx.message.channel.send( ("You do not have permission to edit the assignable roles. "
                                                         "You must be an administrator of the discord guild {}.".format(ctx.message.guild.name)))
        return
    listArgs = parseStringArgsComma(stringArgs)
    elevatedRolenameArg = listArgs[0]
    rolenameArg = listArgs[1]
    revoke = False
    if len(listArgs)==3:
        revoke = True
    [isElevatedRoleInguildRoles, elevatedRoleArg, garbage] = await is_in_guild_roles(ctx.message.guild.roles, elevatedRolenameArg)
    if not isElevatedRoleInguildRoles:
        await ctx.message.channel.send( ("Specified elevated role {} does not exist!".format(elevatedRolenameArg)))
        return
    elevatedRolenameArg = elevatedRoleArg.name
    [isRoleInguildRoles, roleArg, garbage] = await is_in_guild_roles(ctx.message.guild.roles, rolenameArg)
    if not isRoleInguildRoles:
        await ctx.message.channel.send( ("Specified role {} does not exist!".format(rolenameArg)))
        return
    rolenameArg = roleArg.name
    try:
        roles = await get_roles(ctx.message.guild)
        roles['admin'] = str(ctx.message.author.id)
        nameList = roles['names']
        if not elevatedRolenameArg in nameList: 
            roles['names'].append(elevatedRolenameArg)
            roles['assignable'].append([])
        i = nameList.index(elevatedRolenameArg)
        inAssignableRoles = rolenameArg in roles['assignable'][i]
        if revoke and inAssignableRoles:
            j = roles['assignable'][i].index(rolenameArg)
            roles['assignable'][i].pop(j)	
            await ctx.message.channel.send( ("Elevated role {} editing privileges for role {} have been revoked.".format(elevatedRolenameArg, rolenameArg)))			
        elif not revoke and not inAssignableRoles:
            roles['assignable'][i].append(rolenameArg)
            await ctx.message.channel.send( ("Elevated role {} members have been granted editing privileges for role {}.".format(elevatedRolenameArg, rolenameArg)))
        if not len(roles['assignable'][i]) > 0:
            roles['assignable'].pop(i)
            roles['names'].pop(i)
            await ctx.message.channel.send( ("Elevated role {} has been de-elevated.".format(elevatedRolenameArg)))
        await update_roles(ctx.message.guild, roles)
    except:
        await ctx.message.channel.send( ("Failure to verify. Ask oka@rain-ffxiv.com to troubleshoot."))
        raise

@monsoon.command()
async def edit_role(ctx, *stringArgs):
    successFlag = False
    listArgs = parseStringArgsComma(stringArgs)
    usermentionArg = listArgs[0]
    usernameArg = stripMention(usermentionArg)
    rolenameArg = listArgs[1]
    revoke = False
    if len(listArgs)==3:
        revoke = True
    [isInguildRoles, roleArg, garbage] = await is_in_guild_roles(ctx.message.guild.roles, rolenameArg)
    if not isInguildRoles:
        await ctx.message.channel.send( ("Specified role {} does not exist!".format(rolenameArg)))
        return
		
    userArg = ctx.message.guild.get_member(int(usernameArg)) #discord.utils.get(ctx.message.guild.members, id=usernameArg)
    #for i,member in enumerate(ctx.message.guild.members):
    #    if member.id == usernameArg:
    #        userArg = member
    #        break

    print(userArg)

    if userArg is None:
        await ctx.message.channel.send( ("Please contact oka@rain-ffxiv.com. "
                                                         "Finding members by mention is not working "
                                                         "for this member, and this error must be "
                                                         "addressed in the bot code."))
        return
    try:
        roles = await get_roles(ctx.message.guild)
        nameList = roles['names']
        for i,elevatedRoleName in enumerate(nameList):
            authorRoleMatch = await member_has_role(ctx.message.author,elevatedRoleName, ctx.message.channel)
            if not authorRoleMatch:
                continue
            isInAssignableRoles = await is_in_list_string(roles['assignable'][i], rolenameArg)
            if not isInAssignableRoles:
                continue
            userRoleMatch = await member_has_role(userArg, elevatedRoleName, ctx.message.channel)
            if userRoleMatch:
                successFlag = False
                break
            successFlag = True
        if successFlag:
            if not revoke:
                await userArg.add_roles(roleArg)#await monsoon.add_roles(userArg, roleArg)
                await ctx.message.channel.send( ("{} has assigned the {} role to {}".format(ctx.message.author.mention, rolenameArg, userArg.mention)))
            else:
                await userArg.remove_roles(roleArg)
                await ctx.message.channel.send( ("{} has revoked the {} role from {}".format(ctx.message.author.mention, rolenameArg, userArg.mention)))
        else:
            await ctx.message.channel.send( ("{}: your command failed. Double check the format and remember that you may not change role assignments for other elevated users.".format(ctx.message.author.mention)))
    except:
        await ctx.message.channel.send( ("Failure to verify. Ask oka@rain-ffxiv.com to troubleshoot."))
        raise





















monsoon.run(TOKEN, reconnect=True)