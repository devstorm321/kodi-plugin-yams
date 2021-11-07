import xbmc, xbmcaddon, xbmcgui
import resources.modules.scraper as scraper
import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, requests
import json

try:
    from simplejson import loads as json_loads
except:
    print(('Plugin Error', 'simplejson import error: limited functionality'))
    pass

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
dev = []

def remove_device(user, passd,sess_id):
    request_dict = {
        'task': 'removedevice',
        'username': user,
        'password': passd,
        'session': sess_id
    }
    json_data = scraper.__get_json(request_dict)
    xbmc.log('remove device result: "%s"' % json_data)
    if json_data.get('status') == 'success':
        return True, json_data.get('reason', '')
    else:
        return False, json_data.get('reason', '')


for device in devices["boxes"]:
    if device["device_type"] == "box":
        ip = device["remote_addr"]

        appversion = device["App_Version"]
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
            dev.append(("{0}, {1}, {2}".format(ip,location,appversion)))
            k = 1
        elif k == 1:
            dev.append(("{0}, {1}, {2}".format(ip,location,appversion)))
            k = 2
        elif k == 2:
            dev.append(("{0}, {1}, {2}".format(ip,location,appversion)))
            k = 3
        elif k == 3:
            dev.append(("{0}, {1}, {2}".format(ip,location,appversion)))
            k = 4
        elif k == 4:
            dev.append(("{0}, {1}, {2}".format(ip,location,appversion)))
            k = 5
        elif k == 5:
            dev.append(("{0}, {1}, {2}".format(ip,location,appversion)))
            k = 6
        elif k == 6:
            dev.append(("{0}, {1}, {2}".format(ip,location,appversion)))
            k = 7
        elif k == 7:
            dev.append(("{0}, {1}, {2}".format(ip,location,appversion)))
            k = 8

for device in devices["mobiles"]:
    if device["device_type"] == "mobile":
        ip = device["remote_addr"]
        sessionid = device["session_id"]
        appversion = device["App_Version"]
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
            dev.append(("{0}, {1}, {2}".format(ip,location,appversion,)))
            k = 1
        elif k == 1:
            dev.append(("{0}, {1}, {2}".format(ip,location,appversion,)))
            k = 2
        elif k == 2:
            dev.append(("{0}, {1}, {2}".format(ip,location,appversion,)))
            k = 3
        elif k == 3:
            dev.append(("{0}, {1}, {2}".format(ip,location,appversion,)))
            k = 4
        elif k == 4:
            dev.append(("{0}, {1}, {2}".format(ip,location,appversion,)))
            k = 5
        elif k == 5:
            dev.append(("{0}, {1}, {2}".format(ip,location,appversion,)))
            k = 6


if k ==0 : dialog.ok("Active devices", ' No device active' )
else :
    dev_rem = dialog.contextmenu(dev)
