import string

from Socket import sendMessage
import sys
reload(sys)
sys.setdefaultencoding('UTF8')
def joinRoom(s):
    readbuffer = ""
    Loading = True

    while Loading:
        readbuffer = readbuffer + s.recv(1024)
        temp = string.split(readbuffer, "\n")
        readbuffer = temp.pop()

        for line in temp:
            print(line)
            Loading = loadingComplete(line)

    sendMessage(s, "Successfully joined the chat!")
    global nowplaying
    nowplaying = False


def loadingComplete(line):
    if("End of /NAMES list" in line):
        return False
    else:
        return True

def initsqlite():
    import sqlite3
    from sqlite3 import Error
    #initalize the database
    try:
        db = sqlite3.connect("songqueue.db")
    except Error as e:
        print(e)

    #initalize the tables

    try:
        cursor = db.cursor()
        cursor.execute ('''
		CREATE TABLE songs(id INTEGER PRIMARY KEY, name TEXT, song TEXT)
	''')
        db.commit()
    except Error as e:
        db.rollback()
        print(e)
    finally:
        db.close()

def dosqlite(command):
    import sqlite3
    from sqlite3 import Error
    db = sqlite3.connect('songqueue.db')
    try:
        cursor = db.cursor()
        cursor.execute(command)
        db.commit()
    except Error as e:
        db.rollback()
        print e
    finally:
        db.close


