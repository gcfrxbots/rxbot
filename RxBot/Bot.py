from urllib.request import urlopen
import random
import xlsxwriter
import datetime
from Initialize import sendMessage, sqlitewrite, sqliteread, settings, sqliteFetchAll

commands_BotCommands = {
    "!ping": ('bot.ping', 'cmdarguments', 'user'),
    "!uptime": ('bot.uptime', 'cmdarguments', 'user'),
    "!roll": ('bot.roll', 'cmdarguments', 'user'),
    "!r": ('bot.roll', 'cmdarguments', 'user'),  # Alias
    "!reloaddb": ("STREAMER", 'dbCloner.manualCloneDb', 'None', 'None'),
    "!quote": ('quotes', 'cmdarguments', 'user'),
    "!addquote": ('quotes.addQuote', 'cmdarguments', 'user'),
    "!removequote": ('quotes.rmQuote', 'cmdarguments', 'user'),
    "!deletequote": ('quotes.rmQuote', 'cmdarguments', 'user'),  # Alias
    "!test": ('getCurrentGame', 'cmdarguments', 'user'),

}


def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def todaysDate():
    today = datetime.datetime.now()
    return today.strftime("%m/%d/%y")


class BotCommands:
    def __init__(self):
        pass

    def ping(self, arg, user):
        return "Pong"

    def uptime(self, arg, user):
        f = urlopen("https://beta.decapi.me/twitch/uptime/" + settings['CHANNEL'])
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


class QuoteControl:
    def __init__(self):
        self.usedQuotes = []

    def __call__(self, arg, user):
        if not arg.strip():
            return self.displayQuote()
        firstArg = arg.split()[0].lower()
        arg = (arg.replace(arg.split()[0], '').strip())

        if is_number(firstArg):
            return self.displayQuoteById(firstArg)
        elif firstArg == "add":
            return self.addQuote(arg, user)
        elif firstArg == "remove":
            return self.rmQuote(arg, user)
        elif firstArg == "delete":
            return self.rmQuote(arg, user)


    def displayQuote(self):
        if not self.usedQuotes:  # Don't filter if theres nothing to filter
            data = sqliteFetchAll('''SELECT * FROM quotes ORDER BY RANDOM()''')
        else:
            strUsedQuotes = ""
            for item in self.usedQuotes:
                strUsedQuotes += '"%s", ' % item  # dude i dunno math
            strUsedQuotes = strUsedQuotes[:-2]  # Format a string to filter by and filter by it
            data = sqliteFetchAll('''SELECT * FROM quotes WHERE id NOT IN (%s) ORDER BY RANDOM()''' % strUsedQuotes)

        if not data:  # If it's returned empty, reset the list and grab a random quote
            self.usedQuotes = []
            data = sqliteFetchAll('''SELECT * FROM quotes ORDER BY RANDOM()''')
        if not data:  # No quotes in db
            return "There are currently no quotes. Add one with !quote add"

        quote = data[0]  # Fuck its 1am
        self.usedQuotes.append(quote[0])
        if "''" in quote[1]:
            return '%s (%s)' % (quote[1], quote[2])
        else:
            return '"%s" (%s)' % (quote[1], quote[2])

    def displayQuoteById(self, id):
        data = sqliteread("SELECT * FROM quotes WHERE id=%s" % id)
        if not data:
            return "No quote exists with that ID."
        if "''" in data[1]:
            return '%s (%s)' % (data[1], data[2])
        else:
            return '"%s" (%s)' % (data[1], data[2])

    def addQuote(self, arg, user):
        if not arg or (arg == " "):
            return "You need to specify something to be quoted."
        arg = arg.strip()

        if arg[0] in ["'", '"'] and arg[-1] in ["'", '"']:
            arg = arg.strip("'")
            arg = arg.strip('"')

        arg = arg.replace('"', "''")  # Replace double quotes with two single quotes

        if sqlitewrite('''INSERT INTO quotes(quote, date) VALUES("%s", "%s");''' % (arg, todaysDate())):
            newId = str(sqliteread('SELECT id FROM quotes ORDER BY id DESC LIMIT 1')[0])
            return "Quote successfully added [ID: %s]" % newId
        else:
            print(user + " >> Your quote was not successfully added. Please try again.")

    def rmQuote(self, arg, user):
        if not arg or (arg == " "):
            return "You need to specify a quote ID to remove."
        arg = arg.strip()
        idExists = sqliteread('''SELECT id FROM quotes WHERE id = "%s";''' % arg)
        if idExists:
            sqlitewrite('''DELETE FROM quotes WHERE id = "%s";''' % arg)
            return "Quote %s successfully removed." % arg
        else:
            return "Quote %s does not exist." % arg



quotes = QuoteControl()
bot = BotCommands()