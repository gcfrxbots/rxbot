from Socket import *
from Initialize import joinRoom
from SongRequest import *
import string
import vlc
from threading import Thread





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

p = vlc.MediaPlayer()



def main():
    import time
    s = openSocket()
    joinRoom(s)
    readbuffer = ""
    pingActive = 0
    data = ""
    timecontrol = time

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

                        user = getUser(line)
                        message = str(getMessage(line))

                        print(">> " + user + ": " + message)

                        if "!sr" in message.lower():
                            song_name = message.replace("!sr", '')
                            url = cmd_sr(song_name)
                            global p
                            p = vlc.MediaPlayer(url)
                            p.play()
                            timecontrol.sleep(1.5) # startup time.
                            duration = p.get_length() / 1000
                            mm, ss   = divmod(duration, 60)
                            print "Current song length is: ", "%02d:%02d" % (mm,ss)

                            global nowplaying
                            nowplaying = True

                            t2.start()

                        if "!pause" in message.lower():
                            p.pause()
                            nowplaying = False
                        if "!play" in message.lower():
                            p.pause()
                            nowplaying = True
                        if "!time" in message.lower():
                            time = p.get_time()
                            sendMessage(s, str(time))


                        if "!volume" in message.lower():
                            vol = message.replace("!volume", '')
                            vol = int(vol.replace("/r", ''))
                            if vol > 100 or vol < 0:
                                sendMessage(s, "Invalid volume level. Must be between 0-100.")
                                break

                            p.audio_set_volume(vol)
                            sendMessage(s, "Music volume set to: " + str(vol))
                        #if "!volumeup" in message.lower():
                        #    amt = int(message.replace("!volumeup", ''), message.replace("/r", ''))
                        #    print(str(amt))
                        #    volume = p.audio_get_volume
                        #    p.pause()

                        #if "!volumedown" in message.lower():
                        #    pass









            except socket.error:
                print("Socket died")

            except socket.timeout:
                print("Socket timeout")

def tick():
    import time
    print("ping")
    while True:
        if nowplaying == True:
            nptime = int(p.get_time())
            nplength = int(p.get_length())

            if (nptime + 1500) > nplength:
                time.sleep(1.5)
                sendMessage(s, "Song is over!")
                global nowplaying
                nowplaying = False


t1 = Thread(target = main)
t2 = Thread(target = tick)


t1.start()
