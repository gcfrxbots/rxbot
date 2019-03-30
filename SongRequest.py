from gmusicapi import Mobileclient
from Initialize import sqliteread, sqlitewrite, openSocket, sendMessage,  createqueuecsv
import sys
from pytube import YouTube
import keyboard
import validators
import vlc
from Settings import *
import time
import sqlite3
from sqlite3 import Error
reload(sys)
sys.setdefaultencoding('utf-8')

s = openSocket()


api = Mobileclient()
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

def removetopqueue():
    row = sqliteread('''SELECT id, name, song, key FROM songs ORDER BY id ASC''') #Pick the top song
    if row[1] == "BotPlaylist": #>>>>>> DO THIS STUFF IF THE LIST IS EMPTY!
        sqlitewrite(('''DELETE FROM songs WHERE id={0}''').format(int(row[0]))) #Delete the top song
        return
    return False

def getnewentry():
    result = sqliteread('SELECT id FROM songs ORDER BY id DESC LIMIT 1')
    return(str(result[0]))

def sr_geturl(songkey):
    try:
        stream_url = Mobileclient.get_stream_url(api, songkey, "3e9ff840362801d4")
        return(stream_url)
    except Exception as e:
        print e
        sendMessage(s, "There was an issue playing the song.")

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

def getsongtime(title, key):
    songtime = -1
    try:
        if title:
            if title == "Online":
                songurl = key
            else:
                songurl = YouTube(title).streams.filter(only_audio=True).order_by('abr').first().url
        else:  # Otherwise it's GPM
            songurl = sr_geturl(key)
        instance = vlc.Instance()
        media = instance.media_new(songurl)
        player = instance.media_player_new()
        player.set_media(media)

        while songtime == -1:  # Yes, this is bad. Sometimes it doesn't get the time, so it keeps trying if it doesnt. It's totally random. Sorry.
            player.play()
            time.sleep(0.05)
            player.stop()
            songtime = media.get_duration()

    except Exception as e:
        print "GETSONGTIME ISSUE"
        print e
        return
    return (songtime - 1500) #Most songs have a 1.5 to 2 second offset



class SRcontrol:
    def __init__(self):
        self.msg = None
        self.songtitle = ""

    def playsong(self):
        row = sqliteread('''SELECT id, name, song, key FROM songs ORDER BY id ASC''') # Pick the top song
        try:
            self.songtitle = row[2]
            songkey = row[3]
        except Exception as e:
            print e
            print(">>>>>>BACKUP PLAYLIST IS EMPTY! ADD SOME SONGS TO IT WITH PlaylistEditor.py or !plsr<<<<<<")
            return
        sqlitewrite(('''DELETE FROM songs WHERE id={0}''').format(row[0]))  # Delete the top song

        try:
            if validators.url(self.songtitle) == True: # TEST IF THE REQUEST IS A LINK
                if "youtu" in self.songtitle:  # IS IT A YOUTUBE LINK?
                    playurl = YouTube(self.songtitle).streams.filter(only_audio=True).order_by('abr').first().url
                    self.songtitle = YouTube(self.songtitle).title
                    writenowplaying(True, self.songtitle)
                else:  # If not YT link, play normal music file.
                    playurl = self.songtitle
                    self.songtitle = "Online Music File"
                    writenowplaying(True, self.songtitle)
            else:  # Otherwise it's GPM
                playurl = sr_geturl(songkey)
                writenowplaying(True, self.songtitle)

            self.p = vlc.MediaPlayer(playurl)  # Play the music
            self.p.play()
            writenowplaying(True, self.songtitle)
            createqueuecsv()
            if ENABLE_HOTKEYS:
                pass
                #hotkeys()
            return True
        except Exception as e:
            print "PLAYSONG ERROR:"
            print e

    def songover(self):
        print("Song is over!")
        time.sleep(DELAY_BETWEEN_SONGS)
        self.p.stop()
        return False

    def gettime(self):
        return int(self.p.get_time())





    #-------------------------SONG REQUEST COMMANDS----------------------------------




    def volume(self, vol, user):
        if vol == None:
            return "Current volume: " + str(self.p.audio_get_volume())
        if (vol > 100) or (vol < 0):
            return "Invalid volume level. Must be between 0-100."
        self.p.audio_set_volume(vol)
        return "Music volume set to: " + str(vol)

    def volumeup(self, vol, user):
        if not vol:
            vol = VOL_INCREMENT
        currentvolume = self.p.audio_get_volume()
        if (currentvolume + vol) > 100:
            self.p.audio_set_volume(100)
            print "Raised the volume to: 100"
            return "Raised the volume to: 100"
        self.p.audio_set_volume(currentvolume + vol)
        self.msg = "Raised the volume to: " + str(currentvolume + vol)
        print self.msg
        return self.msg

    def volumedown(self, vol, user):
        if not vol:
            vol = VOL_INCREMENT
        currentvolume = self.p.audio_get_volume()
        if (currentvolume - vol) < 0:
            self.p.audio_set_volume(0)
            print "Lowered the volume to: 0"
            return "Lowered the volume to: 0"
        self.p.audio_set_volume(currentvolume - vol)
        self.msg = "Lowered the volume to: " + str(currentvolume - vol)
        print self.msg
        return self.msg


    def play(self):
        print "Resumed the music"
        writenowplaying(True, self.songtitle)
        self.p.set_pause(False)


    def pause(self):
        print "Paused the music"
        writenowplaying(False, "")
        self.p.set_pause(True)




class SRcommands:
    def __init__(self):
        self.db = None

    '''--------------------QUEUE CONTROL--------------------'''

    def songrequest(self, request, user):
        if request == "\r":  # Send a message if they request nothing
            return user + " >> " + DEFAULT_SR_MSG
        # Check for songs already in the queue
        if sqliteread('''SELECT count(*) FROM songs WHERE name="{0}"'''.format(user))[0] > (MAX_REQUESTS_USER - 1):
            return user + " >> You already have " + str(MAX_REQUESTS_USER) + " songs in the queue."

        request = request.replace("\r", "")[1:]
        # LINKS
        # DETERMINE LINK TYPE
        if validators.url(request):
            if "youtu" in request:
                try:
                    title = YouTube(request).title
                except Exception as e:
                    print e
                    return "Unable to use that video for some reason."
                key = getytkey(request)
                if not key: return "Something is wrong with your Youtube link."

                # Check the queue to see if the song is already in there.
                self.db = sqliteread('''SELECT id, count(*) FROM songs WHERE key="{0}"'''.format(key))

                if self.db[1] > (MAX_DUPLICATE_SONGS - 1):
                    return user + " >> That song is already in the queue."
                songtime = getsongtime(request, key)
                if songtime > (MAXTIME * 60000):
                    return user + " >> That song exceeds the maximum length of " + str(MAXTIME) + " minutes."

                sqlitewrite('''INSERT INTO songs(name, song, key, time) VALUES("{user}", "{request}", "{key}", "{time}");'''.format(user=user, request=request, key=key, time=songtime))
                removetopqueue()
                return user + " >> Added: " + title + " to the queue (YT). ID: " + getnewentry()
            else:  # OTHER MP3 REQUESTS <<<<<<<
                songtime = getsongtime("Online", request)
                if songtime > (MAXTIME * 60000):
                    return user + " >> That song exceeds the maximum length of " + str(MAXTIME) + " minutes."

                sqlitewrite('''INSERT INTO songs(name, song, key, time) VALUES("{user}", "{request}", "{request}", "{time}");'''.format(user=user, request=request, time=songtime))
                removetopqueue()
                return user + " >> Added that link to the queue. ID: " + getnewentry()

        else:  # GOOGLE PLAY MUSIC STUFF
            try:
                top_song_result = songtitlefilter(request, 0)
                key = top_song_result['storeId']
                songtitle = str(top_song_result['artist'] + " - " + top_song_result['title'])
            # If theres an error (its unable to find the song) then announce it, otherwise write the song data to the db
            except IndexError:
                return "No results found for that song. Please try a different one."
            else:
                # Test if the song is already in the queue
                self.db = sqliteread('''SELECT id, count(*) FROM songs WHERE key="{0}"'''.format(key))
                if self.db[1] > (MAX_DUPLICATE_SONGS - 1):
                    return user + " >> That song is already in the queue."
                songtime = getsongtime(None, key)

                if songtime > (MAXTIME * 60000):
                    return user + " >> That song exceeds the maximum length of " + str(MAXTIME) + " minutes."

                # Add song to the queue
                sqlitewrite('''INSERT INTO songs(name, song, key, time) VALUES("{user}", "{request}", "{key}", "{time}");'''.format(user=user, request=songtitle, key=key, time=songtime))
                removetopqueue()
                return user + " >> Added: " + songtitle + " to the queue. ID: " + getnewentry()

    def youtubesr(self, request, user):
        pass


    def wrongsong(self, songid, user):
        if not songid:
            try:
                result = sqliteread('SELECT id, song FROM songs WHERE name="{0}"  ORDER BY id DESC LIMIT 1'.format(user))
                sqlitewrite('DELETE FROM songs WHERE id={0}'.format(str(result[0])))
                return user + ' >> Removed your request: "' + str(result[1]) + '" from the queue.'
            except Error as e:
                raise e
            except:
                return user + " >> Couldn't find your most recent request."
        else:
            try:
                result = sqliteread('SELECT song, name FROM songs WHERE id={0}'.format(songid))
                if user in result[1]:
                    sqlitewrite('DELETE FROM songs WHERE id={0}'.format(songid))
                    return user + ' >> Removed your request: "' + str(result[0]) + '" from the queue.'
                else:
                    return user + " >> You didn't request that song, you can't delete it!"
            except Error as e:
                raise e
            except:
                return user + " >> Couldn't find that request."


    def getnowplaying(self, x, user):
        with open("nowplaying.txt", "r") as f:
            returnnp = f.readlines()
        if not returnnp:
            sendMessage(s, (user + " >> The music is currently paused."))
        else:
            sendMessage(s, (user + " >> " + returnnp[0]))


    def clearsong(self, songid, user):
        if not songid:
            try:
                result = sqliteread('SELECT id, song, name FROM songs ORDER BY id DESC LIMIT 1')
                sqlitewrite('DELETE FROM songs WHERE id={0}'.format(str(result[0])))
                return user + ' >> Removed the request: "' + str(result[1]) + '" requested by ' + str(result[2]) + " from the queue."
            except Error as e:
                raise e
            except:
                return "Something messed up. Is the queue empty?"
        else:
            try:
                result = sqliteread('SELECT song, name FROM songs WHERE id={0}'.format(songid))
                sqlitewrite('DELETE FROM songs WHERE id={0}'.format(songid))
                return user + ' >> Removed the request: "' + str(result[0]) + '" requested by ' + str(result[1]) +" from the queue."
            except Error as e:
                raise e
            except:
                return user + " >> Couldn't find that request."


    def queuetime(self, id, user):
        import sqlite3
        from sqlite3 import Error
        data = []
        db = sqlite3.connect('songqueue.db')
        try:
            cursor = db.cursor()
            if not id:  # If there's no ID, get the total song
                cursor.execute('''SELECT time FROM songs''')
            else:  # Get up to that song
                cursor.execute('''SELECT time FROM songs WHERE id < {0}'''.format(id))
            data = cursor.fetchall()
            if (not data) or (data[0][0] == None):
                if id:
                    return user + " >> That ID is not in the queue."
                else:
                    return user + " >> There are currently no songs in the queue."
            totaltime = 0
            for item in data:
                totaltime += int(item[0])
            seconds=(totaltime/1000)%60
            minutes=(totaltime/(1000*60))%60
            hours=(totaltime/(1000*60*60))%24
            db.close()
            return user + " >> There is about " + str(hours) + "h " + str(minutes) + "m " + str(seconds) + "s of songs in the queue."
        except Error as e:
            db.rollback()
            print "QUEUETIME ERROR:"
            print e

    '''--------------------BACKUP PL CONTROL--------------------'''

    def plsongrequest(self, request, user):
        request = request.replace("\r", "")[1:]
        # LINKS
        # DETERMINE LINK TYPE
        if validators.url(request):
            if "youtu" in request:
                try:
                    title = YouTube(request).title
                except Exception: return user + " >> Unable to use that video for some reason."
                key = getytkey(request)
                if not key: return user + " >> Something is wrong with your Youtube link."

                # Check the queue to see if the song is already in there.
                self.db = sqliteread('''SELECT id, count(*) FROM playlist WHERE key="{0}"'''.format(key))
                if self.db[1] > (MAX_DUPLICATE_SONGS - 1):
                    return user + " >> That song is already in the playlist. ID: " + str(self.db[0])
                sqlitewrite('''INSERT INTO playlist(song, key) VALUES("{request}", "{key}");'''.format(request=request, key=key))
                return user + " >> Added: " + title + " to the playlist (YT). ID: " + str(sqliteread('SELECT id FROM playlist ORDER BY id DESC LIMIT 1')[0])
            else:  # OTHER MP3 REQUESTS <<<<<<<
                sqlitewrite('''INSERT INTO playlist(song, key) VALUES("{request}", "{request}");'''.format(request=request))
                return user + " >> Added that link to the playlist. ID: " + str(sqliteread('SELECT id FROM playlist ORDER BY id DESC LIMIT 1')[0])
        else:  # GOOGLE PLAY MUSIC STUFF
            try:
                top_song_result = songtitlefilter(request, 0)
                key = top_song_result['storeId']
                songtitle = str(top_song_result['artist'] + " - " + top_song_result['title'])
            # If theres an error (its unable to find the song) then announce it, otherwise write the song data to the db
            except IndexError:
                return user + " >> No results found for that song. Please try a different one."
            else:
                # Test if the song is already in the playlist
                self.db = sqliteread('''SELECT id, count(*) FROM playlist WHERE key="{0}"'''.format(key))
                if self.db[1] > (MAX_DUPLICATE_SONGS - 1):
                    return user + " >> That song is already in the playlist. ID: " + str(self.db[0])
                # Add song to the playlist
                sqlitewrite('''INSERT INTO playlist(song, key) VALUES("{request}", "{key}");'''.format(request=songtitle, key=key))
                return user + " >> Added: " + songtitle + " to the playlist. ID: " + str(sqliteread('SELECT id FROM playlist ORDER BY id DESC LIMIT 1')[0])


    def plclearsong(self, songid, user):
        if not songid:
            try:
                result = sqliteread('SELECT id, song FROM playlist ORDER BY id DESC LIMIT 1')
                sqlitewrite('DELETE FROM playlist WHERE id={0}'.format(str(result[0])))
                return user + ' >> Removed your request: "' + str(result[1]) + '" from the backup playlist.'
            except Exception as e:
                print e
                return user + " >> Couldn't find the most recent request."
        else:
            try:
                result = sqliteread('SELECT song FROM playlist WHERE id={0}'.format(songid))
                sqlitewrite('DELETE FROM playlist WHERE id={0}'.format(songid))
                return user + ' >> Removed the song: "' + str(result[0]) + " from the queue."
            except Error as e:
                raise e
            except:
                return user + " >> Couldn't find that request."
