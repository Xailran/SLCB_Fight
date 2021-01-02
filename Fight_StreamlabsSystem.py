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
import ctypes
import winsound

#---------------------------------------
# Script information
#---------------------------------------
ScriptName = "Fight"
Website = "https://www.twitch.tv/Xailran"
Creator = "Xailran"
Version = "1.0.0"
Description = "Let viewers fight each other with a variety of weapons"

#---------------------------------------
# Versions
#---------------------------------------
"""
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
		location = os.path.join(os.path.dirname(__file__), "Weapons.txt")
		with codecs.open(location, "w", "utf-8") as f:
			textline = "apple\r\naxe\r\nboomerang\r\nchainsaw\r\ngolf club\r\npistol\r\nspear\r\nspoon\r\ntaco\r\ntrain\r\n"
			f.write(textline)
		MessageBox(0, u"Weapons successfully restored to default values!"
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
	
def Execute(data):
	"""Required Execute data function"""
	if (not data.IsWhisper() and data.IsFromTwitch() and data.GetParam(0).lower() == MySet.command.lower()):
		if not HasPermission(data, MySet.FightPermission, MySet.FightPermissionInfo):
			return
		if (MySet.onlylive and not Parent.IsLive()):
			message = MySet.respNotLive.format(data.UserName)
			SendResp(data, message)
			return
		command = MySet.command.lower()
		if IsOnCooldown(data, command):
			Fight(data)
	
def Tick():
	"""Required tick function"""
	return
		
#---------------------------------------
# [Optional] Fight functions
#---------------------------------------
def Fight(data):
	"""Start of Fight function"""
	#Establishes opponent
	opponent = data.GetParam(1).replace("@", "")
	viewerlist = Parent.GetViewerList()
	if opponent == "":
		message = MySet.needinfo.format(data.UserName, MySet.command)
		SendResp(data, message)
		return
	if opponent.lower() == data.UserName.lower():
		message = MySet.attackself.format(data.UserName)
		SendResp(data, message)
		return
	check = False
	for x in viewerlist:
		if opponent.lower() == x.lower():
			opponent = x
			check = True
			break
	if not check:
		message = MySet.targetoffline.format(data.UserName, opponent)
		SendResp(data, message)
		return

	#Sets parameters
	Currency = Parent.GetCurrencyName()
	UPoints = Parent.GetPoints(data.UserName)
	TPoints = Parent.GetPoints(opponent)
	#Sets command cost
	if MySet.FightSetting == "Constant":
		FightPoints = MySet.FightCValue
	else:
		if MySet.FightMinValue < MySet.FightMaxValue:
			FightPoints = Parent.GetRandom(MySet.FightMinValue, MySet.FightMaxValue+1)
		else: 
			FightPoints = Parent.GetRandom(MySet.FightMaxValue, MySet.FightMinValue+1)
	#Checks that all parties have enough points
	if Parent.GetPoints(data.User) < FightPoints:
		message = MySet.notenough.format(data.UserName, str(FightPoints), Currency, str(UPoints))
		SendResp(data, message)
		return
	if TPoints < FightPoints:
		message = MySet.opponentnotenough.format(opponent, str(FightPoints), Currency, str(TPoints))
		SendResp(data, message)
		return
	opponentpoints = {opponent: FightPoints}
	#Loads weapons
	with codecs.open(Weapons, encoding="utf-8-sig", mode="r") as file:
		Item = [line.strip() for line in file]
		UWeapon = Item[Parent.GetRandom(0, len(Item))]
		OWeapon = Item[Parent.GetRandom(0, len(Item))]
		count = 0
		while UWeapon == OWeapon:
			OWeapon = Item[Parent.GetRandom(0, len(Item))]
			count = count + 1
			if count == 3:
				message = "Despite my best efforts, we only seem to have one weapon available!"
				SendResp(data, message)
				break
	#Loads fight message
	with codecs.open(FightDescriptions, encoding="utf-8-sig", mode="r") as file:
		Item = [line.strip() for line in file]
		VictoryMessage = Item[Parent.GetRandom(1, len(Item))]
	#Determines winner
	if MySet.FightAttWinChance >= Parent.GetRandom(0, 101):
		Parent.RemovePointsAll(opponentpoints)
		Parent.AddPoints(data.User,data.UserName,FightPoints)
		message = VictoryMessage.format(data.UserName, UWeapon, opponent, OWeapon)
		SendResp(data, message)
		message = "{0}, you WON {2} {3}. {1}, you LOST {2} {3}".format(data.UserName, opponent, FightPoints, Currency)
		SendResp(data, message)
	else:
		Parent.RemovePoints(data.User,data.UserName, FightPoints)
		Parent.AddPointsAll(opponentpoints)
		message = VictoryMessage.format(opponent, OWeapon, data.UserName, UWeapon)
		SendResp(data, message)
		message = "{0}, you LOST {2} {3}. {1}, you WON {2} {3}".format(data.UserName, opponent, FightPoints, Currency)
		SendResp(data, message)
	command = MySet.command.lower()
	Parent.AddCooldown(ScriptName,command,MySet.timerCooldown)
	Parent.AddUserCooldown(ScriptName,command,data.User,MySet.timerUserCooldown)

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
			self.FightSetting = "Random"
			self.FightCValue = 250
			self.FightMinValue = 100
			self.FightMaxValue = 500
			self.targetoffline = "Hey, that viewer isn't online right now, fighting them would be unfair!"
			self.needinfo = "You must choose a target when using the {0} command!"
			self.attackself = "Trying to fight yourself? That's a little angsty"
			self.respNotLive = "Sorry {0}, but the stream must be live in order to use that command."
			self.notenough = "{0} -> you don't have the {1} {2} required to use this command."
			self.opponentnotenough = "{0} doesn't have enough {2}!"
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