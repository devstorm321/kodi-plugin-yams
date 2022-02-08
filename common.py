import os
import sys
import urllib.request
import urllib.parse
import urllib.error
import xbmc, xbmcaddon, xbmcgui, xbmcplugin, xbmcvfs
import requests

try:
    from simplejson import loads as json_loads
except:
    print(('Plugin Error', 'simplejson import error: limited functionality'))
    pass


# import common
ADDON_ID = 'plugin.video.yams'
try:
    ADDON_HANDLE = int(sys.argv[1])
except:
    ADDON_HANDLE = 0

settings = xbmcaddon.Addon(id=ADDON_ID)


def get_device_info(device):
    ip = device["remote_addr"]
    sessionid = device["session_id"]
    appversion = device["App_Version"]
    headers = {"authorization": "Basic MTI0OTU4Om5aMm1EV0M0aFBvTVpUS08=",
               "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"}
    url = "https://geoip.maxmind.com/geoip/v2.1/city/{0}".format(ip)

    georesp = requests.get(url, headers=headers)
    georesp = json_loads(georesp.text)
    if georesp["city"]["names"]["en"] != "":
        location = georesp["city"]["names"]["en"]
    elif georesp["country"]["names"]["en"] != "":
        location = georesp["country"]["names"]["en"]
    return ip, sessionid, appversion, location


def auth_check():
    username = settings.getSetting(id="username")
    password = settings.getSetting(id="password")

    if username == "" or username is None:
        xbmcgui.Dialog().ok("Oops", "Sorry Username is invalid/compulsory")
        sys.exit(0)

    if password == "" or password is None:
        xbmcgui.Dialog().ok("Oops", "Sorry Password is invalid/compulsory")
        sys.exit(0)

    return username, password


def http_request(url):
    req = urllib.request.Request(url)
    req.add_header('User-Agent',
                   'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36')
    return urllib.request.urlopen(req)
