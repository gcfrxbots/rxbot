from Settings import *
from Initialize import sendMessage, sqlitewrite, sqliteread


'''

Welcome to Rxbot Custom Commands!
All your commands will go in commands_CustomCommands so that they can be run.
Everything should remain a string, and will be converted when run.
For MOD only commands, the first value should be 'MOD' and everything else stays normal.
Anything in the CustomCommands() class is run with "customcmds.function"
If you make more classes you'll need to initalize them in Run.py
You can use 'cmdarguments' for all the arguments given, or 'getint(cmdarguments)' for just an int given.
Every command MUST have two arguments, usually args and user. If yours doesn't need two, just use x and y.

'''

commands_CustomCommands = {
    "!ccexample": ('customcmds.example', 'cmdarguments', 'user'),
    "!ccexamplemod": ('MOD', 'customcmds.modexample', 'cmdarguments', 'user'),
}


class CustomCommands():
    def __init__(self):
        pass

    def example(self, args, user):
        print("The user who did this command is: " + user)
        print("Everything after the command that the user typed is: " + args)

        # To send the message, return it as a string. Most messages start with 'user + " >> "'
        return user + " >> You just ran an example custom command. Your args were " + args

    def modexample(self, args, user):
        print("The user who did this command is: " + user)
        print("Everything after the command that the user typed is: " + args)

        # To send the message, return it as a string. Most messages start with 'user + " >> "'
        return user + " >> You just ran an example Mod-Only custom command. Your args were " + args