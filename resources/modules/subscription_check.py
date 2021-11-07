import urllib.request, urllib.error, urllib.parse
import json
import xbmc, xbmcaddon, xbmcgui, xbmcvfs
from . import scraper
import traceback
import os

def setSubscriptionButton(username):
    try:
        path = xbmcvfs.translatePath(os.path.join('special://home/userdata', '')).encode('unicode_escape')
        url = "https://yamshost.org/amember/api/check-access/by-login?_key=HODzCPbEpwmz4ufir2jimobile&login=%s" % username
        response = urllib.request.urlopen(url).read()
        jsonResp = json.loads(response)
        print((jsonResp, "BBBBBBBBBB"))
        categories = jsonResp["categories"]
        categories = [int(a) for a in list(jsonResp["categories"].keys())]
        category = ""
        print(categories)
        if 2 in categories: # basic cat
            category = "Basic"
            xbmc.executebuiltin('Skin.SetBool(HomeMenuNoBasicButton)')
            xbmc.executebuiltin('Skin.Reset(%s)' % 'HomeMenuNoStandardButton')
            xbmc.executebuiltin('Skin.Reset(%s)' % 'HomeMenuNoPremiumButton')
        if 12 in categories: # standard cat
            xbmc.executebuiltin('Skin.SetBool(HomeMenuNoStandardButton)')
            xbmc.executebuiltin('Skin.Reset(%s)' % 'HomeMenuNoBasicButton')
            xbmc.executebuiltin('Skin.Reset(%s)' % 'HomeMenuNoPremiumButton')
            category = "Standard"
        if 125 in categories: # premium cat
            category = "Premium"
            xbmc.executebuiltin('Skin.SetBool(HomeMenuNoPremiumButton)')
            xbmc.executebuiltin('Skin.Reset(%s)' % 'HomeMenuNoBasicButton')
            xbmc.executebuiltin('Skin.Reset(%s)' % 'HomeMenuNoStandardButton')
        print(category)
        try:
            catFile = open(os.path.join(path, "astream.category"), 'r')
            oldCategory = catFile.read()
            catFile.close()
        except:
            oldCategory = ""
        if not category in oldCategory:
            skin_update(category)
        xbmc.executebuiltin('Skin.SetString(subs, %s)' % category)
        catFile = open(os.path.join(path, "astream.category"), 'w')
        catFile.write(category)
        catFile.close()
    except Exception as e:
        print('>>> traceback <<<')
        traceback.print_exc()
        print('>>> end of traceback <<<')
        pass

def skin_update(category):
    dialog = xbmcgui.Dialog()
    dialog.ok('Notice', "Due to a change of your subscription, we are updating the skin to be accustomed to subscription level: %s" % category)
    # selecting skin Languages
    __settings__   = xbmcaddon.Addon(id='plugin.video.yams')
    langs = __settings__.getSetting('channellanguage').lower()
    config1 = "https://astreamweb.com/kodi/skin/{0}/skin.estuary-mainmenu.DATA.xml".format(langs.lower())
    config2 = "https://astreamweb.com/kodi/skin/{0}/skin.estuary-videosubmenu.DATA.xml".format(langs.lower())
    path = xbmcvfs.translatePath(os.path.join('special://home/userdata/addon_data/script.skinshortcuts/', '')).encode('unicode_escape')
    settingsFile1 = os.path.join(path, 'mainmenu.DATA.xml')
    settingsFile2 = os.path.join(path, 'videosubmenu.DATA.xml')
    if not os.path.exists(path):
        os.mkdir(path)
    scraper._downloadOverride(config1, settingsFile1)
    scraper._downloadOverride(config2, settingsFile2)
    xbmc.executebuiltin('UnloadSkin()')
    xbmc.executebuiltin('ReloadSkin()')
    xbmc.executebuiltin("XBMC.ActivateWindow(Home)")
