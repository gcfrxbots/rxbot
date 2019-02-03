from Socket import *
from gmusicapi import Mobileclient
from Settings import GMEmail, GMPass
import csv
from Initialize import dosqlite
import validators
import sys
from pytube import YouTube
import vlc
reload(sys)
sys.setdefaultencoding('UTF8')

s = openSocket()
api = Mobileclient()
api.login(GMEmail, GMPass, Mobileclient.FROM_MAC_ADDRESS)

if Mobileclient.is_authenticated(api) == True:
    print("Logged into GPM successfully")
else:
    print("Can't log into Google Play Music.")
stream_url = ""

def sr_getsong(song_name, user):

    song_name = song_name.replace("\r", "")[1:]


    if validators.url(song_name) == True: #TEST IF THE REQUEST IS A LINK

        if "youtu" in song_name: #TEST IF THE SONG IS A YOUTUBE LINK
            title = YouTube(song_name).title
            print(title)
            sqlcommand = '''
                            INSERT INTO songs(name, song)
                            VALUES("{user}", "{song_name}");'''.format(user=user, song_name=song_name)

            dosqlite(sqlcommand)
            sendMessage(s, (user + " >> Added: " + title + " to the queue. (YT)"))
        else:
            sqlcommand = '''
                            INSERT INTO songs(name, song)
                            VALUES("{user}", "{song_name}");'''.format(user=user, song_name=song_name)

            dosqlite(sqlcommand)
            sendMessage(s, (user + " >> Added that link to the queue."))









    else:
        try:
            results = Mobileclient.search(api, song_name)
            top_song_result = results['song_hits'][0]['track']






        #If theres an error (its unable to find the song) then do fuck all, otherwise write the song data to the csv
        except IndexError:
            sendMessage(s, "No results found for that song. Please try a different one.")
        else:
            sendMessage(s, (user + " >> Added: " + str(top_song_result['artist'] + " - " + top_song_result['title'] + " to the queue.")))
            sqlcommand = '''
                        INSERT INTO songs(name, song)
                        VALUES("{user}", "{song_name}");'''.format(user=user, song_name=song_name)

            dosqlite(sqlcommand)










def sr_geturl(songtitle_csv):
    try:
        results = Mobileclient.search(api, songtitle_csv)
        top_song_result = results['song_hits'][0]['track']
        stream_url = Mobileclient.get_stream_url(api, top_song_result['storeId'], "3e9ff840362801d4")
        return(stream_url)
    except:
        sendMessage(s, "There was an issue playing the song.")


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
            strresult = (str(result[0]))[1:-1]
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
            strresult = (str(result[0]))[1:-1]

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