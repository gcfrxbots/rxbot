import string
import socket
import sys
import csv

reload(sys)
sys.setdefaultencoding('utf-8')
from Settings import *





def openSocket():

    s = socket.socket()
    s.connect(("irc.twitch.tv", PORT))
    s.send("PASS " + BOT_OAUTH + "\r\n")
    s.send("NICK " + BOT_NAME + "\r\n")
    s.send("JOIN #" + CHANNEL + "\r\n")
    return s


def sendMessage(s, message):
    messageTemp = "PRIVMSG #" + CHANNEL + " : " + message
    s.send(messageTemp + "\r\n")
    print("Sent: " + messageTemp)


def joinRoom(s):
    readbuffer = ""
    Loading = True

    while Loading:
        readbuffer = readbuffer + s.recv(1024)
        temp = string.split(readbuffer, "\n")
        readbuffer = temp.pop()

        for line in temp:
            print(line)
            Loading = loadingComplete(line)

    sendMessage(s, "Successfully joined the chat!")
    global nowplaying
    nowplaying = False


def loadingComplete(line):
    if("End of /NAMES list" in line):
        return False
    else:
        return True


def sqliteread(command):
    import sqlite3
    from sqlite3 import Error
    db = sqlite3.connect('songqueue.db')
    try:
        cursor = db.cursor()
        cursor.execute(command)
        data = cursor.fetchone()
        db.close()
        createqueuecsv()
        return data
    except Error as e:
        db.rollback()
        print "SQLITE READ ERROR:"
        print e

def sqlitewrite(command):
    import sqlite3
    from sqlite3 import Error
    db = sqlite3.connect('songqueue.db')
    try:
        cursor = db.cursor()
        cursor.execute(command)
        data = cursor.fetchone()
        db.commit()
        db.close()
        createqueuecsv()
        return data
    except Error as e:
        db.rollback()
        print "SQLITE WRITE ERROR:"
        print e



def createqueuecsv():
    import sqlite3
    from sqlite3 import Error
    db = sqlite3.connect('songqueue.db')
    try:
        cursor = db.cursor()
        cursor.execute("SELECT id, name, song FROM songs")
        data = cursor.fetchall()

        with open('Output/SongQueue.csv', 'wb') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Requested By', 'Song Title / Youtube URL'])
            writer.writerows(data)

    except Error as e: print e



def getmoderators():
    import urllib, json
    json_url = urllib.urlopen('http://tmi.twitch.tv/group/user/' + CHANNEL + '/chatters')

    data = json.loads(json_url.read())
    mods = data['chatters']['moderators']

    for item in mods:
        if mods not in MODERATORS:
            MODERATORS.append(item)

    return MODERATORS


