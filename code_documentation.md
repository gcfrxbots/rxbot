## RXBot Code Documentation
Hey there, thanks for taking interest in the actual coding aspect of the bot. This is a document that I'll be updating occasionally to help users understand the code and how to change things to make this bot your own.

This file will be split by each file that the bot uses, and it'll be in order top - bottom so it's easy to find what is being described.

## Initialize.py
I'll cover this first since it introduces some important functions used in the rest of the code.

`openSocket()`, `joinRoom()`, and `loadingComplete()` shouldn't be touched - these are all for setting up the bot and getting it connected to twitch's servers. 

`sendMessage()` is the function used for nearly everything to send a message to the twitch chat. 

`sqliteread()` and `sqlitewrite()` are both used for executing Sqlite3 commands. The read does not commit any changes to the databases, so this should only be used when reading data from a database. The write does commit data, but this can cause issues if data is committed but nothing is changed, so this should only be used for making changes to the database.
These two are used almost everywhere for interacting with the database.

`createqueuecsv()` is run every time there's a change in the song request queue, this copies the contents of the 'songs' table into SongQueue.csv. 

`getmoderators()` grabs a list of all users in your twitch chat, then sorts them by moderators. If you wanted to add something to find normal users or whatever you could do that using this same code.


## Run.py

At the top underneath all of the imports you'll find the INIT section. None of this stuff should be changed as it can break a lot of stuff.

The only exception here is hotkeys, which are at the bottom of the INIT section just above the `END INIT` marker. The hotkeys SHOULD be defining one hotkey (HK_VOLUP) then unhooking them all, this is to ensure that there's at least one hotkey hooked and it doesn't throw an error whenever it's started. You can add a hotkey by copying the format down. The format is:
 `keyboard.add_hotkey([Key], [Function, no args], args=([Function's args]))` 
 so that if you wanted to run volumeup which requires two arguments, you'd need `keyboard.add_hotkey(HK_VOLUP, srcontrol.volumeup, args=(None, None))`
 
 Under `END INIT` you'll find a few functions that make life easier, these will be expanded later. 
 Notably there's getUser which grabs the user from a message twitch sends, 
 getMessage which trims everything but the message sent, 
 and getInt which will attempt to see if the user's message after their command is just an int, and if so it returns it.

Don't mess with PONG, it can cause issues with the bot's connection to twitch.

**The runcommand() function is where you'll be able to make most changes you need.**
In here you'll see a layout of each command in a dictionary format. It's sorted by Public SR Commands, NowPlaying Control, Volume Control, and Playlist Control. Non-Mods only have access to the top category.

Each entry is formatted like this:
`"!command": ("MOD", function, argument, user)`
If the command is mod only, add "MOD" as the first entry. Otherwise it starts with the function.
You can easily create or modify aliases for commands by copying the entry for a command and changing the command. For example:
`"!sr": (sr.songrequest, cmdarguments, user),` has an alias
`"!songrequest": (sr.songrequest, cmdarguments, user), # Alias` and they do the exact same thing.

Also notable in this function is that everything run through it needs to either return `None` or a message to be sent. If the function returns `None` nothing will be sent other than the function running, otherwise anything returned will be sent as a message to the twitch chat. 

My standard formatting for messages is `user + " >> " + message` which nearly every command function returns.

There isn't much more worth modifying in Run.py, but I'll explain further down anyway.

main() is a loop that cycles whenever there's any new message from twitch. It already checks for commands and runs the command from the dict above if there is one, but if there's anything else you want to do to test for something whenever a message is sent, this is where you'd put it.

tick() is a loop that cycles once every 0.3 seconds (to not nuke your CPU). This constantly checks for the state of the song to see if it's playing, if it's been set to paused, if it's been veto'ed, or if it's over. 
The music is paused by setting paused = True and nowplaying = False.
The music is played by setting paused = False and nowplaying = True.
The song is veto'ed by setting paused = False and nowplaying = False.

While VLC has a way of detecting if a song is over, that's less reliable than the solution I came up with here. Every 0.3 second cycle the script stores an int `timecache` as the current time in ms for the song, and after 0.3 seconds checks to see if timecache == the current time. If it is, the song is no longer playing. Of course this check only happens if the music isn't paused.

At the very bottom is the threading to run both loops at the same time. Don't delete.


## SongRequest.py
This file is all the commands and operations that go with playing and requesting songs.

Everything at the top is initializing gmusicapi. Don't recommend touching.

`writenowplaying()` writes whatever the current song title is to the nowplaying.txt

`getytkey()` trims apart a youtube URL to just get the key of the video.

`songtitlefilter()` is a bit complicated. The idea is to blacklist certain terms so that if the search for some reason returns a live version of a song, that's weeded out. 
The `BLACKLISTED_SONG_TITLE_CONTENTS` list in settings is all of the terms for this. It first checks if the request explicitly requested something with one of the terms, and if so it'll remove it from the list for that request (like if they request Despacito Live, it'll let songs with "live" in the title through the filter).
Instead of loading the top song result, it loads multiple (`SONGBLSIZE`) into a list.

For every item in the blacklisted list, starting at the top, it checks to see if a blacklisted term is in any of the song titles. If it is, it removes that song from the list, and it continues doing that until there's one song left. This means that the *top* of the blacklist list are phrases that will be filtered out first. If I request "Despacito" and the only options are "Despacito Live" and "Despacito Remix" and 'live' was above 'remix' in the blacklist, then the Remix song would play.
When a song is requested and it displays a bunch of songs and says >>>REMOVED (song), that's this filter.

`removetopqueue()` just removes the top song from the queue so that it can keep moving. Pretty simple.

`getnewentry()` grabs the ID from a new request so that the user can know what their request's ID is in the queue.

`sr_geturl()` gets the actual streaming URL for a google play music song.

`playfromplaylist()` takes the top song from the 'playlist' table in the database and moves it over to the top of 'songs', and also puts that song at the bottom of the playlist so that it's not lost. This should only be done when there are no other songs in the queue.

`class SRcontrol` is full of song request functions related to controlling the play of audio.

`playsong()` grabs the top song from the queue, figures out what type of request it is, then plays it.

`songover()` stops the playing song, that's about it.

`gettime()` just gets the current elapsed time in the playing song.

`volume()` returns the current volume with no command, or lets you adjust the volume. 

`volumeup()` and `volumedown()` both get the current volume, then add or subtract it by the argument in the command and set the volume to that.

`play()` and `pause()` do exactly what you think they would. They're called to actually change the music after the variables have been changed in Run.py.

`class SRcommands` is all of the actual functions that are run after a command executes them. None of these interact directly with what's playing, but instead interact with the queue.

`songrequest()` is the heart and soul of songrequest (obviously). It goes through a ton of checks to see if the user has too many songs in the queue, if the song is already in the queue, or if the song is long enough. It also uses the Validators library to see if the request is a URL, then checks if it's a youtube request or not. If it's none of them, it goes to google play music. Each request calls `getsongtime()` to get the actual time of the track and store it.

If no results are found for a search request (GPM) then it'll automatically go to `youtubesr()`

`youtubesr()` searches youtube for whatever the search query is. If GPM is disabled this is the primary song request function. If the user requests an ID specifically, the search usually works for it but sometimes it doesnt. If this happens it'll check if it makes a valid youtube URL and if it does it plugs it back into the inital songrequest.

`wrongsong()` uses a bunch of sqlite checks to find the most recent song from a specific user and remove it from the queue. Also works if you specify an id.

`clearsong()` does literally the exact same thing but doesn't check for the user.

`queuetime()` adds the entire 'time' column in the 'songs' table, then translates that into hours/min/sec and sends that to chat.  Also works if you specify an id, in which case it stops at that id rather than at the end.

`plsongrequest()` and `plclearsong()` are nearly identical to their non pl-prefixed functions, only they put their requests into the 'playlist' table (backup playlist) rather than the queue.

 `getnowplaying()` literally just reads nowplaying.txt into the chat.

`clearqueue()` just deletes everything in the queue.

`queuelink()` prints the queue link from settings.

Finally there's `getsongtime()`, the actual bane of my entire existence. This single function took nearly as long to perfect as all of searching GPM and playing it in order.

It first goes through the checks for URLs and whatnot just like songrequest does. What it has to do is load the track as a new mediaplayer but NOT play it, instead it begins parsing it as quickly as possible. To avoid having to load up an eventhandler every single time I started a new track, a loop constantly checks the state of the parsed status until it's done, in which case it finally returns the time. 
getsometime does make requests take a bit longer, mostly because youtube requests take a moment to get the streaming URL and it has to get it to load the whole track into the parser.
The `if cycle > 999999:` is basically just there so if the parser takes more than 5ish seconds something is incredibly broken, so it stops it rather than nuking your CPU. Parsing shouldn't take more than about 0.2 seconds.

It's worth pointing out that this isnt 100% accurate because a lot of songs have an offset - a song with a duration of 40000 might actually be 38375ms long. Because of this I just subtract 2 seconds from every time because that seems fairly consistent, songs usually have between 1 and 3 second delays. Not a huge deal either way.

That's it for now! Thanks for reading and hopefully this helped make things make sense.

