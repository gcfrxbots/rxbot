import datetime
import re
from threading import Thread
from CustomCommands import CustomCommands, commands_CustomCommands
from SongRequest import *
from Bot import *
from Initialize import settings, hotkeys

sr = SRcommands()
srcontrol = SRcontrol()
bot = BotCommands()
customcmds = CustomCommands()
nowplaying = False
paused = False


def togglepause(x, y):
    if paused:
        play(None, None)
    elif not paused:
        pause(None, None)


# These functions require two variables to call to avoid having way more code in the top loop.
def play(x, y):
    global nowplaying, paused
    nowplaying = True
    paused = False
    print(srcontrol.play())


def pause(x, y):
    global nowplaying, paused
    nowplaying = False
    paused = True
    print(srcontrol.pause())


def veto(x, y):
    global nowplaying, paused
    srcontrol.songover()
    paused = False
    nowplaying = False


# Init Hotkeys
def manageHotkeys(event, hotkey, args):
    if hotkeys[args[0]][1]:
        runcommand(args[0], None, "Hotkey", False)
    else:
        runcommand(args[0], None, "Hotkey", True)

if settings['ENABLE HOTKEYS']:
    hk = SystemHotkey(consumer=manageHotkeys)
    for item in hotkeys:
        hk.register(hotkeys[item][0], callback=item)


def getUser(line):
    seperate = line.split(":", 2)
    user = seperate[1].split("!", 1)[0]
    return user


def getMessage(line):
    seperate = line.split(":", 2)
    message = seperate[2]
    return message


def formatted_time():
    return datetime.datetime.today().now().strftime("%I:%M")


def getint(cmdarguments):
    try:
        out = int(re.search(r'\d+', cmdarguments).group())
        return out
    except:
        return None


def runcommand(command, cmdarguments, user, mute):
    commands = {**commands_SongRequest, **commands_BotCommands, **commands_CustomCommands}
    cmd = None
    arg1 = None
    arg2 = None

    for item in commands:
        if item == command:
            if commands[item][0] == "MOD":  # MOD ONLY COMMANDS:
                if (user in getmoderators()) or (user == "Hotkey") or mute:
                    cmd = commands[item][1]
                    arg1 = commands[item][2]
                    arg2 = commands[item][3]
                else:
                    sendMessage("You don't have permission to do this.")
                    return
            else:
                cmd = commands[item][0]
                arg1 = commands[item][1]
                arg2 = commands[item][2]
            break
    if not cmd:
        return
    output = eval(cmd + '(' + arg1 + ', ' + arg2 + ')')
    if not output:
        return
    if mute:
        print(output)
    else:
        sendMessage(output)

def main():
    global nowplaying, paused
    s = openSocket()
    joinRoom(s)
    readbuffer = ""
    while True:
        try:
            readbuffer = readbuffer + s.recv(1024).decode("utf-8")
            temp = readbuffer.split("\n")
            readbuffer = temp.pop()
            for line in temp:
                if "PING" in line:
                    s.send(bytes("PONG :tmi.twitch.tv\r\n".encode("utf-8")))
                else:
                    # All these things break apart the given chat message to make things easier to work with.
                    user = getUser(line)
                    message = str(getMessage(line))
                    command = ((message.split(' ', 1)[0]).lower()).replace("\r", "")
                    cmdarguments = message.replace(command or "\r" or "\n", "")
                    getint(cmdarguments)
                    print(("(" + formatted_time() + ")>> " + user + ": " + message))
                    # Run the commands function
                    if command[0] == "!":
                        runcommand(command, cmdarguments, user, False)
        except Exception as e:
            print("Error while running command:")
            print(e)


# If the queue is completely empty at start, add a song so it's not pulling nonexistent values in the loop below
if not sqliteread('''SELECT id, name, song, key FROM queue ORDER BY id ASC'''):
    playfromplaylist()


def tick():
    timecache = 0
    global nowplaying, paused
    while True:
        time.sleep(0.2)
        # Check if there's nothing in the playlist.
        if not sqliteread('''SELECT id, name, song, key FROM queue ORDER BY id ASC'''):
            playfromplaylist()  # Move a song from the playlist into the queue.

        if paused or not nowplaying:  # If for any reason the music isnt playing, change the nowplaying to nothing
            writenowplaying(False, "")

        if nowplaying and not paused:  # If music IS playing:
            time.sleep(0.3)
            nptime = srcontrol.gettime()  # Save the current now playing time

            if timecache == nptime:  # If the cache (written 0.3 seconds before) and the time are equal, songs over
                time.sleep(0.3)
                nowplaying = srcontrol.songover()
            timecache = nptime

        elif not paused and not nowplaying:  # When a song is over, start a new song
            nowplaying = srcontrol.playsong()
            timecache = 1
            time.sleep(1)


def console():
    while True:
        consoleIn = input("")

        command = ((consoleIn.split(' ', 1)[0]).lower()).replace("\r", "")
        cmdarguments = consoleIn.replace(command or "\r" or "\n", "")
        # Run the commands function
        if command:
            if command[0] == "!":
                runcommand(command, cmdarguments, "CONSOLE", True)

            if command.lower() == "quit":
                print("Shutting down")
                pause(None, None)
                saveAlbumArt(None)
                os._exit(1)


t1 = Thread(target=main)
t2 = Thread(target=tick)
t3 = Thread(target=console)

t1.start()
t2.start()
t3.start()
