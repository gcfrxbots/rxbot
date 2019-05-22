from Settings import *
from subprocess import call
import urllib, urllib.request
import json
import socket
import sqlite3
from sqlite3 import Error
import os
from random import shuffle
try:
    import xlsxwriter
    from gmusicapi import Mobileclient
    import validators
    import vlc
    import youtube_dl
    import pafy
    from system_hotkey import SystemHotkey
except ImportError as e:
    print(e)
    raise ImportError(">>> One or more required packages are not properly installed! Run INSTALL_REQUIREMENTS.bat to fix!")




def initSetup():
    api = Mobileclient()

    # Update Youtube_DL
    print("Attempting to update Youtube resources...")
    call("py -3.7 -m pip install --upgrade youtube_dl")

    # Create Folders
    if not os.path.exists('Output'):
        os.makedirs('Output')
    if not os.path.exists('Resources'):
        os.makedirs('Resources')
        print("Creating necessary folders...")

    # Download necessary files
    if not os.path.exists('Resources/generic_art.jpg'):
        print("Downloading necessary files...")
        f = open('Resources/generic_art.jpg', 'wb')
        f.write(urllib.request.urlopen('https://rxbots.weebly.com/uploads/6/1/2/6/61261317/generic-art_orig.jpg').read())
        f.close()

    # Check SongQueue.xlsx
    print("Creating & Cleaning Up SongQueue and NowPlaying")
    with xlsxwriter.Workbook('Output/SongQueue.xlsx') as workbook:
        worksheet = workbook.add_worksheet('Queue')
        format = workbook.add_format({'bold': True, 'center_across': True, 'font_color': 'white', 'bg_color': 'gray'})
        worksheet.set_column(0, 0, 8)
        worksheet.set_column(1, 1, 30)
        worksheet.set_column(2, 2, 100)
        worksheet.write(0, 0, "ID", format)
        worksheet.write(0, 1, "User", format)
        worksheet.write(0, 2, "Title / Link", format)

    # Check NowPlaying.txt
    with open("Output/NowPlaying.txt", "w") as f:
        f.truncate()

    # Log into GPM
    print("Logging into Google Play Music (Still required for Youtube Only Mode)...")
    if api.oauth_login(device_id=Mobileclient.FROM_MAC_ADDRESS, oauth_credentials="Resources/oauth.txt"):
        print("Logged into GPM successfully")
    else:
        api.perform_oauth(storage_filepath="Resources/oauth.txt")
        if not api.oauth_login(device_id=Mobileclient.FROM_MAC_ADDRESS, oauth_credentials="Resources/oauth.txt"):
            raise ConnectionError("Unable to log into Google Play Music!")

    # Check Settings
    print("Verifying Settings.py is set up correctly...")
    if PORT not in (80, 6667, 443, 6697):
        raise ConnectionError("Wrong Port! The port must be 80 or 6667 for standard connections, or 443 or 6697 for SSL")
    if not BOT_OAUTH or not ('oauth:' in BOT_OAUTH):
        raise Exception("Missing or invalid BOT_OAUTH - Please follow directions in the settings or readme.")
    if not BOT_NAME or not CHANNEL:
        raise Exception("Missing BOT_NAME or CHANNEL - Please follow directions in the settings or readme")

    # Create Sqlite3 File
    print("Creating and updating botData.db...")
    try:
        db = sqlite3.connect('Resources/botData.db')
        sql_creation_commands = (
            # Create Queue
            """ CREATE TABLE IF NOT EXISTS queue (
                            id integer PRIMARY KEY,
                            name text NOT NULL,
                            song text,
                            key text,
                            time text
                        ); """,
            # Create Backup Playlist
            """ CREATE TABLE IF NOT EXISTS playlist (
                            id integer PRIMARY KEY,
                            song text NOT NULL,
                            key text
                        ); """,

            # Create Userdata Playlist
            """ CREATE TABLE IF NOT EXISTS userdata (
                            id integer PRIMARY KEY,
                            user text NOT NULL,
                            currency text
                            hours text
                        ); """,
    )
        c = db.cursor()
        for item in sql_creation_commands:
            c.execute(item)
        db.commit()
        db.close()
    except Error as e:
        print(e)

    # Shuffle Playlist
    if SHUFFLE_ON_START:
        print("Shuffling Playlist...")
        db = sqlite3.connect('Resources/botData.db')
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

    print(">> Bot Startup Complete!")
    return api


def openSocket():
    global s
    s = socket.socket()
    s.connect(("irc.chat.twitch.tv", PORT))
    s.send(("PASS " + BOT_OAUTH + "\r\n").encode("utf-8"))
    s.send(("NICK " + BOT_NAME + "\r\n").encode("utf-8"))
    s.send(("JOIN #" + CHANNEL + "\r\n").encode("utf-8"))
    return s


def sendMessage(message):
    print(message)
    messageTemp = "PRIVMSG #" + CHANNEL + " : " + message
    s.send((messageTemp + "\r\n").encode("utf-8"))
    print("Sent: " + messageTemp)


def joinRoom(s):
    readbuffer = ""
    Loading = True

    while Loading:
        readbuffer = readbuffer + s.recv(1024).decode("utf-8")
        temp = readbuffer.split("\n")
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
    db = sqlite3.connect('Resources/botData.db')
    try:
        cursor = db.cursor()
        cursor.execute(command)
        data = cursor.fetchone()
        db.close()
        return data
    except Error as e:
        db.rollback()
        print("SQLITE READ ERROR:")
        print(e)

def sqlitewrite(command):
    db = sqlite3.connect('Resources/botData.db')
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
        print("SQLITE WRITE ERROR:")
        print(e)



def createsongqueue():
    db = sqlite3.connect('Resources/botData.db')
    cursor = db.cursor()
    cursor.execute("SELECT id, name, song FROM queue")
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
        print("ERROR - UNABLE TO READ XLSX DOC! You probably have it open, close it ya buffoon")



def getmoderators():
    json_url = urllib.request.urlopen('http://tmi.twitch.tv/group/user/' + CHANNEL + '/chatters')

    data = json.loads(json_url.read())
    mods = data['chatters']['moderators']

    for item in mods:
        if mods not in MODERATORS:
            MODERATORS.append(item)

    return MODERATORS


