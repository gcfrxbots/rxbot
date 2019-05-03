import time
import datetime
from Initialize import joinRoom, socket, getmoderators
from SongRequest import *
import string
import threading
from threading import Thread
import keyboard
import sys
import re
from random import shuffle
import sqlite3
reload(sys)
sys.setdefaultencoding('utf-8')





def togglepause():
    if paused == True:
        play(None, None)
    elif paused == False:
        pause(None, None)
#These functions require two variables to call to avoid having way more code in the top loop.
def play(x, y):
    global nowplaying, paused
    srcontrol.play()
    nowplaying = True
    paused = False

def pause(x, y):
    global nowplaying, paused
    srcontrol.pause()
    nowplaying = False
    paused = True

def veto(x, y):
    global nowplaying, paused
    srcontrol.songover()
    paused = False
    nowplaying = False


sr = SRcommands()
srcontrol = SRcontrol()
'''INITALIZE EVERYTHING
All this stuff up here runs when the script first runs and is the init code.'''


nowplaying = False
paused = False

if SHUFFLE_ON_START == True: #Playlist Shuffler
    db = sqlite3.connect('songqueue.db')
    cursor = db.cursor()
    cursor.execute('''SELECT * FROM playlist ORDER BY RANDOM()''')
    listSongs = cursor.fetchall()
    shuffle(listSongs)
    sqlcommand = '''DELETE FROM playlist'''
    cursor.execute(sqlcommand)
    for item in listSongs:
        cursor.execute('''INSERT INTO playlist(song, key) VALUES("{song_name}", "{key}");'''.format(song_name=item[1], key=item[2]))
    db.commit()
    db.close()
    print(">> Backup Playlist has been shuffled.")
if ENABLE_HOTKEYS:
    keyboard.add_hotkey(HK_VOLUP, srcontrol.volumeup, args=(None, None))
    keyboard.unhook_all_hotkeys() #Currently the best way to allow the hotkeys access to the p. class is to redefine them every time a new song is played.
    keyboard.add_hotkey(HK_VOLUP, srcontrol.volumeup, args=(None, None))
    keyboard.add_hotkey(HK_VOLDN, srcontrol.volumedown, args=(None, None))
    keyboard.add_hotkey(HK_PAUSE, togglepause)
    keyboard.add_hotkey(HK_VETO, veto, args=(None, None))
    keyboard.add_hotkey(HK_CLRSONG, sendMessage, args=(s, sr.clearsong(None, "STREAMER")))

'''END INIT'''



def getUser(line):
    seperate = line.split(":", 2)
    user = seperate[1].split("!", 1)[0]
    return user


def getMessage(line):
    seperate = line.split(":", 2)
    message = seperate[2]
    return message

def formatted_time():
    return datetime.datetime.today().now().strftime("%I:%M")
    # Thanks to Zerg3rr for this code and some other help

def getint(cmdarguments):
    try:
        out = int(re.search(r'\d+', cmdarguments).group())
        return out
    except: return None


def PONG():
    s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
    threading.Timer(200, PONG).start()
PONG()


def runcommand(command, cmdarguments, user):
    torun = None
    commands = {
        # Public SR Commands
        "!sr": (sr.songrequest, cmdarguments, user),
        "!songrequest": (sr.songrequest, cmdarguments, user),  # Alias
        "!wrongsong": (sr.wrongsong, getint(cmdarguments), user),
        "!nowplaying": (sr.getnowplaying, None, user),
        "!timeleft": (sr.queuetime, getint(cmdarguments), user),
        "!queue": (sr.queuelink, user, None),
        "!songlist": (sr.queuelink, user, None), #Alias

        # NowPlaying Control
        "!play": ("MOD", play, None, None),
        "!pause": ("MOD", pause, None, None),
        "!veto": ("MOD", veto, None, None),


        # Volume Control
        "!volume": ("MOD", srcontrol.volume, getint(cmdarguments), user),
        "!v": ("MOD", srcontrol.volume, getint(cmdarguments), user), # Alias
        "!volumeup": ("MOD", srcontrol.volumeup, getint(cmdarguments), user),
        "!vu": ("MOD", srcontrol.volumeup, getint(cmdarguments), user), # Alias
        "!volumedown": ("MOD", srcontrol.volumedown, getint(cmdarguments), user),
        "!vd": ("MOD", srcontrol.volumedown, getint(cmdarguments), user), # Alias

        # Playlist Control
        "!clearsong": ("MOD", sr.clearsong, getint(cmdarguments), user),
        "!plsr": ("MOD", sr.plsongrequest, cmdarguments, user),
        "!plclearsong": ("MOD", sr.plclearsong, cmdarguments, user),
        "!clearqueue": ("MOD", sr.clearqueue, None, None),
    }

    for item in commands:
        if item == command:
            if commands[item][0] == "MOD": #MOD ONLY COMMANDS:
                if user in getmoderators():
                    torun = commands[item][1](commands[item][2], commands[item][3])
                else:
                    sendMessage(s, "You don't have permission to do this.")
            else:
                torun = commands[item][0](commands[item][1], commands[item][2])
            break
    if not torun:
        return
    output = torun
    #Modifiers to do something other than send a message
    if output == None:
        pass

    else:
        sendMessage(s, output)



def main():
    global nowplaying, paused
    s = openSocket()
    joinRoom(s)
    readbuffer = ""
    while True:
        try:
            recvData = s.recv(1024)
            if recvData.len() == 0:
                reconnect() # Detect if the data being sent is nonexistent, reconnect
            readbuffer = readbuffer + recvData
            temp = string.split(readbuffer, "\n")
            readbuffer = temp.pop()
            for line in temp:
                if "PING" in line:
                    s.send(("PONG :tmi.twitch.tv\r\n".encode("utf-8")))
                else:
                    # All these things break apart the given chat message to make things easier to work with.
                    user = getUser(line)
                    message = str(getMessage(line))
                    command = ((message.split(' ', 1)[0]).lower()).replace("\r", "")
                    cmdarguments = message.replace(command or "\r" or "\n", "")
                    getint(cmdarguments)
                    print("(" + formatted_time() + ")>> " + user + ": " + message)
                    # Run the commands function
                    runcommand(command, cmdarguments, user)
        except socket.error:
            print("Socket died")
            reconnect()



# If the queue is completely empty at start, add a song so it's not pulling nonexistent values in the loop below
if not sqliteread('''SELECT id, name, song, key FROM songs ORDER BY id ASC'''):
    playfromplaylist() # Move a song from the playlist into the queue.
def tick():
    timecache = 0
    global nowplaying, paused
    while True:
        time.sleep(0.3)
        # Check if there's nothing in the playlist.
        if not sqliteread('''SELECT id, name, song, key FROM songs ORDER BY id ASC'''):
            playfromplaylist() # Move a song from the playlist into the queue.

        if paused or not nowplaying:  # If for any reason the music isnt playing, change the nowplaying to nothing
            writenowplaying(False, "")

        if nowplaying and not paused:  # If music IS playing:
            time.sleep(0.3)
            nptime = srcontrol.gettime()  # Save the current now playing time

            if timecache == nptime:  # If the cache (written 0.3 seconds before) and the time are equal, songs over
                time.sleep(0.5)
                nowplaying = srcontrol.songover()
            timecache = nptime

        elif not paused and not nowplaying: # When a song is over, start a new song
            nowplaying = srcontrol.playsong()

            timecache = 1
            time.sleep(1)






t1 = Thread(target = main)
t2 = Thread(target = tick)


t1.start()
t2.start()