__author__ = 'clearkruti'
import logging
import xbmc,xbmcgui,xbmcaddon

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
    xbmc.executebuiltin("WindowClose()")
    xbmc.executebuiltin("ActivateWindow(Home)")

if password == "" or password is None:
    dialog.ok("Oops", "Sorry Password is invalid/compulsory")
    xbmc.executebuiltin("WindowClose()")
    xbmc.executebuiltin("ActivateWindow(Home)")

scraper.delete_sessions(username, password)
xbmc.executebuiltin("XBMC.ActivateWindow(Home)")
