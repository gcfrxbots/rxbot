from Socket import *
from Initialize import joinRoom, initsqlite
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
def getint(cmdarguments):
    import re
    try:
        out = int(re.search(r'\d+', cmdarguments).group())
        print(str(out))
        return out
    except:
        return None



p = vlc.MediaPlayer()



def main():
    import time
    s = openSocket()
    joinRoom(s)
    readbuffer = ""
    initsqlite()

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
                        command = ((message.split(' ', 1)[0]).lower()).replace("\r", "")
                        print(command)
                        cmdarguments = message.replace(command or "\r" or "\n", "")
                        getint(cmdarguments)

                        print(">> " + user + ": " + message)

                        if ("!sr" == command):
                            global nowplaying, paused
                            sr_getsong(cmdarguments, user)
                            paused = False



                        if ("!pause" in command):
                            p.set_pause(True)
                            nowplaying = False
                            paused = True
                        if ("!play" == command):
                            p.set_pause(False)
                            nowplaying = True
                            paused = False
                        if ("!clearqueue" == command):
                            dosqlite('''DELETE FROM songs''')

                        if ("!time" == command):
                            time = p.get_time()
                            sendMessage(s, str(time))


                        if ("!veto" in command):
                            p.stop()
                            paused = False
                            nowplaying = False

                        if ("!wrongsong" == command):
                            queue = getint(cmdarguments)

                            import csv
                            index = 0
                            with open('queue.csv', 'rb') as inp, open('queuecache.csv', 'wb') as out:
                                writer = csv.writer(out)



                                if queue == None: #set the queue value to the last song in the queue
                                    queue = len(inp.readlines())
                                    print(queue)




                                for row in reversed(list(csv.reader(inp))):
                                    index += 1
                                    if index == queue:
                                        writer.writerow(row)






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
                                vol = 10
                            if (p.audio_get_volume() + vol) > 100:
                                sendMessage(s, "Raised the volume to: 100")
                                p.audio_set_volume(100)
                                break
                            sendMessage(s,  "Raised the volume to: " + str(p.audio_get_volume() + vol))
                            p.audio_set_volume((p.audio_get_volume() + vol))

                        if ("!volumedown" == command):
                            vol = getint(cmdarguments)
                            if vol == None:
                                vol = 10
                            if (p.audio_get_volume() - vol) < 0:
                                sendMessage(s, "Lowered the volume to: 0")
                                p.audio_set_volume(0)
                                break
                            sendMessage(s,  "Lowered the volume to: " + str(p.audio_get_volume() - vol))
                            p.audio_set_volume((p.audio_get_volume() - vol))








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

            try:
                import sqlite3
                from sqlite3 import Error
                db = sqlite3.connect('songqueue.db')
                cursor = db.cursor()
                cursor.execute('''SELECT id, name, song FROM songs ORDER BY id ASC''')
                row = cursor.fetchone()
                songtitle = row[2]

                #Delete the top result
                cursor.execute('SELECT id FROM songs ORDER BY id ASC LIMIT 1')
                row = cursor.fetchone()
                cursor.execute(('''DELETE FROM songs WHERE id={0}''').format(int(row[0])))
                db.commit()
            except Error as e:
                raise e
            except:
                print("List is Empty")
            finally:
                db.close

                try:
                    global p
                    p = vlc.MediaPlayer(sr_geturl(songtitle))
                    p.play()
                    nowplaying = True
                except:
                    pass








t1 = Thread(target = main)
t2 = Thread(target = tick)


t1.start()
t2.start()