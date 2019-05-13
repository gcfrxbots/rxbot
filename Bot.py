from Settings import *
from Initialize import sendMessage, sqlitewrite, sqliteread

commands_BotCommands = {
    "!test": ('bot.test', 'cmdarguments', 'user'),
    #"!bottest": ('bot.test', 'cmdarguments', 'user'),


}

class BotCommands:
    def __init__(self):
        pass

    def test(self, arg, user):
        return "Test"