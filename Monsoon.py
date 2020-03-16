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

if len(sys.argv) == 2:
    TOKEN = sys.argv[1]
else:
    TOKEN = os.environ['MONSOON_TOKEN']
    '''print("You must provide the Discord Bot's token.")
    sys.exit()'''

json_config_file_name = 'config.json'

monsoon = commands.Bot(command_prefix='monsoon.', max_messages=20000000)


@monsoon.event
async def on_ready():
    print('Logged in as')
    print(monsoon.user.name)
    print(monsoon.user.id)
    print('------')
    await monsoon.change_presence(game=discord.Game(name="www.rain-ffxiv.com", type=0, url="http://www.rain-ffxiv.com"))
    #random.seed(time.time())





async def setup_roles(server):
    if not os.path.exists(str(server.name)):
        default_roles = dict()
        default_roles['admin'] = secrets.token_urlsafe(24)
        default_roles['names']=[]
        default_roles['assignable']=[]
        os.makedirs(str(server.name))
        with open(Path(server.name, json_config_file_name), 'w+') as roles_file:
            json.dump(default_roles, roles_file)

async def get_roles(server):
    await setup_roles(server)
    with open(Path(server.name, json_config_file_name), 'r') as roles_file:
        roles = json.load(roles_file)
    return roles

async def update_roles(server, roles):
    with open(Path(server.name, json_config_file_name), 'w+') as roles_file:
        json.dump(roles, roles_file)





async def is_author_server_admin(ctx):
    if not ctx.message.author.server_permissions.administrator:
        await monsoon.send_message(ctx.message.channel, "You do not have sufficient permissions.")
        return False
    else:
        return True

async def member_has_role(member, roleName):
    try:
        if roleName.lower() in [y.name.lower() for y in member.roles]:
            return True
        return False
    except:
        await monsoon.send_message(ctx.message.channel,("Failure to verify roles. Ask oka@rain-ffxiv.com to troubleshoot."))
        raise

async def is_in_server_roles(roles, role_string):
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

@monsoon.command(pass_context=True)
async def print_assignable_roles(ctx):
    try:
        commander = ctx.message.author
        roles = await get_roles(ctx.message.server)
        '''adminCheck = await is_author_server_admin(ctx)
        if adminCheck==False:
            return
        else:'''
        nameList = roles['names']
        for i,roleName in enumerate(nameList):
            roleMatch = await member_has_role(ctx.message.author,roleName)
            if not roleMatch:
                continue
            count = len(roles['assignable'][i])
            if count > 0:
                if count == 1:
                    await monsoon.send_message(ctx.message.channel, ("{}: you have the {} role, which has {} role that can be assigned: {}".format(ctx.message.author.mention, roleName, count, roles['assignable'][i])))
                elif count > 1:
                    await monsoon.send_message(ctx.message.channel, ("{}: you have the {} role, which has {} roles that can be assigned: {}".format(ctx.message.author.mention, roleName, count, roles['assignable'][i])))

    except:
        await monsoon.send_message(ctx.message.channel, ("Failure to verify. Ask oka@rain-ffxiv.com to troubleshoot."))
        raise

@monsoon.command(pass_context=True)
async def request(ctx, *stringArgs):
    successFlag = False
    listArgs = parseStringArgsComma(stringArgs)
    rolenameArg = listArgs[0]
    [isInServerRoles, roleArg, garbage] = await is_in_server_roles(ctx.message.server.roles, rolenameArg)
    if not isInServerRoles:
        await monsoon.send_message(ctx.message.channel, ("Specified role {} does not exist!".format(rolenameArg)))
        return
    try:
        roles = await get_roles(ctx.message.server)
        indexOfRole = -1
        for i,listOfRoles in enumerate(roles['assignable']):
            isRoleInList = await is_in_list_string(listOfRoles, rolenameArg)
            if isRoleInList:
                [isRoleInServerRoles, elevatedRole, garbage] = await is_in_server_roles(ctx.message.server.roles, roles['names'][i])
                authorRoleMatch = await member_has_role(ctx.message.author,roles['names'][i])
                if authorRoleMatch:
                    await monsoon.send_message(ctx.message.channel, "{}, you can assign this role to yourself. Type monsoon.edit_role {}, {}".format(ctx.message.author.mention, ctx.message.author.mention, roleArg.name))
                else:
                    await monsoon.send_message(ctx.message.channel, "{}, please assign {} the {} role.".format(elevatedRole.mention,ctx.message.author.mention,roleArg.name))
                successFlag = True
                break
        if not successFlag:
            adminUser = discord.utils.get(ctx.message.server.members, id=stripMention(roles['admin']))
            await monsoon.send_message(ctx.message.channel, "{}, please assign {} the {} role.".format(adminUser.mention, ctx.message.author.mention,roleArg.name))
    except:
        await monsoon.send_message(ctx.message.channel, ("Failure to verify. Ask oka@rain-ffxiv.com to troubleshoot."))
        raise

@monsoon.command(pass_context=True)
async def edit_assignable_role(ctx, *stringArgs):
    hasPermission = await is_author_server_admin(ctx)
    if not hasPermission:
        await monsoon.send_message(ctx.message.channel, ("You do not have permission to edit the assignable roles. "
                                                         "You must be an administrator of the discord server {}.".format(ctx.message.server.name)))
        return
    listArgs = parseStringArgsComma(stringArgs)
    elevatedRolenameArg = listArgs[0]
    rolenameArg = listArgs[1]
    revoke = False
    if len(listArgs)==3:
        revoke = True
    [isElevatedRoleInServerRoles, elevatedRoleArg, garbage] = await is_in_server_roles(ctx.message.server.roles, elevatedRolenameArg)
    if not isElevatedRoleInServerRoles:
        await monsoon.send_message(ctx.message.channel, ("Specified elevated role {} does not exist!".format(elevatedRolenameArg)))
        return
    elevatedRolenameArg = elevatedRoleArg.name
    [isRoleInServerRoles, roleArg, garbage] = await is_in_server_roles(ctx.message.server.roles, rolenameArg)
    if not isRoleInServerRoles:
        await monsoon.send_message(ctx.message.channel, ("Specified role {} does not exist!".format(rolenameArg)))
        return
    rolenameArg = roleArg.name
    try:
        roles = await get_roles(ctx.message.server)
        roles['admin'] = ctx.message.author.id
        nameList = roles['names']
        if not elevatedRolenameArg in nameList: 
            roles['names'].append(elevatedRolenameArg)
            roles['assignable'].append([])
        i = nameList.index(elevatedRolenameArg)
        inAssignableRoles = rolenameArg in roles['assignable'][i]
        if revoke and inAssignableRoles:
            j = roles['assignable'][i].index(rolenameArg)
            roles['assignable'][i].pop(j)	
            await monsoon.send_message(ctx.message.channel, ("Elevated role {} editing privileges for role {} have been revoked.".format(elevatedRolenameArg, rolenameArg)))			
        elif not revoke and not inAssignableRoles:
            roles['assignable'][i].append(rolenameArg)
            await monsoon.send_message(ctx.message.channel, ("Elevated role {} members have been granted editing privileges for role {}.".format(elevatedRolenameArg, rolenameArg)))
        if not len(roles['assignable'][i]) > 0:
            roles['assignable'].pop(i)
            roles['names'].pop(i)
            await monsoon.send_message(ctx.message.channel, ("Elevated role {} has been de-elevated.".format(elevatedRolenameArg)))
        await update_roles(ctx.message.server, roles)
    except:
        await monsoon.send_message(ctx.message.channel, ("Failure to verify. Ask oka@rain-ffxiv.com to troubleshoot."))
        raise

@monsoon.command(pass_context=True)
async def edit_role(ctx, *stringArgs):
    successFlag = False
    listArgs = parseStringArgsComma(stringArgs)
    usermentionArg = listArgs[0]
    usernameArg = stripMention(usermentionArg)
    rolenameArg = listArgs[1]
    revoke = False
    if len(listArgs)==3:
        revoke = True
    [isInServerRoles, roleArg, garbage] = await is_in_server_roles(ctx.message.server.roles, rolenameArg)
    if not isInServerRoles:
        await monsoon.send_message(ctx.message.channel, ("Specified role {} does not exist!".format(rolenameArg)))
        return
    userArg = discord.utils.get(ctx.message.server.members, id=usernameArg)
    if userArg is None:
        await monsoon.send_message(ctx.message.channel, ("Please contact oka@rain-ffxiv.com. "
                                                         "Finding members by mention is not working "
                                                         "for this member, and this error must be "
                                                         "addressed in the bot code."))
        return
    try:
        roles = await get_roles(ctx.message.server)
        nameList = roles['names']
        for i,elevatedRoleName in enumerate(nameList):
            authorRoleMatch = await member_has_role(ctx.message.author,elevatedRoleName)
            if not authorRoleMatch:
                continue
            isInAssignableRoles = await is_in_list_string(roles['assignable'][i], rolenameArg)
            if not isInAssignableRoles:
                continue
            userRoleMatch = await member_has_role(userArg, elevatedRoleName)
            if userRoleMatch:
                successFlag = False
                break
            successFlag = True
        if successFlag:
            if not revoke:
                await monsoon.add_roles(userArg, roleArg)
                await monsoon.send_message(ctx.message.channel, ("{} has assigned the {} role to {}".format(ctx.message.author.mention, rolenameArg, userArg.mention)))
            else:
                await monsoon.remove_roles(userArg, roleArg)
                await monsoon.send_message(ctx.message.channel, ("{} has revoked the {} role from {}".format(ctx.message.author.mention, rolenameArg, userArg.mention)))
        else:
            await monsoon.send_message(ctx.message.channel, ("{}: your command failed. Double check the format and remember that you may not change role assignments for other elevated users.".format(ctx.message.author.mention)))
    except:
        await monsoon.send_message(ctx.message.channel, ("Failure to verify. Ask oka@rain-ffxiv.com to troubleshoot."))
        raise





















monsoon.run(TOKEN, reconnect=True)