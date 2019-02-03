from Socket import *
from gmusicapi import Mobileclient
from Settings import GMEmail, GMPass
import csv
import vlc
from Initialize import dosqlite


s = openSocket()
api = Mobileclient()
api.login(GMEmail, GMPass, Mobileclient.FROM_MAC_ADDRESS)

if Mobileclient.is_authenticated(api) == True:
    print("Logged into GPM successfully")
else:
    print("Can't log into Google Play Music.")
stream_url = ""

csv.register_dialect('myDialect',
                     quoting=csv.QUOTE_ALL,
                     skipinitialspace=True)

def sr_getsong(song_name, user):
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
