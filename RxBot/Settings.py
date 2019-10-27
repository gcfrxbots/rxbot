import os
import time
import argparse

try:
    import xlrd
    import xlsxwriter
    from system_hotkey import SystemHotkey, SystemRegisterError
except ImportError as e:
    print(e)
    raise ImportError(">>> One or more required packages are not properly installed! Run INSTALL_REQUIREMENTS.bat to fix!")

parser = argparse.ArgumentParser(description='Generate Settings File')
parser.add_argument('--g', dest="GenSettings", action="store_true")
parser.set_defaults(GenSettings=False)

GenSettings = (vars(parser.parse_args())["GenSettings"])

'''----------------------SETTINGS----------------------'''

'''FORMAT ---->   ("Option", "Default", "This is a description"), '''

defaultSettings = [
    ("PORT", 80, "Try 6667 if this doesn't work. Use 443, 6697 for SSL. Don't touch otherwise."),
    ("BOT OAUTH", "", "To get this Oauth, head to https://twitchapps.com/tmi/ and log in with YOUR BOT'S ACCOUNT!"),
    ("BOT NAME", "", "The twitch username of your bot (Lowercase)"),
    ("CHANNEL", "", "The twitch username of the channel you are connecting to (Lowercase)"),
    ("GPM ENABLE", "Yes", "Set to false if you don't have a Google Play Music subscription, or if you don't want to use it."),
    ("", "", ""),
    ("", "", "-------SONG REQUEST-------"),
    ("", "", ""),
    ("MAX DUPLICATE SONGS", 1, "This is the max amount of duplicate songs that can be in the queue. Leave 1 to only have one of each song in the queue at once."),
    ("MAX USER REQUESTS", 10, "This is the maximum amount of songs that a user may request. Ranks coming soon."),
    ("SHUFFLE ON START", "Yes", "This will automatically shuffle the contents of the backup playlist whenever you start the bot if set to True. Might delay startup a bit."),
    ("DELAY BETWEEN SONGS", 0.2, "Delay in seconds between a song ending and another starting."),
    ("VOL INCREMENT", 5, "This is how much the volume will be changed by when you type !volumeup, !volumedown, or use a hotkey to adjust volume."),
    ("MAX SONG LENGTH", 10, "The maximum song length in minutes. Songs longer than this duration won't be added to the queue."),
    ("YT IF NO RESULT", "Yes", "If no results are found searching Google Play Music, the bot will plug the same query into youtube and play the top result from there."),
    ("MEDIA FILES ENABLE", "Yes", "Toggle online media, such as a link directly to an .mp3 or .wav. This gives users more options for requests, but use with caution as people can request bad stuff."),
    ("QUEUE LINK", "The streamer has not set a queue link yet.", "Link to SongQueue.xlsx hosted online somewhere. Google Backup & Sync is recommended. This appears when someone types !queue."),
    ("DEFAULT SR MSG", "You need to type a song's name, or a link to a Youtube video or music file. You can type !wrongsong if the wrong one is selected.", "This is the message that will show up if someone types '!sr' or '!songrequest' without any request."),
    ("GPM PLAYLIST", "", "This is the exact title of the Google Play Music playlist that you want to use when updating your playlist in PlaylistEditor.py - If blank, you'll need to select a playlist each time."),
    ("", "", ""),
    ("", "", "-------TITLE BLACKLIST FILTER-------"),
    ("", "", ""),
    ("SONG BL SIZE", 8, "This is how many songs are loaded into the sorter and checked to see if they get affected by the blacklist. If you see 'Can't find this song' a lot, increase this a bit. 1 disables the filter."),
    ("BLACKLISTED TITLE CONTENTS", "live, remix, instrumental, nightcore, edit, mix, commentary", "Separate entries with commas. - The bot will make an effort to request add songs with these words in the title."),
    ("", "", ""),
    ("", "", "-------GENERAL-------"),
    ("", "", ""),
    ("MODERATORS", "rxbots", "Separate entries with commas. - Moderators of the BOT. Twitch channel mods are imported automatically."),
    ("ENABLE HOTKEYS", "No", "Turn on or off hotkeys. If this is true, you'll need to swap to the HOTKEYS worksheet at the bottom to configure them."),
]

listSettings = ["BLACKLISTED TITLE CONTENTS", "MODERATORS"]
listFloats = ["DELAY BETWEEN SONGS", "MAX SONG LENGTH"]
'''----------------------END SETTINGS----------------------'''

defaultHotkeys = [
    ("!togglepause", "f1", "No"),
    ("!veto", "f2", "No"),
    ("!clearsong", "control, f3", "Yes"),
    ("!vu", "f5", "No"),
    ("!vd", "f8", "No"),
]

def stopBot(err):
    print(">>>>>---------------------------------------------------------------------------<<<<<")
    print(err)
    print("A full explanation to this issue and how to fix it can be found in the readme.")
    print(">>>>>----------------------------------------------------------------------------<<<<<")
    time.sleep(3)
    quit()

def writeSettings(sheet, toWrite):
    row = 1  # WRITE SETTINGS
    col = 0
    for col0, col1, col2 in toWrite:
        sheet.write(row, col, col0)
        sheet.write(row, col + 1, col1)
        sheet.write(row, col + 2, col2)
        row += 1

def formatSettingsXlsx():
    try:
        with xlsxwriter.Workbook('../Config/Settings.xlsx') as workbook:  # FORMATTING
            worksheet = workbook.add_worksheet('Settings')
            format = workbook.add_format({'bold': True, 'center_across': True, 'font_color': 'white', 'bg_color': 'gray'})
            boldformat = workbook.add_format({'bold': True, 'center_across': True, 'font_color': 'white', 'bg_color': 'black'})
            lightformat = workbook.add_format({'bold': True, 'center_across': True, 'font_color': 'black', 'bg_color': '#DCDCDC', 'border': True})
            worksheet.set_column(0, 0, 25)
            worksheet.set_column(1, 1, 50)
            worksheet.set_column(2, 2, 130)
            worksheet.write(0, 0, "Option", format)
            worksheet.write(0, 1, "Your Setting", boldformat)
            worksheet.write(0, 2, "Description", format)
            worksheet.set_column('B:B', 50, lightformat)  # END FORMATTING

            writeSettings(worksheet, defaultSettings)

            # HOTKEYS WORKSHEET
            worksheet = workbook.add_worksheet('Hotkeys')
            worksheet.set_column(0, 0, 40)
            worksheet.set_column(1, 1, 60)
            worksheet.set_column(2, 2, 30)
            worksheet.write(0, 0, "Command", boldformat)
            worksheet.write(0, 1, "Key Combo", format)
            worksheet.write(0, 2, "Announce Response?", format)
            worksheet.set_column('B:B', 60, lightformat)  # END FORMATTING

            writeSettings(worksheet, defaultHotkeys)

        print("Settings.xlsx has been configured successfully.")
    except PermissionError:
        print("Can't open the settings file. Please close it and make sure it's not set to Read Only")

def reloadSettings(sheet):
    for item in settings:
        for i in enumerate(defaultSettings):
            if (i[1][0]) == item:  # Remove all 'list' elements from the string to feed it back into the speadsheet
                toRemove = ["'", '"', "[", "]", "\\", "/"]
                tempSetting = ''.join(c for c in str(settings[item]) if not c in toRemove)

                defaultSettings[i[0]] = (item, tempSetting, defaultSettings[i[0]][2])
    writeSettings(sheet, defaultSettings)

def readSettings(wb):
    settings = {}
    worksheet = wb.sheet_by_name("Settings")
    # Check if there's an update
    if worksheet.nrows != (len(defaultSettings)+1):
        reloadSettings(worksheet)

    for item in range(worksheet.nrows):
        if item == 0:
            pass
        else:
            option = worksheet.cell_value(item, 0)
            try:
                setting = int(worksheet.cell_value(item, 1))
            except ValueError:
                setting = str(worksheet.cell_value(item, 1))
                # Change "Yes" and "No" into bools, only for strings
                if setting.lower() == "yes":
                    setting = True
                elif setting.lower() == "no":
                    setting = False

            # Test if setting is a list
            if option in listSettings:
                setting = list(map(str.strip, setting.split(',')))
            if option in listFloats:
                setting = float(worksheet.cell_value(item, 1))

            settings[option] = setting
    return settings

def readHotkeys(wb):
    hotkeys = {}
    worksheet = wb.sheet_by_name("Hotkeys")

    for item in range(worksheet.nrows):
        if item == 0:
            pass
        else:
            option = worksheet.cell_value(item, 0)
            setting = list(map(str.strip, worksheet.cell_value(item, 1).split(',')))
            announce = worksheet.cell_value(item, 2)
            if announce.lower() == "yes":
                announce = True
            elif announce.lower() == "no":
                announce = False
            else:
                stopBot("Hotkeys config is configured wrong.")

            hotkeys[option] = (setting, announce)

    return hotkeys

def settingsSetup():
    global settings, hotkeys


    if not os.path.exists('../Config'):
        print("Creating a Config folder, check it out!")
        os.mkdir("../Config")

    if not os.path.exists('../Config/Settings.xlsx'):
        print("Creating Settings.xlsx")
        formatSettingsXlsx()
        print("\nPlease open Config / Settings.xlsx and configure the bot, then run it again.")
        print("Please read the readme to get everything set up!")
        time.sleep(3)
        quit()

    wb = xlrd.open_workbook('../Config/Settings.xlsx')
    # Read the settings file
    settings = readSettings(wb)
    hotkeys = readHotkeys(wb)

    # Check Settings
    if str(int(settings["PORT"])) not in ('80', '6667', '443', '6697'):  # Convert into non-float string
        stopBot("Wrong Port! The port must be 80 or 6667 for standard connections, or 443 or 6697 for SSL")
    if not settings['BOT OAUTH']:
        stopBot("Missing BOT OAUTH - Please follow directions in the settings or readme.")
    if not ('oauth:' in settings['BOT OAUTH']):
        stopBot("Invalid BOT OAUTH - Your oauth should start with 'oauth:'")
    if not settings['BOT NAME'] or not settings['CHANNEL']:
        stopBot("Missing BOT NAME or CHANNEL")

    print(">> Initial Checkup Complete! Connecting to Chat...")
    return settings, hotkeys


if GenSettings:
    if not os.path.exists('../Config'):
        os.mkdir("../Config")

    if not os.path.exists('../Config/Settings.xlsx'):
        print("Creating Settings.xlsx")
        formatSettingsXlsx()
        print("\nPlease open Config / Settings.xlsx and configure the bot, then run it again.")
        print("Please read the readme to get everything set up!")
        time.sleep(3)
        quit()
    else:
        print("Everything is already set up!")