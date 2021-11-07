__author__ = 'clearkruti'
import sys
import logging
import xbmc, xbmcgui,xbmcaddon
import resources.modules.scraper as scraper

logger = logging

dialog = xbmcgui.Dialog()
__settings__ = xbmcaddon.Addon(id='plugin.video.yams')

# Ideally do not use username & password when there is a valid session to kill
# But cannot guarantee valid session
username = __settings__.getSetting(id="username")
password = __settings__.getSetting(id="password")
session = __settings__.getSetting(id="session")

if username == "" or username is None:
    dialog.ok("Oops", "Sorry Username is invalid/compulsory")
    sys.exit(0)

if password == "" or password is None:
    dialog.ok("Oops", "Sorry Password is invalid/compulsory")
    sys.exit(0)

# Unused
# if session == "" or session is None:
#     dialog.ok("Oops", "Sorry Current Session is invalid/compulsory")
#     sys.exit(0)

if dialog.yesno('Kill Session', 'Kill all sessions?'):
    success, message = scraper.delete_sessions(username, password)
    if success:
        dialog.ok("Done", message)
    else:
        dialog.ok("Failed", message)
