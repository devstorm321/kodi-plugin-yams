import sys
import xbmc, xbmcaddon, xbmcgui
import resources.modules.scraper as scraper

dialog = xbmcgui.Dialog()
__settings__ = xbmcaddon.Addon(id="plugin.video.yams")

username = __settings__.getSetting(id="username")
password = __settings__.getSetting(id="password")
session = __settings__.getSetting(id="session")

# digest = ''
# digest = yamsutils.__digest(ADDON_PATH)
digest = "0860588e3a23f9637ea47c3dc314a63185515d29bf7c839612a9e88ce596847b"

scraper.__set_digest(digest)

if username == "" or username is None:
    dialog.ok("Oops", "Sorry Username is invalid/compulsory")
    sys.exit(0)

if password == "" or password is None:
    dialog.ok("Oops", "Sorry Password is invalid/compulsory")
    sys.exit(0)

if dialog.yesno("Day Pass", "Would you like to activate day pass for 1 day"):
    bypass = scraper.get5DayBypass(username, password)

    if bypass["success"]:
        dialog.ok("Success", f'''You are using {bypass["bypasses"]} out of 20 day pass''')
        dialog.ok("Restart Required",
                  "Please restart your device for day pass to take effect (shutdown icon -> exit)")
        xbmc.executebuiltin("XBMC.ActivateWindow(Home)")
    else:
        dialog.ok("Failure", bypass["reason"])
        xbmc.executebuiltin("XBMC.ActivateWindow(Home)")
