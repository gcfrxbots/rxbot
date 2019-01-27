from Socket import *
from Initialize import joinRoom
from SongRequest import *
import string
import vlc
from threading import Thread
import csv

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

def send_pong(msg):
    s.send(bytes('PONG %s\r\n' % msg, 'UTF-8'))

def copyqueuecache():
    with open('queuecache.csv', 'r') as f2:
        with open('queue.csv', 'w') as f3:
            for line in f2:
                f3.write(line)

p = vlc.MediaPlayer()



def main():
    import time
    s = openSocket()
    joinRoom(s)
    readbuffer = ""

    while True:
            try:
                readbuffer = readbuffer + s.recv(1024)
                temp = string.split(readbuffer, "\n")
                readbuffer = temp.pop()




                for line in temp:

                    if "PING" in line:
                        s.send("PONG %s\r\n" % line[1])
                        print("Send a PONG to Twitch's servers")
                    else:
                        global user
                        user = getUser(line)
                        message = str(getMessage(line))
                        command = (message.split(' ', 1)[0]).lower()
                        cmdarguments = message.replace(command or "/r" or "/n", "")

                        print(">> " + user + ": " + message)

                        if ("!sr" in command):
                            global nowplaying, paused
                            sr_getsong(cmdarguments, user)
                            paused = False



                        if ("!pause" in command):
                            p.set_pause(True)
                            nowplaying = False
                            paused = True
                        if ("!play" in command):
                            p.set_pause(False)
                            nowplaying = True
                            paused = False
                        if ("!clearqueue" in command):
                            sendMessage(s, "Cleared the song request queue.")
                            f = open('queue.csv', 'w')
                            f.truncate()
                            f.close()

                        if ("!time" in command):
                            time = p.get_time()
                            sendMessage(s, str(time))


                        if ("!veto" in command):
                            p.stop()
                            paused = False
                            nowplaying = False

                        if ("!wrongsong" in command):
                            print("Worked")
                            if cmdarguments != '':
                                print("Penis")

                            import csv
                            with open('queue.csv', 'rb') as inp, open('queuecache.csv', 'wb') as out:
                                writer = csv.writer(out)
                                for index, row in enumerate(csv.reader(inp)):
                                    pass





                        if ("!volume" in command):
                            vol = message.replace("!volume", '')
                            try:
                                vol = int(vol.replace("/r", ''))
                            finally:
                                if vol > 100 or vol < 0:
                                    sendMessage(s, "Invalid volume level. Must be between 0-100.")
                                    break

                            p.audio_set_volume(vol)
                            sendMessage(s, "Music volume set to: " + str(vol))
                        if ("!volumeup" in command):
                            amt = int(message.replace("!volumeup", ''), message.replace("/r", ''))
                            print(str(amt))
                            p.audio_set_volume((p.audio_get_volume + 10))
                        if ("!volumedown" in command):
                            pass








            except socket.error:
                print("Socket died")

            except socket.timeout:
                print("Socket timeout")

def tick():
    import time
    print("ping")
    while True:
        time.sleep(0.3) #Slow down the stupidly fast loop for the sake of CPU
        global nowplaying
        global paused
        if (nowplaying == True and paused == False):  #Detect when a song is over
            time.sleep(1)
            nptime = int(p.get_time())
            nplength = int(p.get_length())

            if (nptime + 1500) > nplength:
                time.sleep(1)
                sendMessage(s, "Song is over!")
                global nowplaying
                nowplaying = False




        elif paused == False: # When a song is over, start a new song
            #(Parse the csv, grab the song off the top, play it, remove song from csv, resave it)
            try:
                with open('queue.csv', 'r') as f:
                    reader = csv.reader(f)
                    #remove the top line by rewriting it into a new csv cache
                    with open('queuecache.csv', 'w') as f1:
                        songtitle_csv = next(reader)[1]
                        for line in f:
                            f1.write(line)

                copyqueuecache()

                #Is it inefficient as fuck? yes. Does it work? Probably

                global p
                p = vlc.MediaPlayer(sr_geturl(songtitle_csv))
                p.play()
                nowplaying = True

            except StopIteration:
                print "List is empty"
                paused = True
        else:
            pass








t1 = Thread(target = main)
t2 = Thread(target = tick)


t1.start()
t2.start()