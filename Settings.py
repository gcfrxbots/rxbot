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

MAX_REQUESTS_USER = 5
#This is the maximum amount of songs that a user may request. Ranks coming soon.

BLACKLISTED_SONG_TITLE_CONTENTS = [
    "live",
    "remix",
    "instrumental",
    "nightcore",
    "Ninja Sex Party",
    "Radio",
    "Version",
    "(",
    ")",
]
#One entry per line, followed by a comma. The top words are a higher priority to remove, so a song including "version" will be played over a song including "live". More documentation coming soon.