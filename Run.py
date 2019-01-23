from Socket import *
from Initialize import joinRoom
from SongRequest import *
import string
import vlc

s = openSocket()
joinRoom(s)
readbuffer = ""
pingActive = 0
data = ""




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

                if "!sr" in message:
                    song_name = message.replace("!sr", '')
                    cmd_test(song_name)
                if "!pause" in message:
                    cmd_pause()






    except socket.error:
        print("Socket died")

    except socket.timeout:
        print("Socket timeout")