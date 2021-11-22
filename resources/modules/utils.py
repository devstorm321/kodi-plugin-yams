import datetime as dt
import os
import requests

import xbmc
import xbmcgui


def log(text):
    print((dt.datetime.now(), 'AstreamWeb : {}'.format(text)))


class ApiError(Exception):
    def __init__(self, exception):
        self.exception = exception

    def __str__(self):
        return self.exception


def killXbmc():
    platform = queryPlatform()

    if platform == 'OSX':
        try:
            os.system('killall -9 XBMC')
        except:
            pass

        try:
            os.system('killall -9 Kodi')
        except:
            pass
    elif platform == 'AppleTV':
        try:
            os.system('killall AppleTV')
        except:
            pass

        try:
            os.system('sudo initctl stop kodi')
        except:
            pass

        try:
            os.system('sudo initctl stop xbmc')
        except:
            pass
    elif platform == 'Linux':
        try:
            os.system('killall XBMC')
        except:
            pass

        try:
            os.system('killall Kodi')
        except:
            pass

        try:
            os.system('killall -9 xbmc.bin')
        except:
            pass

        try:
            os.system('killall -9 kodi.bin')
        except:
            pass
    #    elif (platform == 'Android'):
    #        try:
    #            os.system('adb shell am force-stop org.xbmc.kodi')
    #        except:
    #            pass
    #
    #        try:
    #            os.system('adb shell am force-stop org.kodi')
    #        except:
    #            pass
    #
    #        try:
    #            os.system('adb shell am force-stop org.xbmc.xbmc')
    #        except:
    #            pass
    #
    #        try:
    #            os.system('adb shell am force-stop org.xbmc')
    #        except:
    #            pass
    elif platform == 'Windows':
        try:
            os.system('@ECHO off')
            os.system('tskill XBMC.exe')
        except:
            pass

        try:
            os.system('@ECHO off')
            os.system('tskill Kodi.exe')
        except:
            pass

        try:
            os.system('@ECHO off')
            os.system('TASKKILL /im XBMC.exe /f')
        except:
            pass

        try:
            os.system('@ECHO off')
            os.system('TASKKILL /im Kodi.exe /f')
        except:
            pass
    else:
        dialog = xbmcgui.Dialog()
        dialog.ok('AstreamWeb Maintenance', 'Please pull the power cable from your device.')


def queryPlatform():
    if xbmc.getCondVisibility('system.platform.osx'):
        return 'OSX'
    elif xbmc.getCondVisibility('system.platform.atv2'):
        return 'AppleTV'
    elif xbmc.getCondVisibility('system.platform.linux'):
        return 'Linux'
    elif xbmc.getCondVisibility('system.platform.android'):
        return 'Android'
    elif xbmc.getCondVisibility('system.platform.windows'):
        return 'Windows'
    else:
        return 'Other'


def postHtml(url, form_data={}, headers={}, compression=True, NoCookie=None):
    try:
        _user_agent = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.1 ' + \
                      '(KHTML, like Gecko) Chrome/13.0.782.99 Safari/535.1'
        headers['User-Agent'] = _user_agent
        if compression:
            headers['Accept-Encoding'] = 'gzip'
        resp = requests.request('POST', url=url, headers=headers, data=form_data)
        data = resp.content
        resp.close()
    except Exception as e:
        if 'SSL23_GET_SERVER_HELLO' in str(e):
            # notify('Oh oh','Python version to old - update to Krypton or FTMC')
            raise requests.HTTPError()
        else:
            # notify('Oh oh','It looks like this website is down.')
            raise requests.HTTPError()
        return None
    return data
