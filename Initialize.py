import string
import urllib, json
import socket
import sys
import ssl
import sqlite3
from sqlite3 import Error
from Settings import *
import xlsxwriter
import os
reload(sys)
sys.setdefaultencoding('utf-8')

# Auto package installer. Causes issues with new pip version.
#required = ['gmusicapi', 'validators', 'pytube', 'python-vlc', 'xlsxwriter']
#installed = [pkg.key for pkg in pip.get_installed_distributions()]
#
#for package in required:
#    if package not in installed:
#        print ("INITIAL SETUP >> " + package + " seems to be missing. Installing it.")
#        try:
#            pip.main(['install', '-q', package])
#        except WindowsError:
#            print "WinErr"



if not os.path.exists('Output'):
    os.makedirs('Output')

def reconnect():
    if RESTART:
        print "Detected a critical error with the bot's connection to GPM or Twitch. Restarting connections!"
        s.send(("PART #" + CHANNEL + "\r\n").encode("utf-8"))
        s.close()
        os.execv(sys.executable, ['python'] + sys.argv)
        quit()

def openSocket():
    global s
    if PORT in (443, 6697):
        old_s = socket.socket()
        s = ssl.wrap_socket(old_s)
    else:
        s = socket.socket()
    s.connect(("irc.chat.twitch.tv", PORT))
    s.send(("PASS " + BOT_OAUTH + "\r\n").encode("utf-8"))
    s.send(("NICK " + BOT_NAME + "\r\n").encode("utf-8"))
    s.send(("JOIN #" + CHANNEL + "\r\n").encode("utf-8"))
    return s


def sendMessage(s, message):
    messageTemp = "PRIVMSG #" + CHANNEL + " : " + message
    s.send((messageTemp + "\r\n").encode("utf-8"))
    print(("Sent: " + messageTemp).encode("utf-8"))


def joinRoom(s):
    readbuffer = ""
    Loading = True

    while Loading:
        readbuffer = readbuffer + s.recv(1024,)
        temp = string.split(readbuffer, "\n")
        readbuffer = temp.pop()

        for line in temp:
            print(line)
            Loading = loadingComplete(line)



def loadingComplete(line):
    if("End of /NAMES list" in line):
        return False
    else:
        return True


def sqliteread(command):
    db = sqlite3.connect('songqueue.db')
    try:
        cursor = db.cursor()
        cursor.execute(command)
        data = cursor.fetchone()
        db.close()
        return data
    except Error as e:
        db.rollback()
        print "SQLITE READ ERROR:"
        print e

def sqlitewrite(command):
    db = sqlite3.connect('songqueue.db')
    try:
        cursor = db.cursor()
        cursor.execute(command)
        data = cursor.fetchone()
        db.commit()
        db.close()
        createsongqueue()
        return data
    except Error as e:
        db.rollback()
        print "SQLITE WRITE ERROR:"
        print e



def createsongqueue():
    db = sqlite3.connect('songqueue.db')

    cursor = db.cursor()
    cursor.execute("SELECT id, name, song FROM songs")
    data = cursor.fetchall()
    # Write to the excel workbook
    row = 1
    col = 0
    try:
        with xlsxwriter.Workbook('Output/SongQueue.xlsx') as workbook:
            worksheet = workbook.add_worksheet('Queue')
            format = workbook.add_format({'bold': True, 'center_across': True, 'font_color': 'white', 'bg_color': 'gray'})
            center = workbook.add_format({'center_across': True})
            worksheet.set_column(0, 0, 8)
            worksheet.set_column(1, 1, 30)
            worksheet.set_column(2, 2, 100)
            worksheet.write(0, 0, "ID", format)
            worksheet.write(0, 1, "User", format)
            worksheet.write(0, 2, "Title / Link", format)
            for id, name, song in (data):
                worksheet.write(row, col,   id, center)
                worksheet.write(row, col + 1, name, center)
                worksheet.write(row, col + 2, song)
                row += 1
    except IOError:
        print "ERROR - UNABLE TO READ XLSX DOC! You probably have it open, close it ya buffoon"



def getmoderators():
    json_url = urllib.urlopen('http://tmi.twitch.tv/group/user/' + CHANNEL + '/chatters')

    data = json.loads(json_url.read())
    mods = data['chatters']['moderators']

    for item in mods:
        if mods not in MODERATORS:
            MODERATORS.append(item)

    return MODERATORS


