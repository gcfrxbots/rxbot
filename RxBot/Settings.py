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
    ("PORT", 80, "Try 6667 if this doesn't work. Use 443 or 6697 for SSL. Don't touch otherwise."),
    ("BOT OAUTH", "", "To get this oauth code, head here and log in with YOUR BOT'S account: https://twitchapps.com/tmi/"),
    ("BOT NAME", "", "Your bot's Twitch username, all lowercase."),
    ("CHANNEL", "", "Your Twitch username, all lowercase."),
    ("GPM ENABLE", "Yes", "MUST be set to 'No' if you do not plan on using RXBot's Google Play Music functionality."),
    ("", "", ""),
    ("", "", "-------SONG REQUEST-------"),
    ("", "", ""),
    ("MAX DUPLICATE SONGS", 1, "If a song is already in the queue this many times, it cannot be requested again. Most users will want this set to 1."),
    ("MAX USER REQUESTS", 10, "If a user already has this many requests in the queue, they cannot request another one at that time."),
    ("SHUFFLE ON START", "Yes", "If enabled, your backup playlist will automatically shuffle itself every time you run RXBot."),
    ("DELAY BETWEEN SONGS", 0.2, "The delay, in seconds, between one song ending and the next song starting."),
    ("VOL INCREMENT", 5, "If a value is not specified, volume commands will adjust the bot's music volume by this increment."),
    ("MAX SONG LENGTH", 10, "Songs longer than this many minutes can not be requested."),
    ("YT IF NO RESULT", "Yes", "If a user requests a song, and no results are found on Google Play Music, the bot will play the top result from YouTube instead."),
    ("MEDIA FILES ENABLE", "Yes", "Allows users to request songs using direct file links. Enabling this gives users more options, but can also be abused."),
    ("QUEUE LINK", "The streamer has not set a queue link yet.", "If you've uploaded your SongQueue.xlsx file for viewers to see with !queue, this is where you put the link to it. More info in the setup guide."),
    ("DEFAULT SR MSG", "You need to type a song's name, or a link to a Youtube video or music file. You can type !wrongsong if the wrong one is selected.", "This message will show up in the chat if someone types '!sr' or '!songrequest' without any request."),
    ("GPM PLAYLISTS", "", "Separate with commas. The EXACT title of the Google Play Music playlist(s) that you want to import, either with the playlist editor or the auto-update setting below."),
    ("UPDATE PL ON START", "No", "The playlist you entered into the setting above will automatically update every time you start the bot. Noticeably slows bot startup time."),
    ("YT VOL RESET", "No", "If the volume is changed while a Youtube song is playing, this will change the volume back to what it was before once the song is over."),
    ("", "", ""),
    ("", "", "-------TITLE BLACKLIST FILTER-------"),
    ("", "", ""),
    ("SONG BL SIZE", 8, "How many songs are loaded into the sorter before the blacklist filters them. If you see 'Can't find this song' a lot, increase this a bit. Set to 1 to disable."),
    ("BLACKLISTED TITLE CONTENTS", "live,remix,instrumental,nightcore,edit,mix,commentary", "Separate terms with commas. Songs with a blacklisted term in the title will be filtered out, unless said term was actually included in the request itself."),
    ("", "", ""),
    ("", "", "-------GENERAL-------"),
    ("", "", ""),
    ("MODERATORS", "rxbots", "Separate entries with commas. These are moderators of the BOT, not your Twitch channel. Channel mods are imported automatically."),
    ("ENABLE HOTKEYS", "No", "Turn hotkeys on or off. If this is set to 'Yes', you'll need to swap to the HOTKEYS worksheet at the bottom to configure them."),
]

listSettings = ["BLACKLISTED TITLE CONTENTS", "MODERATORS", "GPM PLAYLISTS"]
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
    print("More info can be found here: https://rxbots.net/rxbot-settings.html")
    print(">>>>>----------------------------------------------------------------------------<<<<<")
    time.sleep(3)
    quit()

def deformatEntry(inp):
    if isinstance(inp, list):
        toRemove = ["'", '"', "[", "]", "\\", "/"]
        return ''.join(c for c in str(inp) if not c in toRemove)

    elif isinstance(inp, bool):
        if inp:
            return "Yes"
        else:
            return "No"

    else:
        return inp

def writeSettings(sheet, toWrite):

    row = 1  # WRITE SETTINGS
    col = 0
    for col0, col1, col2 in toWrite:
        sheet.write(row, col, col0)
        sheet.write(row, col + 1, col1)
        sheet.write(row, col + 2, col2)
        row += 1

class settingsConfig:
    def __init__(self):
        self.defaultSettings = defaultSettings
        self.defaultHotkeys = defaultHotkeys

    def formatSettingsXlsx(self):
        try:
            with xlsxwriter.Workbook('../Config/Settings.xlsx') as workbook:
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

                writeSettings(worksheet, self.defaultSettings)

                worksheet = workbook.add_worksheet('Hotkeys')
                worksheet.set_column(0, 0, 40)
                worksheet.set_column(1, 1, 60)
                worksheet.set_column(2, 2, 30)
                worksheet.write(0, 0, "Command", boldformat)
                worksheet.write(0, 1, "Key Combo", format)
                worksheet.write(0, 2, "Announce Response?", format)
                worksheet.set_column('B:B', 60, lightformat)  # END FORMATTING

                writeSettings(worksheet, self.defaultHotkeys)

        except PermissionError:
            stopBot("Can't open the Settings file. Please close it and make sure it's not set to Read Only.")
        except:
            stopBot("Can't open the Settings file. Please close it and make sure it's not set to Read Only. [0]")

    def reloadSettings(self, tmpSettings):
        for item in tmpSettings:
            for i in enumerate(defaultSettings):
                if (i[1][0]) == item:  # Remove all 'list' elements from the string to feed it back into the speadsheet
                    defaultSettings[i[0]] = (item, deformatEntry(tmpSettings[item]), defaultSettings[i[0]][2])
        # Reformat default hotkeys to be the user's hotkeys
        self.defaultHotkeys = []
        for item in hotkeys:
            self.defaultHotkeys.append((item, deformatEntry(hotkeys[item][0]), deformatEntry(hotkeys[item][1])))

        self.formatSettingsXlsx()

    def readSettings(self, wb):
        settings = {}
        worksheet = wb.sheet_by_name("Settings")

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

        if worksheet.nrows != (len(defaultSettings) + 1):
            self.reloadSettings(settings)
            stopBot("The settings have been changed with an update! Please check your Settings.xlsx file then restart the bot.")
        return settings

    def readHotkeys(self, wb):
        hotkeys = {}
        worksheet = wb.sheet_by_name("Hotkeys")

        for item in range(worksheet.nrows):
            if item == 0:
                pass
            else:
                option = worksheet.cell_value(item, 0)

                key = worksheet.cell_value(item, 1)
                if isinstance(key, int) or isinstance(key, float):
                    key = str(int(key))

                setting = list(map(str.strip, key.split(',')))
                announce = worksheet.cell_value(item, 2)
                if announce.lower() == "yes":
                    announce = True
                elif announce.lower() == "no":
                    announce = False
                else:
                    stopBot("Hotkeys config is configured wrong.")

                hotkeys[option] = (setting, announce)

        return hotkeys

    def settingsSetup(self):
        global settings, hotkeys

        if not os.path.exists('../Config'):
            print("Creating a Config folder, check it out!")
            os.mkdir("../Config")

        if not os.path.exists('../Config/Settings.xlsx'):
            print("Creating Settings.xlsx")
            self.formatSettingsXlsx()
            stopBot("Please open Config / Settings.xlsx and configure the bot, then run it again.")

        wb = xlrd.open_workbook('../Config/Settings.xlsx')
        # Read the settings file
        hotkeys = self.readHotkeys(wb)
        settings = self.readSettings(wb)



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
        settingsConfig.formatSettingsXlsx(settingsConfig())
        print("\nPlease open Config / Settings.xlsx and configure the bot, then run it again.")
        print("Please read the readme to get everything set up!")
        time.sleep(3)
        quit()
    else:
        print("Everything is already set up!")
