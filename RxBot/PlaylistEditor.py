#This script is meant to populate the playlist table with a user's playlist from google play music.
from gmusicapi import Mobileclient
import sqlite3
import xlrd
from Settings import listSettings, listFloats

def readSettings():
    wb = xlrd.open_workbook('../Config/Settings.xlsx')
    settings = {}
    worksheet = wb.sheet_by_name("Settings")

    for item in range(worksheet.nrows):
        if item == 0:
            pass
        else:
            option = worksheet.cell_value(item, 0)
            try:
                setting = int(worksheet.cell_value(item, 1))
            except ValueError:
                setting = str(worksheet.cell_value(item, 1))
            # Test if setting is a list
            if option in listSettings:
                setting = list(map(str.strip, setting.split(',')))
            if option in listFloats:
                setting = float(worksheet.cell_value(item, 1))

            settings[option] = setting
    return settings


settings = readSettings()


if settings["GPM ENABLE"]:
    api = Mobileclient()
    print("Logging into Google Play Music...")
    if api.oauth_login(device_id=Mobileclient.FROM_MAC_ADDRESS, oauth_credentials="Resources/oauth.txt"):
        print("Logged into GPM successfully")
    else:
        api.perform_oauth(storage_filepath="Resources/oauth.txt")
        if not api.oauth_login(device_id=Mobileclient.FROM_MAC_ADDRESS, oauth_credentials="Resources/oauth.txt"):
            raise ConnectionError("Unable to log into Google Play Music!")
else:
    print("Youtube-Only mode enabled. As of now, filling the playlist is not supported here and you'll need to add songs with !plsr.")








def fillPlaylist():
    print("These playlists were detected on your Google Play Music account:")
    print(">>-------------------------------------<<")
    dplaylists = api.get_all_user_playlist_contents()
    index = 1
    for item in dplaylists:
        print((str(index) + ". " + item['name']))
        index += 1
    index -= 1
    print(">>-------------------------------------<<")
    selection = eval(input("Please type the number of the playlist you wish to import into the bot's backup playlist, then press ENTER. \n"))
    while (selection < 1) or (selection > index):
        selection = eval(input("The number you have entered is invalid. Please enter a number between 1 and " + str(index) + ". \n"))
    selection -= 1
    playlist = dplaylists[selection]

    print("Using the songs from playlist: " + playlist['name'])

    db = sqlite3.connect('Resources/botData.db')
    cursor = db.cursor()
    index = 0
    errors = 0
    for item in playlist['tracks']:
        if item['trackId'][0][0] == "T":
            try:
                songtitle = (item['track']['artist'] + " - " + item['track']['title'])
                key = item['track']['storeId']

                sqlcommand = '''
                            INSERT INTO playlist(song, key)
                            VALUES("{song_name}", "{key}");'''.format(song_name=songtitle.replace('"', "'"), key=key)

                cursor.execute(sqlcommand)


                print(str(index) + " - Added: " + songtitle)
            except KeyError:
                pass
            except Exception as e:
                print(">>>>>>>>>>>>>>>Something went wrong with adding the last song. Error below.<<<<<<<<<<<<<<<<<<<<<<<<<<")
                errors += 1
                print(e)
        else:
            print(str(index) + " - >>>>>>>>User Uploaded File - Cannot add to the playlist. Try !plsr with Youtube or an online link.")
            errors += 1
        index += 1
    print(">>>Finished! Out of " + str(index) + " songs, " + str(index - errors) + " were added successfully. There were " + str(errors) + " songs that couldn't be added, probably because they were user uploaded files.")

    db.commit()
    db.close()


def updateplaylist():
    db = sqlite3.connect('Resources/botData.db')
    cursor = db.cursor()
    cursor.execute('''SELECT * FROM playlist''')
    listSongs = cursor.fetchall()

    dbSongTitles = []
    for item in listSongs:
        dbSongTitles.append(item[2])
    print("Loading playlists, please wait...")
    dplaylists = api.get_all_user_playlist_contents()

    if len(settings["GPM PLAYLIST"]) == 0:
        print("These playlists were detected on your Google Play Music account:")
        print(">>-------------------------------------<<")
        index = 1
        for item in dplaylists:
            print((str(index) + ". " + item['name']))
            index += 1
        index -= 1
        print(">>-------------------------------------<<")
        selection = eval(input("Please type the number of the playlist you wish to merge with the bot's playlist, then press ENTER. \n"))
        while (selection < 1) or (selection > index):
            selection = eval(input("The number you have entered is invalid. Please enter a number between 1 and " + str(index) + ". \n"))
        selection -= 1
        playlist = dplaylists[selection]

        print("Using the songs from playlist: " + playlist['name'])
        print("You can set GPM PLAYLIST in the settings file to avoid doing this next time.")

    else:
        playlist = None
        for item in dplaylists:
            if (item['name'].lower()) == (settings["GPM PLAYLIST"].lower()):
                playlist = item
        if not playlist:
            raise Exception("Invalid setting for GPM PLAYLIST setting - That playlist doesn't exist on your account")
    gpmSongTitles = []
    for item in playlist['tracks']:
        if item['trackId'][0][0] == "T":
            gpmSongTitles.append(item['track']['storeId'])
    toAdd = list(set(gpmSongTitles) - set(dbSongTitles))

    if len(toAdd) == 0:
        print("It doesn't look like there are any songs in the selected playlist that aren't already in the bot's playlist.")
        return

    for item in toAdd:
        for gpmitem in playlist['tracks']:
            if gpmitem['trackId'] == item:
                songtitle = (gpmitem['track']['artist'] + " - " + gpmitem['track']['title'])
                key = gpmitem['track']['storeId']
                print(songtitle + " has been added!")
                cursor.execute('''
                            INSERT INTO playlist(song, key)
                            VALUES("{song_name}", "{key}");'''.format(song_name=songtitle.replace('"', "'"), key=key))
    db.commit()
    db.close()



def shuffleplaylist():
    from random import shuffle
    db = sqlite3.connect('Resources/botData.db')
    cursor = db.cursor()
    cursor.execute('''SELECT * FROM playlist ORDER BY RANDOM()''')
    listSongs = cursor.fetchall()
    shuffle(listSongs)
    clearplaylist()
    for item in listSongs:
        print("Added: " + item[1])
        sqlcommand = '''
                        INSERT INTO playlist(song, key)
                        VALUES("{song_name}", "{key}");'''.format(song_name=item[1].replace('"', "'"), key=item[2])
        cursor.execute(sqlcommand)
    db.commit()
    db.close()

def viewplaylist():
    db = sqlite3.connect('Resources/botData.db')
    cursor = db.cursor()
    cursor.execute('''SELECT * FROM playlist''')
    listSongs = cursor.fetchall()
    for item in listSongs:
        id = str(item[0])
        title = str(item[1])
        key = str(item[2])

        print("ID: " + id + " >>  " + title + "  >> Key: " + key)








def clearplaylist():
    db = sqlite3.connect('Resources/botData.db')
    cursor = db.cursor()
    sqlcommand = '''DELETE FROM playlist'''
    cursor.execute(sqlcommand)
    db.commit()
    db.close()


while True:
    print(">>-------------------------------------<<")
    print("Welcome to the RXBot Backup Playlist Control Application. What would you like to do? "
          "\n1. Fill Playlist "
          "\n2. Update Playlist "
          "\n3. Shuffle Playlist "
          "\n4. View Playlist "
          "\n5. Clear Playlist "
          "\n0. Exit "

          )
    print(">>-------------------------------------<<")
    inp = eval(input("Type the number of the option you would like here then press ENTER: \n"))
    if inp == 1:
        fillPlaylist()
        wait = input("Finished, press ENTER to return to Main Menu")
    if inp == 2:
        updateplaylist()
        wait = input("Finished, press ENTER to return to Main Menu")
    if inp == 3:
        shuffleplaylist()
        wait = input("Shuffled the playlist, press ENTER to return to Main Menu")
    if inp == 4:
        viewplaylist()
        wait = input("Press ENTER to close")
    if inp == 5:
        clearplaylist()
        wait = input("Cleared the whole backup playlist. Press ENTER to return to Main Menu")
    if inp == 0:
        quit()













