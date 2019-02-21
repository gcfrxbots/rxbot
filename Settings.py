HOST = "irc.twitch.tv"
#Don't change this unless you know what you're doing.

PORT = 80
#Use whatever port is open on your network. If this doesn't work, try 443

BOT_OAUTH = ""
#To get this Oauth, head to https://twitchapps.com/tmi/ and log in with YOUR BOT'S ACCOUNT!

BOT_NAME = ""
#The name of your bot (Lowercase)

CHANNEL = ""
#The name of the channel you are connecting to (Lowercase)

MAX_DUPLICATE_SONGS = 1
#This is the maximum amount of duplicate songs that can be in the queue. Leave 1 to only have one of each song in the queue at once.

MAX_REQUESTS_USER = 50
#This is the maximum amount of songs that a user may request. Ranks coming soon.

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

SONGBLSIZE = 8
#This is how many songs are loaded into the sorter and checked to see if they get affected by the blacklist.
#If you often get "Can't find this song," increase this by one or two. If you want GPM song requests to load faster, drop this to 3.
# 1 disables the blacklist entirely.

SHUFFLE_ON_START = True
#This will automatically shuffle the contents of the backup playlist whenever you start the bot if set to True. Depending on the playlists size this will delay the bot's startup a bit.

DELAY_BETWEEN_SONGS = 0.5
#The amount of time in seconds between one song ending and another starting.