from urllib.request import urlopen
import random
from Settings import *
from Initialize import sendMessage, sqlitewrite, sqliteread

commands_BotCommands = {
    "!ping": ('bot.ping', 'cmdarguments', 'user'),
    "!uptime": ('bot.uptime', 'cmdarguments', 'user'),
    "!roll": ('bot.roll', 'cmdarguments', 'user'),

}

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

class BotCommands:
    def __init__(self):
        pass

    def ping(self, arg, user):
        return "Pong"

    def uptime(self, arg, user):
        f = urlopen("https://beta.decapi.me/twitch/uptime/" + CHANNEL)
        file = f.read().decode("utf-8")
        if "offline" in file:
            return file + "."
        else:
            return "The stream has been live for: " + file

    def roll(self, arg, user):
        arg = arg.replace("\r", "")
        splitCmd = arg.split("d")
        operators = ["+", "-", "/", "*"]
        op = ''
        mod = ''
        if not is_number(splitCmd[0]):
            splitCmd[0] = 1

        for item in operators:
            if item in splitCmd[1]:
                op = item
                secondSplitCmd = (splitCmd[1].split(item))
                mod = secondSplitCmd[1]
                splitCmd[1] = secondSplitCmd[0]
        # Calculate Values
        amt = int(splitCmd[0])
        size = int(splitCmd[1])
        total = 0
        rolls = []
        for item in operators:
            if item in splitCmd[1]:
                size = int(splitCmd[1].split(item)[0])
                op = item
                mod = int(splitCmd[1].split(item)[1])
        # Roll Stuff

        for x in range(0, amt):
            roll = random.randint(1, size)
            rolls.append(roll)
        total = eval(str(sum(rolls)) + " " + op + " " + mod)
        if (len(rolls) == 1) or (len(rolls) > 20):
            return("You rolled: >[ " + str(total) + " ]<")

        return("You rolled: " + str(rolls) + " with a total of: >[ " + str(total) + " ]<")




