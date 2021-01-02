#####################
#   Fight Script    #
#####################

Description: Let viewers fight each other with a variety of weapons
Made By: Xailran
Website: https://www.twitch.tv/xailran
	 https://www.twitter.com/xailran

#####################
#     Versions      #
#####################

1.2.2 - Changed when cooldown starts
1.2.1 - Mixer-specific and general bug fixes
1.2.0 - Added $addweapon() parameter.
1.1.1 - Fixed script to properly work for Mixer and YT. Also fixed bug with using the "accept" settings
1.1.0 - Added UI options for viewers to select amount of points to fight for, and option for users to "accept" a fight before it actually happens. (Funded by twitch.tv/GodOfRanch)
1.0.0 - Initial Release

Known bugs:
None

#####################
#       Usage       #
#####################
Set weapons that can be used in the weapons.txt, and use the FightResponses.txt to add a variety of messages that can be used

!fight
	Like the default Duel minigame, but you choose what weapons viewers will randomly use!
	"!fight @target" or "!fight target". Enjoy the action!
	If users can choose how much to fight for (set in the UI), "!fight target value" will be the command to use

#####################
#    Parameters     #
#####################
$addweapon("weapon name", "success message", "Failure message") - Adds "weapon name" to the list of weapons that can be used in a fight
    Example: $addweapon($msg, "$username has added the weapon $msg", "The weapon $msg could not be added")

######################
#   Future Updates   #
######################
Add stats tracking for fights, and parameters for accessing those stats
Add leaderboard using above stats
Add UI option for how much to win

################################
#   Other Scripts by Xailran   #
################################
Please note that commissioned scripts come with idea and sale protection. These scripts are not included in the list below
Idea protection means that I will not share any ideas without permission from the client.
Sale protection means that I will not give away a script for free that someone else has paid for, without permission from the original client.
Commissioning the script only gives the client the rights to use the script, not to sell or otherwise distribute the script.
Existing clients are able to request early release versions of public scripts. If you would like to commission a script, send me a message on Discord!

Public Scripts:
Store (1.5.1) (2.0.0 coming out soon!)
Fight (1.2.2)
Xailran's Script Bundle (1.2.2)

Up to date as of 16/02/2019

#############################################
#   Donations are never expected, but any   #
#    support definitely helps, and keeps    #
#     me able to make more free scripts!    #
#       https://streamlabs.com/xailran      # 
#############################################
#############################################
# Tag me in the Streamlabs Chatbot discord  #
#    if you have any questions or ideas!    #
#   https://discordapp.com/invite/J4QMG5m   #
#############################################