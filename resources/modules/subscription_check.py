import json
import os
import traceback
import urllib.error
import urllib.parse
import urllib.request

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

from . import scraper


def setSubscriptionButton(username):
    try:
        path = xbmcvfs.translatePath(os.path.join('special://home/userdata', ''))
        url = f"https://yamshost.org/amember/api/check-access/by-login?_key=HODzCPbEpwmz4ufir2jimobile&login={username}"
        response = urllib.request.urlopen(url).read().decode('utf-8')
        jsonResp = json.loads(response)

        categories = [int(a) for a in list(jsonResp["categories"].keys())]
        category = ""
        print(categories)
        if 2 in categories:  # basic cat
            category = "Basic"
            xbmc.executebuiltin('Skin.SetBool(HomeMenuNoBasicButton)')
            xbmc.executebuiltin('Skin.Reset(%s)' % 'HomeMenuNoStandardButton')
            xbmc.executebuiltin('Skin.Reset(%s)' % 'HomeMenuNoPremiumButton')
        if 12 in categories:  # standard cat
            xbmc.executebuiltin('Skin.SetBool(HomeMenuNoStandardButton)')
            xbmc.executebuiltin('Skin.Reset(%s)' % 'HomeMenuNoBasicButton')
            xbmc.executebuiltin('Skin.Reset(%s)' % 'HomeMenuNoPremiumButton')
            category = "Standard"
        if 125 in categories:  # premium cat
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
    dialog.ok('Notice',
              f"Due to a change of your subscription, we are updating the skin to be accustomed to subscription level: {category}")
    # selecting skin Languages
    __settings__ = xbmcaddon.Addon(id='plugin.video.yams')
    langs = __settings__.getSetting('channellanguage').lower()
    mainmenu_config = "https://astreamweb.com/kodi/skin/{0}/skin.estuary-mainmenu.DATA.xml".format(langs.lower())
    videosubmenu_config = "https://astreamweb.com/kodi/skin/{0}/skin.estuary-videosubmenu.DATA.xml".format(langs.lower())
    path = xbmcvfs.translatePath(os.path.join('special://home/userdata/addon_data/script.skinshortcuts/', ''))
    settingsFile1 = os.path.join(path, 'mainmenu.DATA.xml')
    settingsFile2 = os.path.join(path, 'videosubmenu.DATA.xml')
    if not os.path.exists(path):
        os.mkdir(path)
    scraper._downloadOverride(mainmenu_config, settingsFile1)
    scraper._downloadOverride(videosubmenu_config, settingsFile2)
    xbmc.executebuiltin('UnloadSkin()')
    xbmc.executebuiltin('ReloadSkin()')
    xbmc.executebuiltin("XBMC.ActivateWindow(Home)")
