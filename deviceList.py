import xbmc, xbmcaddon, xbmcgui
import resources.modules.scraper as scraper
import requests
import sys

try:
    from simplejson import loads as json_loads
except:
    print(('Plugin Error', 'simplejson import error: limited functionality'))
    pass

from common import get_device_info


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
dev = []


def remove_device(user, passd, sess_id):
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
        ip, location, appversion, sessionid = get_device_info(device)
        if k == 0:
            dev.append(("{0}, {1}, {2},{3}".format(ip, location, appversion, sessionid)))
            k = 1
        elif k == 1:
            dev.append(("{0}, {1}, {2},{3}".format(ip, location, appversion, sessionid)))
            k = 2
        elif k == 2:
            dev.append(("{0}, {1}, {2},{3}".format(ip, location, appversion, sessionid)))
            k = 3
        elif k == 3:
            dev.append(("{0}, {1}, {2},{3}".format(ip, location, appversion, sessionid)))
            k = 4
        elif k == 4:
            dev.append(("{0}, {1}, {2},{3}".format(ip, location, appversion, sessionid)))
            k = 5
        elif k == 5:
            dev.append(("{0}, {1}, {2},{3}".format(ip, location, appversion, sessionid)))
            k = 6
        elif k == 6:
            dev.append(("{0}, {1}, {2},{3}".format(ip, location, appversion, sessionid)))
            k = 7
        elif k == 7:
            dev.append(("{0}, {1}, {2},{3}".format(ip, location, appversion, sessionid)))
            k = 8

for device in devices["mobiles"]:
    if device["device_type"] == "mobile":
        ip, location, appversion, sessionid = get_device_info(device)

        if k == 0:
            dev.append(("{0}, {1}, {2},{3}".format(ip, location, appversion, sessionid)))
            k = 1
        elif k == 1:
            dev.append(("{0}, {1}, {2},{3}".format(ip, location, appversion, sessionid)))
            k = 2
        elif k == 2:
            dev.append(("{0}, {1}, {2},{3}".format(ip, location, appversion, sessionid)))
            k = 3
        elif k == 3:
            dev.append(("{0}, {1}, {2},{3}".format(ip, location, appversion, sessionid)))
            k = 4
        elif k == 4:
            dev.append(("{0}, {1}, {2},{3}".format(ip, location, appversion, sessionid)))
            k = 5
        elif k == 5:
            dev.append(("{0}, {1}, {2},{3}".format(ip, location, appversion, sessionid)))
            k = 6

if k == 0:
    dialog.ok("Active devices", ' No device active')
else:
    dev_rem = dialog.multiselect("Select the devices you want to remove ", dev)
    if dev_rem is not None:
        if dev_rem != 0:
            for i in dev_rem:
                xbmc.log('remove device result: %s' % dev[i], xbmc.LOGINFO)
                rem_conf = dialog.yesno("Please confirm you want to remove {}.".format(dev[i].split(',')[2]),
                                        "Re-adding this device will cost you 5USD.")
                if rem_conf:
                    rem_suc, rem_rea = remove_device(username, password, dev[i].split(',')[1].replace(' ', ''))
                    if rem_suc:
                        dialog.ok('Remove device success', rem_rea)
                    else:
                        dialog.ok('Remove device not success', rem_rea)
