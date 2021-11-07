__author__ =  "enc0der"

import sys
import logging
import xbmc, xbmcaddon, xbmcgui
import resources.modules.scraper as scraper
import datetime

logger = logging

dialog = xbmcgui.Dialog()
__settings__ = xbmcaddon.Addon(id="plugin.video.yams")

username = __settings__.getSetting(id="username")
password = __settings__.getSetting(id="password")
session = __settings__.getSetting(id="session")

#digest = ''
#digest = yamsutils.__digest(ADDON_PATH)
digest = "bb33deceb9c51ab1fcf38ad78b4b1e835230285a857d8a99bd9dfd7373247ad7"

scraper.__set_digest(digest)

if username == "" or username is None:
    dialog.ok("Oops", "Sorry Username is invalid/compulsory")
    sys.exit(0)

if password == "" or password is None:
    dialog.ok("Oops", "Sorry Password is invalid/compulsory")
    sys.exit(0)

bypass = scraper.getBypassActive(username)
print(bypass)
if bypass["active"]:
    untilDate = bypass["untilDate"].split(" ")[0]
    today = datetime.date.today()
    expiredates = untilDate.split("-")
    expire = datetime.date(int(expiredates[0]), int(expiredates[1]), int(expiredates[2]))
    days = expire - today
    dialog.ok("Success", "You have {0} days left on your anti-sharing bypass".format(days.days))
else:
    dialog.ok("Failure", "Your anti-sharing bypass isn't active")
