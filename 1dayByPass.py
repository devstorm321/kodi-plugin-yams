import sys
import xbmc
import xbmcgui
import resources.modules.scraper as scraper

from common import auth_check

# digest = yamsutils.__digest(ADDON_PATH)
digest = "0860588e3a23f9637ea47c3dc314a63185515d29bf7c839612a9e88ce596847b"

scraper.__set_digest(digest)

username, password = auth_check()

if xbmcgui.Dialog().yesno("Day Pass", "Would you like to activate day pass for 1 day"):
    bypass = scraper.get5DayBypass(username, password)

    if bypass["success"]:
        xbmcgui.Dialog().ok("Success", f'''You are using {bypass["bypasses"]} out of 20 day pass''')
        xbmcgui.Dialog().ok("Restart Required",
                  "Please restart your device for day pass to take effect (shutdown icon -> exit)")
        xbmc.executebuiltin("XBMC.ActivateWindow(Home)")
    else:
        xbmcgui.Dialog().ok("Failure", bypass["reason"])
        xbmc.executebuiltin("XBMC.ActivateWindow(Home)")
