import xbmc, xbmcaddon, xbmcgui
import resources.modules.scraper as scraper
import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse
import json,requests

import sys

try:
    from simplejson import loads as json_loads
except:
    print(('Plugin Error', 'simplejson import error: limited functionality'))
    pass

dialog = xbmcgui.Dialog()
# Ideally do not use username & password when there is a valid session to kill
# But cannot guarantee valid session
__settings__ = xbmcaddon.Addon(id='plugin.video.yams')
username = __settings__.getSetting(id="username")
password = __settings__.getSetting(id="password")

if username == "" or username is None:
    dialog.ok("Oops", "Sorry Username is invalid/compulsory")
    sys.exit(0)

if password == "" or password is None:
    dialog.ok("Oops", "Sorry Password is invalid/compulsory")
    sys.exit(0)

devices = scraper.__get_json({"task": "devicelist", "username": username})
first = ""
second = ""
third = ""
k = 0
dialog = xbmcgui.Dialog()
xbmc.log(' devices {}'.format(devices))
for device in devices["mobiles"]:
    if device["device_type"] == "mobile":
        ip = device["remote_addr"]
        headers = {"authorization": "Basic MTI0OTU4Om5aMm1EV0M0aFBvTVpUS08=",
           "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"}
        url = "https://geoip.maxmind.com/geoip/v2.1/city/{0}".format(ip)

        georesp = requests.get(url,headers=headers)
        georesp = json_loads(georesp.text)
        if georesp["city"]["names"]["en"] != "":
            location = georesp["city"]["names"]["en"]
        elif georesp["country"]["names"]["en"] != "":
            location = georesp["country"]["names"]["en"]
        if k == 0:
            first = "{0} {1}".format(ip, location)
            k = 1
        elif k == 1:
            second = "{0} {1}".format(ip, location)
            k = 2
        elif k == 2:
            third = "{0} {1}".format(ip, location)
            k = 3
if k ==0 : dialog.ok("Active mobile devices", ' No mobile device active' )
else : dialog.ok("Active mobile devices", first, second, third)
