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
import requests
from bs4 import BeautifulSoup
try:
    import xlsxwriter
    import xlrd
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
    if not os.path.exists('../Config'):
        buildConfig()
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

            # Create Userdata
            """ CREATE TABLE IF NOT EXISTS userdata (
                            id integer PRIMARY KEY,
                            user text NOT NULL,
                            currency text
                            hours text
                        ); """,

            # Create Quotes Table
            """ CREATE TABLE IF NOT EXISTS quotes (
                            id integer PRIMARY KEY,
                            quote text NOT NULL,
                            date text,
                            game text
                        ); """,
    )
        c = db.cursor()
        for item in sql_creation_commands:
            c.execute(item)
        db.commit()
        db.close()
    except Error as e:
        print(e)

    if os.path.exists("../Output/BotData.xlsx"):
        dbCloner.cloneXlsxToDb()
        print("Cloned everything in BotData.xlsx to the database")
    else:
        dbCloner.cloneDbToXlsx()
        print("Created BotData.xlsx in /Output")

    if not os.path.exists('../Config/Playlist Editor.exe'):
        copyfile('Playlist Editor.exe', '../Config/Playlist Editor.exe')

    # Update Playlist
    if settings['UPDATE PL ON START']:
        updatePlaylists(api)

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



    return api


def updatePlaylists(api):
    playlist = None
    if not settings["GPM PLAYLISTS"]:
        stopBot("You have UPDATE PL ON START enabled, but no playlist specified in GPM PLAYLISTS.")
    print("Updating your playlist, please wait...")


    db = sqlite3.connect('Resources/botData.db')
    cursor = db.cursor()

    botSongData = {}
    songsAdded = 0


    allGPMPlaylists = api.get_all_user_playlist_contents()

# Select the correct playlist, specified in Settings
    for settingPlaylist in settings["GPM PLAYLISTS"]:
        gpmSongs = {}
        for gpmPlaylist in allGPMPlaylists:
            if gpmPlaylist['name'].lower() in settingPlaylist.lower():
                playlist = gpmPlaylist  # Set playlist to the correct playlist specified in settings
        if not playlist:
            stopBot("Invalid playlist in GPM PLAYLISTS setting - %s doesn't exist on your account" % settingPlaylist)

# Populate botSongData with stuff from database
        songsAlreadyInPlaylist = sqliteFetchAll('''SELECT song, key FROM playlist''')
        for item in songsAlreadyInPlaylist:
            botSongData[item[1]] = item[0]

# Populate validGPMTracks with only songs that are good and correct IDs
        validGPMTracks = {}
        for track in playlist['tracks']:  # Load in all songs
            if track['trackId'][0][0] == "T":
                validGPMTracks[track['track']['storeId']] = (track['track']['artist'] + " - " + track['track']['title'])  # All GPM'able songs in the playlist
                # songID : songTitle

# Fill gpmSongs with all songs not already in the database
        for gpmSongId, gpmSong in validGPMTracks.items():
            if gpmSongId not in botSongData.keys():
                #print(gpmSongId)
                gpmSongs[gpmSongId] = gpmSong


# Add songs to database
        if len(gpmSongs) > 0:  # If theres actually something to add
            for songId, songTitle in gpmSongs.items():
                cursor.execute('''INSERT INTO playlist(song, key) VALUES("{song_name}", "{key}");'''.format(
                    song_name=songTitle.replace('"', "'"), key=songId))
                songsAdded += 1

    if songsAdded > 0:
        print(str(songsAdded) + " new songs added to the backup playlist!")
    else:
        print("No new songs to add to your playlist.")

    #cursor.execute('''DELETE FROM playlist WHERE song IN (SELECT song FROM playlist GROUP BY song HAVING COUNT(*) > 1);''')
    db.commit()
    db.close()


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
        print(command)


def sqliteFetchAll(command):
    db = sqlite3.connect('Resources/botData.db')
    try:
        cursor = db.cursor()
        cursor.execute(command)
        data = cursor.fetchall()
        db.close()
        return data
    except Error as e:
        db.rollback()
        print("SQLITE FETCHALL ERROR:")
        print(e)
        print(command)


def sqlitewrite(command):
    db = sqlite3.connect('Resources/botData.db')
    try:
        cursor = db.cursor()
        cursor.execute(command)
        db.commit()
        db.close()

        if "queue" in command:
            createsongqueue()
        if ("playlist" in command) or ("quotes" in command):
            dbCloner.cloneDbToXlsx()
        return True
    except Error as e:
        db.rollback()
        print("SQLITE WRITE ERROR:")
        print(e)
        print(command)
        return False


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


def getCurrentGame():
    return "Go fuck yourself"


class dbClone:
    def __init__(self):
        self.listDbs = ['quotes', 'playlist']  # Remember to update triggers in sqlitewrite too, dipshit
        self.cursor = None

    def cloneDbToXlsx(self):
        try:
            with xlsxwriter.Workbook('../Output/BotData.xlsx') as workbook:
                for db in self.listDbs:
                    dbColumns = []
                    dbData = sqliteFetchAll("SELECT * FROM %s" % db)

                    for item in sqliteFetchAll("PRAGMA table_info(%s);" % db):
                        dbColumns.append(item[1])

                    worksheet = workbook.add_worksheet(db.capitalize())
                    header = workbook.add_format(
                        {'bold': True, 'center_across': True, 'font_color': 'black'})
                    # Add the ID column, which will always remain constant
                    worksheet.set_column(0, 0, 10)
                    worksheet.set_column(1, (len(dbColumns)-1), 75)

                    for column in enumerate(dbColumns):  # Write headers
                        worksheet.write(0, column[0], column[1].capitalize(), header)

                    row = 1  # Fill in data
                    try:
                        for entry in dbData:
                            for item in enumerate(entry):
                                col = item[0]
                                worksheet.write(row, col, item[1])
                            row += 1
                    except TypeError:
                        print("No data in database.")
        except PermissionError:
            print("\n\nCANT UPDATE BOTDATA.XLSX, PLEASE CLOSE THE FILE!\n\n")

    def cloneXlsxToDb(self):
        database = sqlite3.connect('Resources/botData.db')
        self.cursor = database.cursor()
        wb = xlrd.open_workbook('../Output/BotData.xlsx')
        for db in self.listDbs:
            db = db.capitalize()
            worksheet = wb.sheet_by_name(db)
            if not self.checkReset(db, worksheet.nrows):
                print("\n\nWARNING- While syncing BotData.xlsx to the bot's database, it looks like 3 or more rows have been deleted from %s. Proceed?" % db.capitalize())
                print("Type yes to proceed, and sync the new data in BotData.xlsx to the bot's database.")
                print("Type skip to skip this, and sync the bot's existing database with your BotData.xlsx")
                print("Type anything else to close the bot.")
                inp = input(">> ").lower()
                if inp == "skip":
                    break
                elif inp != "yes":
                    stopBot("BotData.xlsx is either empty or missing a bunch of data. Type 'skip' next time you're prompted to load old bot data.")

            self.cursor.execute("DELETE FROM %s" % db.lower())
            database.commit()

            header = ""
            for row in range(worksheet.nrows):
                if row == 0:
                    for column in range(worksheet.ncols):
                        option = worksheet.cell_value(row, column)
                        header += option + ", "
                    header = (header[:-2]).lower()
                else:
                    rowData = ""  # Data per row
                    for column in range(worksheet.ncols):
                        option = worksheet.cell_value(row, column)
                        try:  # Convert the float IDs into Ints
                            option = int(option)
                            rowData += ('%s, ' % option)
                        except ValueError:
                            rowData += ('"%s", ' % option)

                    # Add to database
                    rowData = rowData[:-2]
                    self.cursor.execute("INSERT INTO {database}({header}) VALUES({rowData});".format(database=db, header=header, rowData=rowData))

        database.commit()
        database.close()

    def checkReset(self, db, rows):
        self.cursor.execute("SELECT * FROM %s" % db)
        dbData = self.cursor.fetchall()
        dbSize = len(dbData)

        if dbSize > 0:  # If the database was not empty
            if rows < 2:  # If theres only one or no rows
                return False

        if (dbSize - 3) > rows:
            return False

        return True

    def manualCloneDb(self, x, y):
        self.cloneXlsxToDb()
        return("Cloned the contents of BotData.xlsx to the bot's database.")


dbCloner = dbClone()



