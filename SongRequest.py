
from gmusicapi import Mobileclient
from Initialize import dosqlite, openSocket, sendMessage
import sys
from pytube import YouTube
import validators
from Settings import *
reload(sys)
sys.setdefaultencoding('utf-8')

s = openSocket()
api = Mobileclient()
#Now using the newer oauth login!
api.oauth_login(device_id=Mobileclient.FROM_MAC_ADDRESS, oauth_credentials="oauth.txt")


if Mobileclient.is_authenticated(api) == True:
    print("Logged into GPM successfully")
else:
    sendMessage(s, "Can't log into Google Play Music! Please check the console and follow the instructions!")
    api.perform_oauth(storage_filepath="oauth.txt")
    api.oauth_login(device_id=Mobileclient.FROM_MAC_ADDRESS, oauth_credentials="oauth.txt")
stream_url = ""

def writenowplaying(isPlaying, song_name):
    with open("nowplaying.txt", "w") as f:
        if isPlaying == True:
            f.write(song_name)
        else:
            f.truncate()



def getytkey(url):
    if "youtube" in url.lower():
        return(url.split("=")[1][:11])
    elif "youtu.be" in url.lower():
        return(url.split("e/")[1][:11])
    else:
        return None


def songtitlefilter(song_name, redo):
    blacklist = BLACKLISTED_SONG_TITLE_CONTENTS[:]

    results = (Mobileclient.search(api, song_name)['song_hits'])[:SONGBLSIZE]
    songs = []

    for item in results:
        songs.append(item['track'])

    #Remove things from the blacklist if theyre explicitly requested
    for term in blacklist:
        if term.lower() in song_name.lower():
            blacklist.remove(term)

    #Iterate through the blacklisted contents, then the songs. Last song standing wins.
    for term in blacklist:
        if len(songs) == 1:
            break
        for song in reversed(songs):
            if len(songs) == 1:
                break
            if term.lower() in song['title'].lower():
                print ">Removed: " + song['title']
                songs.remove(song)


    for item in songs:
        print ">>>Allowed: " + item['title']
    print ">>>>>>Playing: " + songs[0]['title']
    return songs[redo]



#def srredo(song, user):
#    wrongsong(None, user)



def removetopqueue():
    import sqlite3 #Open the db, get the song out
    db = sqlite3.connect('songqueue.db')
    cursor = db.cursor()

    cursor.execute('''SELECT id, name, song, key FROM songs ORDER BY id ASC''') #Pick the top song
    row = cursor.fetchone()

    if row[1] == "BotPlaylist": #>>>>>> DO THIS STUFF IF THE LIST IS EMPTY!
        cursor.execute('SELECT id FROM songs ORDER BY id ASC LIMIT 1')
        row = cursor.fetchone()
        cursor.execute(('''DELETE FROM songs WHERE id={0}''').format(int(row[0]))) #Delete the top song
        db.commit()
        db.close()
        return

    db.close()
    return False






def sr_addsongtoplaylist(song_name):


    song_name = song_name.replace("\r", "")[1:]




    if validators.url(song_name) == True: #TEST IF THE REQUEST IS A LINK

        if "youtu" in song_name: #TEST IF THE SONG IS A YOUTUBE LINK
            try:
                title = YouTube(song_name).title
            except Exception as e:
                sendMessage(s, "Unable to use that video for some reason.")
                print e
                return


            key = getytkey(song_name)
            if key == None:
                sendMessage(s, "Something is wrong with your Youtube link.")
                return



            #TEST IF ITS ALREADY IN THE QUEUE
            sqlcommand = '''SELECT count(*) FROM playlist WHERE key="{0}"'''.format(key)
            if dosqlite(sqlcommand)[0] > (MAX_DUPLICATE_SONGS - 1):
                sendMessage(s, ("That song is already in the playlist."))
                return


            sqlcommand = '''
                        INSERT INTO playlist(song, key)
                        VALUES("{song_name}", "{key}");'''.format(song_name=song_name, key=key)

            dosqlite(sqlcommand)
            sendMessage(s, ("Added: " + title + " to the playlist (YT)"))
            return


        else:                       #OTHER MP3 REQUESTS <<<<<<<
            sqlcommand = '''
                    INSERT INTO playlist(song, key)
                    VALUES("{song_name}", "{key}");'''.format(song_name=song_name, key=song_name)

            dosqlite(sqlcommand)
            sendMessage(s, ("Added that link to the playlist."))
            return


    try:
        top_song_result = songtitlefilter(song_name, 0)
        key = top_song_result['storeId']
        songtitle = str(top_song_result['artist'] + " - " + top_song_result['title'])



    #If theres an error (its unable to find the song) then do fuck all, otherwise write the song data to the csv
    except IndexError:
        sendMessage(s, "No results found for that song. Please try a different one.")
        return
    else:
        #TEST IF ITS ALREADY IN THE QUEUE
        sqlcommand = '''SELECT count(*) FROM playlist WHERE key="{0}"'''.format(key)
        if dosqlite(sqlcommand)[0] > (MAX_DUPLICATE_SONGS - 1):
            sendMessage(s, ("That song is already in the playlist."))
            return

            #IF NOT, ADD IT
        sqlcommand = '''
                    INSERT INTO playlist(song, key)
                    VALUES("{song_name}", "{key}");'''.format(song_name=songtitle, key=key)

        dosqlite(sqlcommand)
        sendMessage(s, ("Added: " + songtitle + " to the backup playlist"))
        return
























def sr_getsong(song_name, user):

    sqlcommand = '''SELECT count(*) FROM songs WHERE name="{0}"'''.format(user)
    if dosqlite(sqlcommand)[0] > (MAX_REQUESTS_USER - 1):
        sendMessage(s, (user + " >> You already have " + str(MAX_REQUESTS_USER) + " songs in the queue."))
        return


    song_name = song_name.replace("\r", "")[1:]


    if validators.url(song_name) == True: #TEST IF THE REQUEST IS A LINK

        if "youtu" in song_name: #TEST IF THE SONG IS A YOUTUBE LINK
            try:
                title = YouTube(song_name).title
            except Exception as e:
                sendMessage(s, "Unable to use that video for some reason.")
                print e
                return


            key = getytkey(song_name)
            if key == None:
                sendMessage(s, "Something is wrong with your Youtube link.")
                return


            #TEST IF ITS ALREADY IN THE QUEUE
            sqlcommand = '''SELECT count(*) FROM songs WHERE key="{0}"'''.format(key)
            if dosqlite(sqlcommand)[0] > (MAX_DUPLICATE_SONGS - 1):
                sendMessage(s, (user + " >> That song is already in the queue."))
                return


            sqlcommand = '''
                            INSERT INTO songs(name, song, key)
                            VALUES("{user}", "{song_name}", "{key}");'''.format(user=user, song_name=song_name, key=key)

            dosqlite(sqlcommand)

            removetopqueue()
            sendMessage(s, (user + " >> Added: " + title + " to the queue (YT). ID: " + getnewentry()))


        else:                       #OTHER MP3 REQUESTS <<<<<<<
            sqlcommand = '''
                            INSERT INTO songs(name, song, key)
                            VALUES("{user}", "{song_name}", "{song_name}");'''.format(user=user, song_name=song_name)

            dosqlite(sqlcommand)
            removetopqueue()
            sendMessage(s, (user + " >> Added that link to the queue. ID: " + getnewentry()))




        #GOOGLE PLAY MUSIC STUFF
    else:
        try:
            top_song_result = songtitlefilter(song_name, 0)
            key = top_song_result['storeId']
            songtitle = str(top_song_result['artist'] + " - " + top_song_result['title'])



        #If theres an error (its unable to find the song) then do fuck all, otherwise write the song data to the csv
        except IndexError:
            sendMessage(s, "No results found for that song. Please try a different one.")
            return
        else:
            #TEST IF ITS ALREADY IN THE QUEUE
            sqlcommand = '''SELECT count(*) FROM songs WHERE key="{0}"'''.format(key)
            if dosqlite(sqlcommand)[0] > (MAX_DUPLICATE_SONGS - 1):
                sendMessage(s, (user + " >> That song is already in the queue."))
                return

                #IF NOT, ADD IT
            sqlcommand = '''
                        INSERT INTO songs(name, song, key)
                        VALUES("{user}", "{song_name}", "{key}");'''.format(user=user, song_name=songtitle, key=key)

            dosqlite(sqlcommand)
            removetopqueue()
            sendMessage(s, (user + " >> Added: " + songtitle + " to the queue. ID: " + getnewentry()))
            return




def getnewentry():
    import sqlite3
    db = sqlite3.connect('songqueue.db')
    cursor = db.cursor()
    cursor.execute('SELECT id FROM songs ORDER BY id DESC LIMIT 1')
    result = cursor.fetchone()
    return(str(result[0]))



def sr_geturl(songkey):
    try:
        stream_url = Mobileclient.get_stream_url(api, songkey, "3e9ff840362801d4")
        return(stream_url)
    except:
        sendMessage(s, "There was an issue playing the song.")

def wrongplsong(user):
    import sqlite3
    db = sqlite3.connect('songqueue.db')
    cursor = db.cursor()
    try:
        cursor.execute('SELECT id, song FROM playlist ORDER BY id DESC LIMIT 1')
        result = cursor.fetchone()
        toremove = str(result[0])
        strresult = (str(result[1]))
        cursor.execute('DELETE FROM playlist WHERE id={0}'.format(toremove))
        db.commit()
        sendMessage(s, (user + ' >> Removed your request: "' + strresult + '" from the queue.'))
    except Exception as e:
        print e
        sendMessage(s, "Couldn't find your most recent request.")

    db.close


def wrongsong(songid, user):
    import sqlite3
    from sqlite3 import Error
    db = sqlite3.connect('songqueue.db')
    cursor = db.cursor()
    if songid == None:
        try:
            cursor.execute('SELECT id, song FROM songs WHERE name="{0}"  ORDER BY id DESC LIMIT 1'.format(user))
            result = cursor.fetchone()
            toremove = str(result[0])
            strresult = (str(result[1]))
            cursor.execute('DELETE FROM songs WHERE id={0}'.format(toremove))
            db.commit()
            sendMessage(s, (user + ' >> Removed your request: "' + strresult + '" from the queue.'))
        except Error as e:
            raise e
            db.rollback()
        except:
            sendMessage(s, "Couldn't find your most recent request.")
        finally:
            db.close
    else:
        try:
            cursor.execute('SELECT song, name FROM songs WHERE id={0}'.format(songid))
            result = cursor.fetchone()
            strresult = (str(result[0]))
            if  user in result[1]:
                cursor.execute('DELETE FROM songs WHERE id={0}'.format(songid))
                db.commit()

                sendMessage(s, (user + ' >> Removed your request: "' + strresult + '" from the queue.'))
            else:
                sendMessage(s, (user + " >> You didn't request that song, you can't delete it!"))



        except Error as e:
            raise e
            db.rollback()
        except:
            sendMessage(s, "Couldn't find that request.")
        finally:
            db.close()




def clearsong(songid, user):
    import sqlite3
    from sqlite3 import Error
    db = sqlite3.connect('songqueue.db')
    cursor = db.cursor()
    if songid == None:
        try:
            cursor.execute('SELECT id, song, name FROM songs ORDER BY id DESC LIMIT 1')
            result = cursor.fetchone()
            toremove = str(result[0])
            strresult = (str(result[1]))
            cursor.execute('DELETE FROM songs WHERE id={0}'.format(toremove))
            db.commit()
            sendMessage(s, (user + ' >> Removed the request: "' + strresult + '" requested by ' + str(result[2]) + " from the queue."))
        except Error as e:
            raise e
            db.rollback()
        except:
            sendMessage(s, "Something messed up. Is the queue empty?")
        finally:
            db.close
    else:
        try:
            cursor.execute('SELECT song, name FROM songs WHERE id={0}'.format(songid))
            result = cursor.fetchone()
            strresult = (str(result[0]))

            cursor.execute('DELETE FROM songs WHERE id={0}'.format(songid))
            db.commit()

            sendMessage(s, (user + ' >> Removed the request: "' + strresult + '" requested by ' + str(result[1]) +" from the queue."))
        except Error as e:
            raise e
            db.rollback()
        except:
            sendMessage(s, "Couldn't find that request.")
        finally:
            db.close()



def playfromplaylist():

    import sqlite3 #Open the db, get the song out
    from sqlite3 import Error
    db = sqlite3.connect('songqueue.db')
    cursor = db.cursor()
    cursor.execute('''SELECT id, song, key FROM playlist ORDER BY id ASC''') #Pick the top song
    row = cursor.fetchone()
    if row == None: #>>>>>> DO THIS STUFF IF THE LIST IS EMPTY!
        print "Backup Playlist is empty!"
    try:
        songtitle = row[1]
        songkey = row[2]
    except:
        print(">>>>>>BACKUP PLAYLIST IS EMPTY! ADD SOME SONGS TO IT WITH FillPlaylist.py or !addsong !!!! <<<<<<<<<<<<<<<<")
        return


    #Delete the top result
    cursor.execute('SELECT id FROM playlist ORDER BY id ASC LIMIT 1')
    row = cursor.fetchone()

    cursor.execute(('''DELETE FROM playlist WHERE id={0}''').format(int(row[0]))) #Delete the top song

    cursor.execute(('''INSERT INTO playlist(song, key) VALUES("{song_name}", "{key}");''').format(song_name=songtitle, key=songkey))

    cursor.execute(('''INSERT INTO songs(name, song, key) VALUES("BotPlaylist", "{song_name}", "{key}");''').format(song_name=songtitle, key=songkey))
    db.commit()












#-------------------------SONG REQUEST COMMANDS----------------------------------


def volume(p, vol):
    if vol == None:
        sendMessage(s, "Current volume: " + str(p.audio_get_volume()))
        return
    if vol > 100 or vol < 0:
        sendMessage(s, "Invalid volume level. Must be between 0-100.")
        return
    p.audio_set_volume(vol)
    sendMessage(s, "Music volume set to: " + str(vol))

def volumeup(p, vol):
    if vol == None:
        vol = VOL_INCREMENT
    if (p.audio_get_volume() + vol) > 100:
        p.audio_set_volume(100)
        print "Raised the volume to: 100"
        return "Raised the volume to: 100"
    p.audio_set_volume((p.audio_get_volume() + vol))
    print ("Raised the volume to: " + str(p.audio_get_volume() + vol))
    return  ("Raised the volume to: " + str(p.audio_get_volume() + vol))


def volumedown(p, vol):
    if vol == None:
        vol = VOL_INCREMENT
    if (p.audio_get_volume() - vol) < 0:

        p.audio_set_volume(0)
        print "Lowered the volume to: 0"
        return "Lowered the volume to: 0"
    p.audio_set_volume((p.audio_get_volume() - vol))
    print "Lowered the volume to: " + str(p.audio_get_volume() - vol)
    return "Lowered the volume to: " + str(p.audio_get_volume() - vol)


