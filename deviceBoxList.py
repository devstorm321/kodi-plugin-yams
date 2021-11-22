import xbmc, xbmcaddon, xbmcgui
import resources.modules.scraper as scraper
from common import auth_check, get_device_info


username, password = auth_check()

devices = scraper.__get_json({"task": "devicelist", "username": username})
first = ""
second = ""
third = ""
k = 0

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
        ip, session_id, appversion, location = get_device_info()
        if k == 0:
            dev.append(("{0}, {1}, {2}".format(ip, location, appversion)))
            k = 1
        elif k == 1:
            dev.append(("{0}, {1}, {2}".format(ip, location, appversion)))
            k = 2
        elif k == 2:
            dev.append(("{0}, {1}, {2}".format(ip, location, appversion)))
            k = 3
        elif k == 3:
            dev.append(("{0}, {1}, {2}".format(ip, location, appversion)))
            k = 4
        elif k == 4:
            dev.append(("{0}, {1}, {2}".format(ip, location, appversion)))
            k = 5
        elif k == 5:
            dev.append(("{0}, {1}, {2}".format(ip, location, appversion)))
            k = 6
        elif k == 6:
            dev.append(("{0}, {1}, {2}".format(ip, location, appversion)))
            k = 7
        elif k == 7:
            dev.append(("{0}, {1}, {2}".format(ip, location, appversion)))
            k = 8

for device in devices["mobiles"]:
    if device["device_type"] == "mobile":
        ip, session_id, appversion, location = get_device_info()
        if k == 0:
            dev.append(("{0}, {1}, {2}".format(ip, location, appversion, )))
            k = 1
        elif k == 1:
            dev.append(("{0}, {1}, {2}".format(ip, location, appversion, )))
            k = 2
        elif k == 2:
            dev.append(("{0}, {1}, {2}".format(ip, location, appversion, )))
            k = 3
        elif k == 3:
            dev.append(("{0}, {1}, {2}".format(ip, location, appversion, )))
            k = 4
        elif k == 4:
            dev.append(("{0}, {1}, {2}".format(ip, location, appversion, )))
            k = 5
        elif k == 5:
            dev.append(("{0}, {1}, {2}".format(ip, location, appversion, )))
            k = 6

if k == 0:
    xbmcgui.Dialog().ok("Active devices", ' No device active')
else:
    dev_rem = xbmcgui.Dialog().contextmenu(dev)
