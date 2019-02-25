
'''WELCOME TO THE RXBOT SETTINGS FILE
Each setting is split into a category.
Pretty much everything has a default value other than the >>BOT<< category, which needs to be changed before the bot can run.
'''

'''-------------------->>BOT<<--------------------'''
HOST = "irc.twitch.tv"
#Don't change this unless you know what you're doing.

PORT = 80
#Use whatever port is open on your network. If this doesn't work, try 443

BOT_OAUTH = "oauth:5jz0y31vg95pq81eym5osr2gqcaswl"
#To get this Oauth, head to https://twitchapps.com/tmi/ and log in with YOUR BOT'S ACCOUNT!

BOT_NAME = "the_rxbot"
#The name of your bot (Lowercase)

CHANNEL = "rxbots"
#The name of the channel you are connecting to (Lowercase)

'''-------------------->>SONGREQUEST<<--------------------'''

MAX_DUPLICATE_SONGS = 1
#This is the maximum amount of duplicate songs that can be in the queue. Leave 1 to only have one of each song in the queue at once.

MAX_REQUESTS_USER = 50
#This is the maximum amount of songs that a user may request. Ranks coming soon.

SONGBLSIZE = 8
#This is how many songs are loaded into the sorter and checked to see if they get affected by the blacklist.
#If you often get "Can't find this song," increase this by one or two. If you want GPM song requests to load faster, drop this to 3.
# 1 disables the blacklist entirely.

SHUFFLE_ON_START = True
#This will automatically shuffle the contents of the backup playlist whenever you start the bot if set to True. Depending on the playlists size this will delay the bot's startup a bit.

DELAY_BETWEEN_SONGS = 0.5
#The amount of time in seconds between one song ending and another starting.

BLACKLISTED_SONG_TITLE_CONTENTS = [
    "live",
    "remix",
    "instrumental",
    "nightcore",
    "Ninja Sex Party",
    "Edit",
    "Version",
    "Mix",
    "(",
    "[",
]
#One entry per line, followed by a comma. Songs not containing these keywords will be prioritized when requested.
#IMPORTANT! The phrases at the TOP of this list will be blacklisted first. Ex: "Song - Live" will be removed first, and "Song (Different Version)" might be played instead if there are no better options.


'''-------------------->>GENERAL<<--------------------'''

MODERATORS = [
    "rxbots",

]
#These are people listed as moderators within the bot. It will automatically pull in moderators from chat as mods as well, but you can define mods here that have mod perms in the bot and not in chat.
#This is case sensitive. I recommend using yourself.