__author__ =  "enc0der"

import sys
import logging
import xbmcgui
import resources.modules.scraper as scraper
import datetime
from common import auth_check

logger = logging

#digest = yamsutils.__digest(ADDON_PATH)
digest = "bb33deceb9c51ab1fcf38ad78b4b1e835230285a857d8a99bd9dfd7373247ad7"

scraper.__set_digest(digest)

username, = auth_check()

bypass = scraper.getBypassActive(username)

if bypass["active"]:
    untilDate = bypass["untilDate"].split(" ")[0]
    today = datetime.date.today()
    expiredates = untilDate.split("-")
    expire = datetime.date(int(expiredates[0]), int(expiredates[1]), int(expiredates[2]))
    days = expire - today
    xbmcgui.Dialog().ok("Success", "You have {0} days left on your anti-sharing bypass".format(days.days))
else:
    xbmcgui.Dialog().ok("Failure", "Your anti-sharing bypass isn't active")
