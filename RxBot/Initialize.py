from Settings import *
from subprocess import call
import urllib, urllib.request
import json
import socket
import sqlite3
from sqlite3 import Error
from shutil import copyfile
import os
from random import shuffle
try:
    import xlsxwriter
    from gmusicapi import Mobileclient
    import validators
    import vlc
    import youtube_dl
    import pafy
    from system_hotkey import SystemHotkey, SystemRegisterError
except ImportError as e:
    print(e)
    raise ImportError(">>> One or more required packages are not properly installed! Run INSTALL_REQUIREMENTS.bat to fix!")
global settings, hotkeys

def initSetup():
    api = Mobileclient()
    global settings, hotkeys

    # Update Youtube_DL
    print("Attempting to update Youtube resources...")
    call("py -3.7 -m pip install --upgrade youtube_dl --user --no-warn-script-location")
    # Create Folders
    if not os.path.exists('../Output'):
        os.makedirs('../Output')
    if not os.path.exists('Resources'):
        os.makedirs('Resources')
        print("Creating necessary folders...")

    # Download necessary files
    if not os.path.exists('../Config/generic_art.jpg'):
        print("Downloading necessary files...")
        f = open('../Config/generic_art.jpg', 'wb')
        f.write(urllib.request.urlopen('https://rxbots.weebly.com/uploads/6/1/2/6/61261317/generic-art_orig.jpg').read())
        f.close()

    # Create Settings.xlsx
    loadedsettings = settingsConfig.settingsSetup(settingsConfig())
    settings = loadedsettings[0]
    hotkeys = loadedsettings[1]

    # Check SongQueue.xlsx
    print("Creating & Cleaning Up SongQueue and NowPlaying")
    with xlsxwriter.Workbook('../Output/SongQueue.xlsx') as workbook:
        worksheet = workbook.add_worksheet('Queue')
        format = workbook.add_format({'bold': True, 'center_across': True, 'font_color': 'white', 'bg_color': 'gray'})
        worksheet.set_column(0, 0, 8)
        worksheet.set_column(1, 1, 30)
        worksheet.set_column(2, 2, 100)
        worksheet.write(0, 0, "ID", format)
        worksheet.write(0, 1, "User", format)
        worksheet.write(0, 2, "Title / Link", format)

    # Check NowPlaying.txt
    with open("../Output/NowPlaying.txt", "w") as f:
        f.truncate()

    # Log into GPM
    if settings['GPM ENABLE']:
        if api.oauth_login(device_id=Mobileclient.FROM_MAC_ADDRESS, oauth_credentials="Resources/oauth.txt"):
            print("Logged into GPM successfully")
        else:
            api.perform_oauth(storage_filepath="Resources/oauth.txt")
            if not api.oauth_login(device_id=Mobileclient.FROM_MAC_ADDRESS, oauth_credentials="Resources/oauth.txt"):
                raise ConnectionError("Unable to log into Google Play Music!")
    else:
        print("Youtube-Only mode enabled. No GPM login needed.")

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

    if not os.path.exists('../Config/Playlist Editor.exe'):
        copyfile('Playlist Editor.exe', '../Config/Playlist Editor.exe')

    # Shuffle Playlist
    if settings['SHUFFLE ON START']:
        db = sqlite3.connect('Resources/botData.db')
        cursor = db.cursor()
        cursor.execute('''SELECT * FROM playlist ORDER BY RANDOM()''')
        listSongs = cursor.fetchall()
        shuffle(listSongs)
        sqlcommand = '''DELETE FROM playlist'''
        cursor.execute(sqlcommand)
        for item in listSongs:
            cursor.execute('''INSERT INTO playlist(song, key) VALUES("{song_name}", "{key}");'''.format(song_name=item[1].replace('"', "'"), key=item[2]))
        db.commit()
        db.close()
        print("Backup Playlist has been shuffled.")

    # Update Playlist
    if settings['UPDATE PL ON START']:
        db = sqlite3.connect('Resources/botData.db')
        cursor = db.cursor()
        cursor.execute('''SELECT * FROM playlist''')
        listSongs = cursor.fetchall()
        dbSongTitles = []
        for item in listSongs:
            dbSongTitles.append(item[2])
        print("Updating your playlist, please wait...")
        dplaylists = api.get_all_user_playlist_contents()
        playlist = None
        for item in dplaylists:
            if (item['name'].lower()) == (settings["GPM PLAYLIST"].lower()):
                playlist = item
        if not playlist:
            stopBot("Invalid setting for GPM PLAYLIST setting - That playlist doesn't exist on your account")
        gpmSongTitles = []
        for item in playlist['tracks']:
            if item['trackId'][0][0] == "T":
                gpmSongTitles.append(item['track']['storeId'])
        toAdd = list(set(gpmSongTitles) - set(dbSongTitles))

        if len(toAdd) > 0:
            for item in toAdd:
                for gpmitem in playlist['tracks']:
                    if gpmitem['trackId'] == item:
                        songtitle = (gpmitem['track']['artist'] + " - " + gpmitem['track']['title'])
                        key = gpmitem['track']['storeId']
                        cursor.execute('''
                                    INSERT INTO playlist(song, key)
                                    VALUES("{song_name}", "{key}");'''.format(song_name=songtitle.replace('"', "'"),
                                                                              key=key))
            print(str(len(toAdd)) + " new songs added to the backup playlist!")
        else:
            print("No new songs to add to your playlist.")
        db.commit()
        db.close()



    print(">> Initial Checkup Complete! Connecting to Chat...")
    return api


def openSocket():
    global s
    s = socket.socket()
    s.connect(("irc.chat.twitch.tv", int(settings['PORT'])))
    s.send(("PASS " + settings['BOT OAUTH'] + "\r\n").encode("utf-8"))
    s.send(("NICK " + settings['BOT NAME'] + "\r\n").encode("utf-8"))
    s.send(("JOIN #" + settings['CHANNEL'] + "\r\n").encode("utf-8"))
    return s


def sendMessage(message):
    print(message)
    messageTemp = "PRIVMSG #" + settings['CHANNEL'] + " : " + message
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
        print(">> Bot Startup complete!")
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
        with xlsxwriter.Workbook('../Output/SongQueue.xlsx') as workbook:
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
    json_url = urllib.request.urlopen('http://tmi.twitch.tv/group/user/' + settings['CHANNEL'].lower() + '/chatters')
    data = json.loads(json_url.read())['chatters']
    mods = data['moderators'] + data['broadcaster']

    for item in mods:
        if item not in list(settings['MODERATORS']):
            settings['MODERATORS'].append(item)

    return settings['MODERATORS']


