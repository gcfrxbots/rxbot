from Socket import *
from Initialize import joinRoom, initsqlite
from SongRequest import *
import string
import vlc
from threading import Thread
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


global nowplaying, paused
nowplaying = False
paused = False



def getUser(line):
    seperate = line.split(":", 2)
    user = seperate[1].split("!", 1)[0]
    return user



def getMessage(line):
    seperate = line.split(":", 2)
    message = seperate[2]
    return message





def getint(cmdarguments):
    import re
    try:
        out = int(re.search(r'\d+', cmdarguments).group())
        print(str(out))
        return out
    except:
        return None

def PONG():
    import threading
    s.send(bytes('PONG :tmi.twitch.tv\r\n'))
    print("PONG SENT!")
    threading.Timer(240, PONG).start()
PONG()

p = vlc.MediaPlayer()
initsqlite()


def main():
    global nowplaying, paused
    s = openSocket()
    joinRoom(s)
    readbuffer = ""


    while True:
        try:
            readbuffer = readbuffer + s.recv(1024)
            temp = string.split(readbuffer, "\n")
            readbuffer = temp.pop()




            for line in temp:

                if "PING" in line: #PING detection from twitch. Immediately sends a PONG back with the same content as the line. The PONG() Function is backup.
                    s.send("PONG %s\r\n" % line[1])
                    print("Got a PING from twitch's servers.")

                else:
                    global user #All these things break apart the given chat message to make things easier to work with.
                    user = getUser(line)
                    message = str(getMessage(line))
                    command = ((message.split(' ', 1)[0]).lower()).replace("\r", "")
                    cmdarguments = message.replace(command or "\r" or "\n", "")
                    getint(cmdarguments)

                    print(">> " + user + ": " + message)

                    if ("!sr" == command):
                        sr_getsong(cmdarguments, user)



                    if ("!pause" in command):
                        p.set_pause(True)
                        nowplaying = False
                        paused = True

                    if ("!play" == command):
                        p.set_pause(False)
                        nowplaying = True
                        paused = False

                    if ("!clearqueue" == command):
                        sendMessage(s, "Cleared the song request queue.")
                        dosqlite('''DELETE FROM songs''')

                    if ("!veto" in command):
                        sendMessage(s, "Song Vetoed.")
                        p.stop()
                        paused = False
                        nowplaying = False

                    if ("!wrongsong" == command):
                        wrongsong(getint(cmdarguments), user)


                    if ("!clearsong" == command):
                        clearsong(getint(cmdarguments), user)

                    if ("!time" == command):
                        time = p.get_time()
                        sendMessage(s, str(time))


                    if ("!volume" == command):
                        vol = getint(cmdarguments)
                        if vol == None:
                            sendMessage(s, "Current volume: " + str(p.audio_get_volume()))
                            break
                        if vol > 100 or vol < 0:
                            sendMessage(s, "Invalid volume level. Must be between 0-100.")
                            break
                        p.audio_set_volume(vol)
                        sendMessage(s, "Music volume set to: " + str(vol))

                    if ("!volumeup" == command):
                        vol = getint(cmdarguments)
                        if vol == None:
                            vol = 5
                        if (p.audio_get_volume() + vol) > 100:
                            sendMessage(s, "Raised the volume to: 100")
                            p.audio_set_volume(100)
                            break
                        sendMessage(s,  "Raised the volume to: " + str(p.audio_get_volume() + vol))
                        p.audio_set_volume((p.audio_get_volume() + vol))

                    if ("!volumedown" == command):
                        vol = getint(cmdarguments)
                        if vol == None:
                            vol = 5
                        if (p.audio_get_volume() - vol) < 0:
                            sendMessage(s, "Lowered the volume to: 0")
                            p.audio_set_volume(0)
                            break
                        sendMessage(s,  "Lowered the volume to: " + str(p.audio_get_volume() - vol))
                        p.audio_set_volume((p.audio_get_volume() - vol))
                    if ("!nowplaying" == command):
                        with open("nowplaying.txt", "r") as f:
                            returnnp = f.readlines()
                            if not returnnp:
                                sendMessage(s, (user + " >> The music is currently paused."))
                            else:
                                sendMessage(s, (user + " >> " + returnnp[0]))









        except socket.error:
            print("Socket died")



def tick():
    import time
    global nowplaying, paused
    songtitle = ""
    while True:
        time.sleep(0.3) #Slow down the stupidly fast loop for the sake of CPU


        if (paused == True or nowplaying == False):
            writenowplaying(False, "")

        if (nowplaying == True and paused == False):#Detect when a song is over
            writenowplaying(True, songtitle)
            time.sleep(1.1)
            nptime = int(p.get_time())
            nplength = int(p.get_length())

            if (nptime + 1500) > nplength: #Do this stuff when a song is over
                time.sleep(0.8)
                print("Song is over!")
                p.stop()
                global nowplaying
                nowplaying = False




        elif paused == False: # When a song is over, start a new song

            try:
                import sqlite3 #Open the db, get the song out
                from sqlite3 import Error
                db = sqlite3.connect('songqueue.db')
                cursor = db.cursor()
                cursor.execute('''SELECT id, name, song, key FROM songs ORDER BY id ASC''') #Pick the top song
                row = cursor.fetchone()
                if row == None: #>>>>>> DO THIS STUFF IF THE LIST IS EMPTY!
                    sendMessage(s, "Queue is empty! Request some more music with !sr")
                    paused = True
                    queueempty = True

                songtitle = row[2]
                songkey = row[3]


                #Delete the top result
                cursor.execute('SELECT id FROM songs ORDER BY id ASC LIMIT 1')
                row = cursor.fetchone()
                cursor.execute(('''DELETE FROM songs WHERE id={0}''').format(int(row[0]))) #Delete the top song
                db.commit()
            except Error as e:
                raise e
                print e
            except:
                pass
            finally:
                db.close


                try:
                    if validators.url(songtitle) == True: #TEST IF THE REQUEST IS A LINK
                        if "youtu" in songtitle: #IS IT A YOUTUBE LINK?
                            playurl = YouTube(songtitle).streams.filter(only_audio=True).order_by('abr').first().url #If it is, get the link with the best sound quality thats only audio
                            songtitle = YouTube(songtitle).title
                            writenowplaying(True, songtitle)
                        else:
                            playurl = songtitle
                            songtitle = "Online Music File"
                            writenowplaying(True, songtitle)
                    else:
                        playurl = sr_geturl(songkey)
                        writenowplaying(True, songtitle)

                    global p
                    p = vlc.MediaPlayer(playurl)
                    p.play()
                    nowplaying = True
                    queueempty = False

                except Exception as e:
                    print e









t1 = Thread(target = main)
t2 = Thread(target = tick)


t1.start()
t2.start()