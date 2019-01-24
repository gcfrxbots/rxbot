from Socket import *
from gmusicapi import Mobileclient
from Settings import GMEmail, GMPass
import vlc





s = openSocket()
api = Mobileclient()
api.login(GMEmail, GMPass, Mobileclient.FROM_MAC_ADDRESS)

if Mobileclient.is_authenticated(api) == True:
    print("Logged into GPM successfully")
else:
    print("Can't log into Google Play Music.")
stream_url = ""

def cmd_sr(song_name):
    print(song_name)

    try:
        results = Mobileclient.search(api, song_name)
        top_song_result = results['song_hits'][0]['track']

        sendMessage(s, "I found this song: " + str(top_song_result['artist'] + " - " + top_song_result['title']))
        global stream_url
        stream_url = Mobileclient.get_stream_url(api, top_song_result['storeId'], "3e9ff840362801d4")
        return(stream_url)

    except IndexError:
        sendMessage(s, "No results found for that song. Please try a different one.")

def cmd_pause():
    print(stream_url)
    p = vlc.MediaPlayer(stream_url)
    p.play()
    sendMessage(s, "Tried to pause")
    p.pause()
    #subprocess.call(['mpv', stream_url])
    #except:
        #sendMessage(s, "Error. Either no results found or shit broke.")


