
'''WELCOME TO THE RXBOT SETTINGS FILE
Each setting is split into a category.
Pretty much everything has a default value other than the >>BOT<< category, which needs to be changed before the bot can run.
'''

'''-------------------->>BOT<<--------------------'''
PORT = 80
# Use whatever port is open on your network. If 80 doesn't work, try 443

BOT_OAUTH = ""
# To get this Oauth, head to https://twitchapps.com/tmi/ and log in with YOUR BOT'S ACCOUNT!

BOT_NAME = ""
# The twitch username of your bot (Lowercase)

CHANNEL = ""
# The twitch username of the channel you are connecting to (Lowercase)

GPM_ENABLE = True
# Are you using Google Play Music? If this is set to false, all requests will only search youtube.
# If false, this will result in sporadic volumes, bad quality, and annoying intros/outros.
# This will throw a LOT OF ERRORS if you have GPM songs in your backup playlist and you set this to False.

'''-------------------->>SONGREQUEST<<--------------------'''

MAX_DUPLICATE_SONGS = 1
# This is the maximum amount of duplicate songs that can be in the queue. Leave 1 to only have one of each song in the queue at once.

MAX_REQUESTS_USER = 10
# This is the maximum amount of songs that a user may request. Ranks coming soon.

SHUFFLE_ON_START = True
# This will automatically shuffle the contents of the backup playlist whenever you start the bot if set to True. Depending on the playlists size this will delay the bot's startup a bit.

DELAY_BETWEEN_SONGS = 0.5
# The amount of time in seconds between one song ending and another starting.

VOL_INCREMENT = 5
# This is how much the volume will be changed by when you type !volumeup, !volumedown, or use a hotkey to adjust volume.

MAXTIME = 10
# The maximum song length in minutes. Songs longer than this duration won't be requested.

YT_IF_NO_RESULT = True
# If no results are found searching Google Play Music, the bot will plug the same query into youtube and play the top result from there.
# This has no effect if GPM_ENABLE is set to False.

DEFAULT_SR_MSG = "You need to type a song's name, or a link to a Youtube video or music file. You can type !wrongsong if the wrong one is selected."
# This is the message that will show up if someone types "!sr" or "!songrequest"


'''-------------------->>TITLE BLACKLIST FILTER<<--------------------'''
# This only applies to GPM and does nothing if GPM_ENABLE is set to False.

SONGBLSIZE = 5
# This is how many songs are loaded into the sorter and checked to see if they get affected by the blacklist.
# If you often get "Can't find this song," increase this by one or two. If you want GPM song requests to load faster, drop this to 3.
# 1 disables the blacklist entirely.

BLACKLISTED_SONG_TITLE_CONTENTS = [
    "live",
    "remix",
    "instrumental",
    "nightcore",
    "Edit",
    "Mix",
]
# One entry per line, followed by a comma. Songs not containing these keywords will be prioritized when requested.
# IMPORTANT! The phrases at the TOP of this list will be blacklisted first. Ex: "Song - Live" will be removed first, and "Song (Different Version)" might be played instead if there are no better options.


'''-------------------->>GENERAL<<--------------------'''

MODERATORS = [
    CHANNEL,

]
# These are people listed as moderators within the bot. It will automatically pull in moderators from chat as mods as well, but you can define mods here that have mod perms in the bot and not in chat.
# This is case sensitive. I recommend using yourself.


'''-------------------->>HOTKEYS<<--------------------'''
ENABLE_HOTKEYS = True # If this is set to true, you'll need to have something in all the hotkey options below.
HK_VOLUP = "F20"    # Volume Up
HK_VOLDN = "F14"    # Volume Down
HK_PAUSE = "F16"    # Toggle play/pause the music
HK_VETO = "F15"     # Veto the currently playing track
HK_CLRSONG = "F22"  # Remove the last song that anyone requested

# Hotkeys must be formatted in a specific way. Valid formats are listed below:
# Key scan codes (like 57 for Space) may be used, or a key's name may be used.
# VALID MODIFIERS: 'alt', 'alt gr', 'ctrl', 'left alt', 'left ctrl', 'left shift', 'left windows', 'right alt', 'right ctrl', 'right shift', 'right windows', 'shift', 'windows'

# "alt+q"
# "Space"
# "57"
# "ctrl+shift+f11"
