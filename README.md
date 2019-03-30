
# **RXBot**

Hi, thank you for choosing RXBot! This documentation serves to help you understand what the bot is, what it can do, and how to use it, with the instructions being as simple and clear as possible.

RXBot is a song request bot for Twitch streamers: viewers can request songs in chat, and they will be added to a queue for the streamer to listen to while they stream. What makes RXBot unique is that it supports not only YouTube, but Google Play Music as well (yes, you must have a subscription). It's also very lightweight, so it will have virtually no impact on system performance.

⚠️ This project is still in early development, so despite pre-release testing, it may not function as expected. Please report bugs using Github's *Issues* tab, or in the [Rxbots Discord](https://discord.gg/8FRQBJy). ⚠️

*(Readme last updated for v2.1)*

-----

## Requirements

Once you download the bot, make sure you have all the requirements installed before running it:

• [**Python 2.7.9**](https://www.python.org/downloads/release/python-279/)

• [**VLC Media Player**](https://www.videolan.org/vlc/index.html) needs to be *installed*, but it does not need to actually be *running* for the bot to work.

• Finally, run **Install_Requirements.bat** in the bot's folder. If you wish, you can delete this file and **requirements.txt** afterwards, as they are no longer needed.

## First-Time Setup

*(Make sure you read this section and the* ***Settings*** *section before attempting to use your bot.)*

Before doing anything, you need to create a Twitch account for your bot to use. Don't use the account you'll actually be streaming from. It would probably be a good idea to make your bot a chat moderator. And if you use the BetterTTV extension, make sure to [add your new bot.](https://manage.betterttv.net/channel)

Run the bot by opening **Run.py** in the bot's folder. The first time you run it, the bot will tell you to go to [this page](https://accounts.google.com/o/oauth2/v2/auth?scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fskyjam&redirect_uri=urn%3Aietf%3Awg%3Aoauth%3A2.0%3Aoob&response_type=code&client_id=228293309116.apps.googleusercontent.com&access_type=offline) to generate an oauth link. Log in with your Google Play Account and follow all the prompts until it gives you a code. Copy that code, paste it in the bot window, and press Enter. If you entered it correctly, the bot will tell you that your backup playlist is empty. Close the bot so we can fix that.

If there are no song requests in the queue, the bot will play songs from your backup playlist. Since this is your first time using the bot, your backup playlist is empty. Run **PlaylistEditor.py**, and it will present you with three options: `1. Fill Playlist || 2. Shuffle Playlist || 3. Clear Playlist` To add songs, type 1 and hit enter. The bot will then detect all playlists on your Google Play Music account (only playlists you've created, not ones you follow). Type the number of the playlist you wish to import and hit enter. Once the bot is finished importing (it should take less than a second), it will close itself, but you can re-open it and add import more playlists if you wish. Note that song files you've *uploaded* to your GPM account will not work, but you can add those songs to the bot via Youtube or uploaded files (more on that later). For now, it's time to adjust your settings.

## Settings

The **Settings.py** file is where you can adjust your personal settings for the bot. Make sure you read this section completely, as you *need* to change some of these for the bot to work in your channel. To edit this file, us a program such as IDLE or Notepad++.

##### BOT

`PORT = 80` || The bot connects to Twitch through this port. 80 will already be open on most networks, so that is the default setting. If 80 doesn't work, try 443.

`BOT_OAUTH = ""` || This is your bot's Twitch OAuth token. To put it simply, it's a password that only *this bot* can use to sign into your bot's Twitch account. [Click here to generate your oauth token](https://twitchapps.com/tmi/) (make sure you sign in with ***your bot's account,*** not your own). Once it's generated, copy it and paste it between the quotes.

`BOT_NAME = ""` || Your bot's Twitch username. Put it between the quotes, in all lowercase.

`CHANNEL = ""` || Your Twitch username. Put it between the quotes, in all lowercase.

##### SONGREQUEST

`MAX_DUPLICATE_SONGS = 1` || The same song cannot be in the queue more than this many times. Most sane users will want to keep this set to 1.

`MAX_REQUESTS_USER = 5` || This is the maximum number of songs a single user can have in the queue at a time.

`SHUFFLE_ON_START = True`| If set to true, the bot will automatically shuffle your backup playlist every time you open it. If set to false, your songs will play in the same order every time.

`DELAY_BETWEEN_SONGS = 0.5` || This is the number of seconds between the current song ending, and the next song beginning. 0.5 should be fine for most users.

`VOL_INCREMENT = 5` || Adjusts how much the volume will change when using a volume hotkey, or `!volumeup`/`volumedown`. For example: if you have this set to 5, and your volume is at 50, hitting your volume up hotkey will change the volume to 55.

`MAXTIME = 10` || This is the maximum song length, in minutes. If a user tries to request a song that exceeds this length, it will be rejected, and not added to the queue.

`DEFAULT_SR_MSG = ""` || The message that will show up if a user types `!sr` or `!songrequest` by itself. Put your message between the quotes.
##### TITLE BLACKLIST FILTER

`SONGBLSIZE = 8` || When a user requests a song (aside from Youtube links, obviously), the song they typed is searched on Google Play Music, and the bot picks the top result. However, the top result is sometimes a cover, remix, live performance, etc. which the user will probably not want. If this setting is above 1, the bot will take that many results, and sort through them using your blacklisted terms. So for example, if you have the word "remix" set as a blacklisted term, the bot will prioritize search results *without* the word "remix" in them. The higher this number is set, the more accurate your search results will be, but the slower the bot will respond to them. We recommend a setting between 3 and 8.

`BLACKLISTED_SONG_TITLE_CONTENTS` || These are terms blacklisted from GPM search results. There are a few terms already blacklisted by default, but you can remove them if you wish, and of course add new ones. Each blacklisted term should be on its own line— just make sure the formatting matches that of the terms that are there by default.  
Note that the terms are in order from most-hated to least-hated. For example: If "remix" is at the top of the list, and "live" is at the bottom, the bot would prioritize adding a song with "live" in the title over one with  "remix".

##### GENERAL

`MODERATORS` || A list of users that have moderator permissions inside the bot, letting them use bot-only commands. Chat moderators will be added to this list automatically once the bot detects them in the viewer list (this can take a few minutes), but you can also manually add users if you want them to have moderator permissions in the bot, but not in your chat. Each user should be on its own line.

##### HOTKEYS

`ENABLE_HOTKEYS = True` || Enable or disable hotkeys for pausing, adjusting the volume, skipping songs, or removing the last song added to the queue. 

`HK_VOLUP` || Turns the volume up.

`HK_VOLDN` || Turns the volume down.

`HK_PAUSE` || Pause/play the music.

`HK_VETO` || Skips the current song.

`HK_CLRSONG` || Removes the last song added to the queue.

More info on these hotkeys later, because honestly we have no fucking idea right now.

## Commands

This is a list of commands for the bot, which users will type into Twitch chat:

##### SONGREQUEST

`!sr` or `!songrequest` || This is the command users will type to request songs. They type the command, then the song they want to request.  
**Google Play Music:** Following the command with a search term will add the song from Google Play Music. For example:`!sr Ginuwine Pony` will search "Ginuwine Pony" on Google Play Music, and add the best result. Users can also add their own blacklisted terms to their search by putting a hyphen before the word they wish to exclude. For example: `!sr Ginuwine Pony -remix` will look up "Ginuwine Pony" on Google Play Music, but will exclude all search results containing the word "Remix" in the title.   
**Youtube:** Instead of looking up a song, users can instead paste a Youtube link. For example: `!sr https://www.youtube.com/watch?v=lbnoG2dsUk0`  
**Uploaded Music File:** If you upload a music file (.mp3, .wav, etc.) to the internet and can get a direct streaming link to it, you can request that as well. For example: You can upload your song file to a website like [Instaudio](https://instaud.io/), then request the song with the direct streaming link, like so: `!sr https://instaud.io/_/3nOe.mp3`  

Note that every song in the queue has an ID, which can be used in other commands. This ID is *not* based on the song's current position in the queue, and does not change. The ID is shown when the song is requested.

`!nowplaying` || Displays the currently-playing song in chat. Note: the current song is saved to the **nowplaying.txt** file in the bot folder, so you can add this as a text source in OBS (or your streaming program of choice) to display the current song on screen.  
There is also a file called **SongQueue.csv**, which contains the whole queue in a readable format. We recommend using something like [Google Drive]([https://www.google.com/drive/download/backup-and-sync/](https://www.google.com/drive/download/backup-and-sync/)) to upload the file every time it updates. Your viewers can then visit this link at any time to see all upcoming songs and their IDs.

`!timeleft` || Displays how much time is left on the current song. Putting a song ID after the command will display the combined length of all songs leading up to that one, i.e. how long until that song begins playing (assuming no pausing or skipping, of course).

`!wrongsong` || If a user requests a song, but the search does not yield the correct song, the user can type this command to remove the last song they requested from the queue. They can also add a song ID after the command, if they wish to remove one of their requests that isn't the most recent one. For example, `!wrongsong 7` will remove song 7 from the queue, assuming the same user requested it.

`!clearsong` **(Mod Only)** || Removes the last song added to the queue, regardless of who requested it. Can also add a song ID after the command, if they wish to remove a song besides the most recent one. For example: `!clearsong 7` will remove song 7 from the queue.

`!plsr` **(Mod Only)** || Functions like `!sr`, but adds the song to the backup playlist rather than the song request queue.

`!plclearsong` **(Mod Only)** || Functions like `!clearsong`, but removes the most recent song added via `!plsr`.

`!volume` **(Mod Only)** || Doing the command by itself will display the current music volume in chat. Adding a number after the command will set the volume to that number. For example: `!volume 75` will set the volume to 75 (out of 100).

`!volumeup`/`!volumedown` **(Mod Only))** || Turn the music volume up or down. Doing the command by itself will adjust the volume based on your `VOL_INCREMENT` setting, but adding a number after the command will adjust the volume by that increment. For example: if your volume is at 50, `!volumeup 20` will change the volume to 70.

`!veto` **(Mod Only)** || Skip the current song.

`!clearqueue` **(Mod Only)** || Removes all songs from the queue (this will not skip the current song).

`!clearplaylist` **(Mod Only)** || Removes all songs from the backup playlist.

## FAQ/Troubleshooting

**Q:** My bot crashes on startup!  
**A:** Your dependencies aren't working. Open command prompt as administrator, and manually type in each line from **requirements.txt**. If it says pip is not recognized as a command, reinstall Python 2.7.9. If it says something else, report it to us as a bug.

**Q:** Hotkeys don't work while I'm in certain programs!  
**A:** Run the bot as administrator.

**Q:** Is this bot purely for song requests?  
**A:** At the moment, yes. We do plan to add normal commands later on though, so stay tuned!

## Credits and Stuff
[**Rxbots**](https://www.twitch.tv/rxbots) - Sole creator of the bot.

[**iCeCoCaCoLa64**](https://www.twitch.tv/icecocacola64) - Ideas, motivation, testing, and documentation (hi there 👋🏻).

[**Grrenix**](https://www.twitch.tv/Grrenix) - Coding help and motivation.

[**kc0zhq**](https://www.twitch.tv/kc0zhq) - Coding help and motivation.

**StreamLabs Chatbot** - For becoming such ungodly amounts of terrible that you inspired a random college student to become a coding God.

If you wish to donate to this project, go to [the Rxbots Twitch channel](https://www.twitch.tv/rxbots) and click the "Donations" panel below the stream. It's absolutely not necessary, but know that we really appreciate it!
