import socket
from Settings import *

def openSocket():

    s = socket.socket()
    s.connect((HOST, PORT))
    s.send("PASS " + BOT_OAUTH + "\r\n")
    s.send("NICK " + BOT_NAME + "\r\n")
    s.send("JOIN #" + CHANNEL + "\r\n")
    return s


def sendMessage(s, message):
    messageTemp = "PRIVMSG #" + CHANNEL + " :"  + message
    s.send(messageTemp + "\r\n")
    print("Sent: " + messageTemp)