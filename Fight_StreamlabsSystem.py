#!/usr/bin/python
# -*- coding: utf-8 -*-
#Parent = Parent # pylint: disable=invalid-name
"""Minigames script to add a collection of games for viwers to play"""
#---------------------------------------
# Libraries and references
#---------------------------------------
import codecs
import json
import os
import re
import ctypes
import winsound
from time import time

#---------------------------------------
# Script information
#---------------------------------------
ScriptName = "Fight"
Website = "https://www.twitch.tv/Xailran"
Creator = "Xailran"
Version = "1.3.3"
Description = "Let viewers fight each other with a variety of weapons"

#---------------------------------------
# Versions
#---------------------------------------
"""
1.3.3 - Fixed all messages to be customizable
1.3.2 - Made changes to file handling, so that weapons and description files are no longer reset on an update.
1.3.1 - Added YouTube compatibility
1.3.0 - Added Response Reset button.
1.2.2 - Changed when cooldown starts
1.2.1 - Mixer-specific and general bug fixes
1.2.0 - Added $addweapon() parameter.
1.1.1 - Fixed script to properly work for Mixer and YT. Also fixed bug with using the "accept" settings
1.1.0 - Added UI options for viewers to select amount of points to fight for, and option for users to "accept" a fight before it actually happens. (Funded by twitch.tv/GodOfRanch)
1.0.0 - Initial Release
"""

#---------------------------------------
# Variables
#---------------------------------------
settingsFile = os.path.join(os.path.dirname(__file__), "settings.json")
MessageBox = ctypes.windll.user32.MessageBoxW
Weapons = os.path.join(os.path.dirname(__file__), "Weapons.txt")
FightDescriptions = os.path.join(os.path.dirname(__file__), "FightResponses.txt")
MB_YES = 6

#---------------------------------------
# Settings functions
#---------------------------------------
def SetDefaults():
	"""Set default settings function"""
	winsound.MessageBeep()
	returnValue = MessageBox(0, u"You are about to reset the settings, "
								"are you sure you want to contine?"
							 , u"Reset settings file?", 4)

	if returnValue == MB_YES:
		Settings(None, None).Save(settingsFile)
		MessageBox(0, u"Settings successfully restored to default values!"
					  "\r\nMake sure to reload script to load new values into UI"
				   , u"Reset complete!", 0)

def ReloadSettings(jsonData):
	"""Reload settings on Save"""
	global MySet
	MySet.Reload(jsonData)
#---------------------------------------
# UI functions
#---------------------------------------

def OpenReadMe():
	"""Open the readme.txt in the scripts folder"""
	location = os.path.join(os.path.dirname(__file__), "README.txt")
	os.startfile(location)
	
def OpenFolder():
	"""Open Minigames Script Folder"""
	location = (os.path.dirname(os.path.realpath(__file__)))
	os.startfile(location)
	
def WeaponsFile():
	"""Open file with weapons data"""
	location = os.path.join(os.path.dirname(__file__), "Weapons.txt")
	os.startfile(location)

def FightDescriptionsFile():
	"""Open file with weapons data"""
	location = os.path.join(os.path.dirname(__file__), "FightResponses.txt")
	os.startfile(location)

def ResetWeaponsFile():
	"""Resets weapons file back to defaults"""
	winsound.MessageBeep()
	returnValue = MessageBox(0, u"You are about to reset the weapons file, "
								"are you sure you want to continue?"
							 , u"Reset weapons file?", 4)

	if returnValue == MB_YES:
		CreateWeapons()
		MessageBox(0, u"Weapons successfully restored to default values!"
					, u"Reset complete!", 0)

def ResetResponsesFile():
	"""Resets responses file back to defaults"""
	winsound.MessageBeep()
	returnValue = MessageBox(0, u"You are about to reset the responses file, "
								"are you sure you want to continue?"
							 , u"Reset responses file?", 4)

	if returnValue == MB_YES:
		CreateResponses()
		MessageBox(0, u"Responses successfully restored to default values!"
					, u"Reset complete!", 0)

#---------------------------------------
# Optional functions
#---------------------------------------
def IsOnCooldown(data, command):
	"""Handle cooldowns"""
	cooldown = Parent.IsOnCooldown(ScriptName, command)
	usercooldown = Parent.IsOnUserCooldown(ScriptName, command, data.User)
	caster = (Parent.HasPermission(data.User, "Caster", "") and MySet.castercd)

	if (cooldown or usercooldown) and caster is False:

		if MySet.usecd:
			cooldownDuration = Parent.GetCooldownDuration(ScriptName, command)
			userCDD = Parent.GetUserCooldownDuration(ScriptName, command, data.User)

			if cooldownDuration > userCDD:
				SendResp(data, MySet.oncooldown.format(data.UserName, cooldownDuration))

			else:
				SendResp(data, MySet.onusercooldown.format(data.UserName, userCDD))
		return False
	return True

def SendResp(data, message):
    """Sends message to Stream or discord chat depending on settings"""
    message = message.replace("$user", data.UserName)
    message = message.replace("$currencyname", Parent.GetCurrencyName())
    message = message.replace("$target", data.GetParam(1))

    if not data.IsFromDiscord() and not data.IsWhisper():
        Parent.SendStreamMessage(message)

    if not data.IsFromDiscord() and data.IsWhisper():
        Parent.SendStreamWhisper(data.User, message)

    if data.IsFromDiscord() and not data.IsWhisper():
        Parent.SendDiscordmessage(message)

    if data.IsFromDiscord() and data.IsWhisper():
        Parent.SendDiscordDM(data.User, message)

def HasPermission(data, permission, permissioninfo):
    """Return true or false dending on if the user has permission.
    Also sends permission response if user doesn't"""
    if not Parent.HasPermission(data.User, permission, permissioninfo):
        message = MySet.notperm.format(data.UserName, permission, permissioninfo)
        SendResp(data, message)
        return False
    return True
	
#---------------------------------------
# [Required] functions
#---------------------------------------
def Init():
	"""data on Load, required function"""
	global MySet
	MySet = Settings(Parent, settingsFile)
	global parent
	parent = Parent
	global fightDict
	fightDict = {}
	
def Execute(data):
	"""Required Execute data function"""
	if not data.IsWhisper() and not data.IsFromDiscord() and data.GetParam(0).lower() == MySet.command.lower():
		if not HasPermission(data, MySet.FightPermission, MySet.FightPermissionInfo):
			return
		if MySet.onlylive and not Parent.IsLive():
			message = MySet.respNotLive.format(data.UserName)
			SendResp(data, message)
			return
		if IsOnCooldown(data, "fight"):
			Fight(data)
	
	if not data.IsWhisper() and not data.IsFromDiscord() and MySet.NeedApproval and data.GetParam(0).lower() == MySet.acceptcommand.lower():
		global fightDict
		challenge = False
		for user, userdict in fightDict.items():
			if userdict["timestamp"] + MySet.accepttime < int(time()):
				del fightDict[user]
			else:
				if userdict["opponentname"].lower() == data.UserName.lower():
					if data.IsFromYoutube():
						userdict["opponentid"] = data.User
					challenge = True
					Attack(userdict["data"], userdict)
					del fightDict[user]
					break
		if not challenge:
			message = MySet.nochallenge.format(data.UserName)
			SendResp(data, message)

def Tick():
	"""Required tick function"""
	return

def Parse(parseString, userid, username, targetid, targetname, message):
	"""Adds parameters to be used in commands"""
	#Add Weapon parameter
	#Group 1 = whole parameter, group 2 = weapon to be added, group 3 = success message, group 4 = failure message
	aw = re.match('^.*(\$addweapon\("?([^"]+)"?,\s?"?([^"]*)"?,\s?"?([^"]+)"?\)).*', parseString)
	if aw:
		with codecs.open(Weapons, encoding="utf-8-sig", mode="r") as file:
			Item = [line.strip().lower() for line in file]
		if aw.group(2).lower() in Item or aw.group(2) == "":
			#Weapon already exists
			parseString = parseString.replace(aw.group(1), aw.group(4))
		else:
			#Weapon needs to be added
			Item.append(aw.group(2))
			Item.sort()
			with codecs.open(Weapons, "w", "utf-8") as f:
				filedata = Item.pop(0)
				for x in Item:
					filedata += "\r\n" + x
				f.write(filedata)
			parseString = parseString.replace(aw.group(1), aw.group(3))
	return parseString
		
#---------------------------------------
# [Optional] Fight functions
#---------------------------------------
def Fight(data):
	"""Full setup for attack function"""
	#Establishes opponent
	global MySet
	userfightdict = {"data":data}
	userfightdict["opponentname"] = data.GetParam(1).replace("@", "")
	viewerlist = [x for x in Parent.GetViewerList()]
	if data.IsFromTwitch():
		viewerlist.append(Parent.GetChannelName())
	if userfightdict["opponentname"] == "":
		message = MySet.needinfo.format(data.UserName, MySet.command)
		SendResp(data, message)
		return
	if userfightdict["opponentname"].lower() == data.UserName.lower():
		message = MySet.attackself.format(data.UserName)
		SendResp(data, message)
		return
	check = False
	if data.IsFromYoutube():
		check = True
		MySet.NeedApproval = True
		userfightdict["opponentname"] = Parent.GetDisplayName(userfightdict["opponentname"].lower())
		userfightdict["opponentid"] = userfightdict["opponentname"].lower()
	else:
		for x in viewerlist:
			if userfightdict["opponentname"].lower() == Parent.GetDisplayName(x.lower()).lower():
				userfightdict["opponentname"] = Parent.GetDisplayName(x)
				userfightdict["opponentid"] = x.lower()
				check = True
				break
	if not check:
		message = MySet.targetoffline.format(data.UserName, userfightdict["opponentname"])
		SendResp(data, message)
		return

	#Sets parameters
	userfightdict["UPoints"] = Parent.GetPoints(data.User)
	userfightdict["TPoints"] = Parent.GetPoints(userfightdict["opponentid"])
	#Sets command cost
	if MySet.UserChoiceSetting == "Standard" or MySet.UserChoiceSetting == "Default" and data.GetParam(2):
		try:
			userfightdict["fightpoints"] = int(data.GetParam(2))
		except:
			message = MySet.outsiderange.format(data.UserName, str(MySet.FightMinValue), str(MySet.FightMaxValue), MySet.command)
			SendResp(data,message)
			return
		else:
			if not MySet.FightMinValue <= userfightdict["fightpoints"] <= MySet.FightMaxValue:
				message = MySet.outsiderange.format(data.UserName, str(MySet.FightMinValue), str(MySet.FightMaxValue), MySet.command)
				SendResp(data, message)
				return
	else:
		if MySet.FightSetting == "Constant":
			userfightdict["fightpoints"] = MySet.FightCValue
		else:
			if MySet.FightMinValue < MySet.FightMaxValue:
				userfightdict["fightpoints"] = Parent.GetRandom(MySet.FightMinValue, MySet.FightMaxValue+1)
			else: 
				userfightdict["fightpoints"] = Parent.GetRandom(MySet.FightMaxValue, MySet.FightMinValue+1)
	#Checks that all parties have enough points
	if Parent.GetPoints(data.User) < userfightdict["fightpoints"]:
		message = MySet.notenough.format(data.UserName, str(userfightdict["fightpoints"]), Parent.GetCurrencyName(), str(userfightdict["UPoints"]))
		SendResp(data, message)
		return
	if userfightdict["TPoints"] < userfightdict["fightpoints"]:
		message = MySet.opponentnotenough.format(userfightdict["opponentname"], str(userfightdict["fightpoints"]), Parent.GetCurrencyName(), str(userfightdict["TPoints"]))
		SendResp(data, message)
		return
	#Approval system
	Parent.AddCooldown(ScriptName,"fight",MySet.timerCooldown)
	Parent.AddUserCooldown(ScriptName,"fight",userfightdict["data"].User,MySet.timerUserCooldown)
	if MySet.NeedApproval:
		global fightDict
		userfightdict["timestamp"] = int(time())
		fightDict[data.UserName] = userfightdict
		message = MySet.challengeissued.format(data.UserName, userfightdict["opponentname"], MySet.acceptcommand, str(MySet.accepttime))
		SendResp(data, message)
	else:
		Attack(data, userfightdict)

def Attack(data, userfightdict):
	"""Handles the actual fight component"""
	#Loads weapons
	if not os.path.exists(Weapons):
		CreateWeapons()
	with codecs.open(Weapons, encoding="utf-8-sig", mode="r") as file:
		Item = [line.strip() for line in file]
		UWeapon = Item[Parent.GetRandom(0, len(Item))]
		OWeapon = Item[Parent.GetRandom(0, len(Item))]
		count = 0
		while UWeapon == OWeapon:
			OWeapon = Item[Parent.GetRandom(0, len(Item))]
			count = count + 1
			if count == 3:
				message = MySet.identicalweapons
				SendResp(userfightdict["data"], message)
				break
	#Loads fight message
	if not os.path.exists(FightDescriptions):
		CreateResponses()
	with codecs.open(FightDescriptions, encoding="utf-8-sig", mode="r") as file:
		Item = [line.strip() for line in file]
		VictoryMessage = Item[Parent.GetRandom(1, len(Item))]
	#Determines winner
	if MySet.FightAttWinChance >= Parent.GetRandom(0, 101):
		Parent.RemovePoints(userfightdict["opponentid"], userfightdict["opponentname"], userfightdict["fightpoints"])
		Parent.AddPoints(userfightdict["data"].User,userfightdict["data"].UserName,userfightdict["fightpoints"])
		message = VictoryMessage.format(userfightdict["data"].UserName, UWeapon, userfightdict["opponentname"], OWeapon)
		SendResp(userfightdict["data"], message)
		message = MySet.userwon.format(userfightdict["data"].UserName, userfightdict["opponentname"], userfightdict["fightpoints"], Parent.GetCurrencyName())
		SendResp(userfightdict["data"], message)
	else:
		Parent.RemovePoints(userfightdict["data"].User,userfightdict["data"].UserName, userfightdict["fightpoints"])
		Parent.AddPoints(userfightdict["opponentid"], userfightdict["opponentname"], userfightdict["fightpoints"])
		message = VictoryMessage.format(userfightdict["opponentname"], OWeapon, userfightdict["data"].UserName, UWeapon)
		SendResp(userfightdict["data"], message)
		message = MySet.targetwon.format(userfightdict["data"].UserName, userfightdict["opponentname"], userfightdict["fightpoints"], Parent.GetCurrencyName())
		SendResp(userfightdict["data"], message)

def CreateWeapons():
	"""Replaces/creates weapons file with default weapons"""
	with codecs.open(Weapons, "w", "utf-8") as f:
		textline = "apple\r\naxe\r\nboomerang\r\nchainsaw\r\ngolf club\r\npistol\r\nspear\r\nspoon\r\ntaco\r\ntrain"
		f.write(textline)

def CreateResponses():
	"""Replaces/creates responses file with default responses"""
	with codecs.open(FightDescriptions, "w", "utf-8") as f:
		textline = "Formatting: {0} = winner, {1} = winner's weapon, {2} = loser, {3} = loser's weapon\r\n{0} used a(n) {1} to fight {2}, and crushed in their skull!\r\nFailure! Not for you though {0}. Your glorious {1} pulverised {2}'s {3}.\r\nAhhh, victory! {0}'s fantastic {1} smashed {2} with their {3}.\r\nWith a {1}, {0} attacked {2}. Even with their {3}. {2} could do nothing to win this fight!\r\n{2} used a(n) {3} with horrible results! {0} with their {1} obliterated them!\r\nAhhh, victory! Not for you though {2}. Your puny {3} lost against {0}'s {1}.\r\n{0} used a(n) {1} to fight {2} who used a(n) {3}, and {0} won!"
		f.write(textline)

#---------------------------------------
# Classes
#---------------------------------------
class Settings:
	"""" Loads settings from file if file is found if not uses default values"""

	# The 'default' variable names need to match UI_Config
	def __init__(self, parent, settingsFile=None):
		if settingsFile and os.path.isfile(settingsFile):
			with codecs.open(settingsFile, encoding='utf-8-sig', mode='r') as f:
				self.__dict__ = json.load(f, encoding='utf-8-sig')
		else: #set variables if no custom settings file is found
			self.onlylive = False
			self.permission = "Everyone"
			self.PermissionInfo = ""
			self.castercd = True
			self.usecd = True
			self.timerCooldown = 5
			self.oncooldown = "{0} the command is still on cooldown for {1} seconds!"
			self.timerUserCooldown = 30
			self.onusercooldown = "{0} the command is still on user cooldown for {1} seconds!"
			self.command = "!fight"
			self.FightPermission = "Everyone"
			self.FightPermissionInfo = ""
			self.FightAttWinChance = 50
			self.UserChoiceSetting = "Default"
			self.FightSetting = "Constant"
			self.FightCValue = 250
			self.FightMinValue = 100
			self.FightMaxValue = 500
			self.NeedApproval = False
			self.acceptcommand = "accept"
			self.accepttime = 180
			self.challengeissued = "{0} has issued a challenge against {1}; Type {2} in chat within the next {3} seconds to accept!"
			self.nochallenge = "Sorry {0}, but there are no challenges for you to confirm currently!"
			self.targetoffline = "Hey, that viewer isn't online right now, fighting them would be unfair!"
			self.needinfo = "You must choose a target when using the {0} command!"
			self.attackself = "Trying to fight yourself? That's a little angsty"
			self.respNotLive = "Sorry {0}, but the stream must be live in order to use that command."
			self.notenough = "{0} -> you don't have the {1} {2} required to use this command."
			self.outsiderange = "{0} -> you need to enter a number between {1} and {2} for the amount to fight for! Format: {3} (opponent name) (amount)"
			self.opponentnotenough = "{0} doesn't have enough {2}!"
			self.userwon = "{0}, you WON {2} {3}. {1}, you LOST {2} {3}"
			self.targetwon = "{0}, you LOST {2} {3}. {1}, you WON {2} {3}"
			self.identicalweapons = "Despite my best efforts, we only seem to have one weapon available!"
			self.notperm = "{0} -> you don't have permission to use this command. permission is: [{1} / {2}]"
		
		self.parent = parent

	# Reload settings on save through UI
	def Reload(self, data):
		"""Reload settings on save through UI"""
		parent = self.parent
		self.__dict__ = json.loads(data, encoding='utf-8-sig')
		self.parent = parent
	
	def Save(self, settingsfile):
		""" Save settings contained within the .json and .js settings files. """
		try:
			with codecs.open(settingsfile, encoding="utf-8-sig", mode="w+") as f:
				json.dump(self.__dict__, f, encoding="utf-8", ensure_ascii=False)
			with codecs.open(settingsfile.replace("json", "js"), encoding="utf-8-sig", mode="w+") as f:
				f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8', ensure_ascii=False)))
		except ValueError:
			MessageBox(0, u"Settings failed to save to file"
					   , u"Saving failed", 0)