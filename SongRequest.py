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

def cmd_test(song_name):
    print(song_name)

    #try:
    results = Mobileclient.search(api, song_name)
    top_song_result = results['song_hits'][0]['track']

    sendMessage(s, "I found this song: " + str(top_song_result['artist'] + " - " + top_song_result['title']))

    stream_url = Mobileclient.get_stream_url(api, top_song_result['storeId'], "3e9ff840362801d4")


    p = vlc.MediaPlayer(stream_url)
    p.play()


def cmd_pause():
    p = vlc.MediaPlayer()
    sendMessage(s, "Tried to pause")
    p.stop()
    #subprocess.call(['mpv', stream_url])
    #except:
        #sendMessage(s, "Error. Either no results found or shit broke.")


