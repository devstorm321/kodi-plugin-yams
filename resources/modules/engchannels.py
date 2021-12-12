import json
import sys
import time
from urllib.request import urlopen

import xbmc
import xbmcgui
import xbmcplugin

try:
    from resources.modules import plugintools
except:
    xbmcgui.Dialog().ok('Import error', "Module plugintools not found!")

params = plugintools.get_params()

username = plugintools.get_setting('username')
password = plugintools.get_setting('password')
base = "https://astreamweb.com/kodi/web/iptv/m3u2json.php"
login_infos = "&username=" + username + "&password=" + password


# show_english_channels
def show_english_channels(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies2')
    url = base
    response = urlopen(url).read().decode('utf-8')
    json_data = json.loads(response)
    if len(json_data):
        for item in json_data:
            if item == '99. Adult Channels':
                plugintools.add_item(action="show_english_channels_items", url=item, title=item,
                                     page='True', folder=True)

            else:
                plugintools.add_item(action="show_english_channels_items", url=item, title=item,
                                     page='False', folder=True)

    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


# show_english_channels_items
def show_english_channels_items(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    is_for_adult = params.get('page')
    category_id = params.get('url')
    if is_for_adult == 'True':
        title = "Please type Family Safe Password."
        keyboard = xbmcgui.Dialog()
        adult_pword = keyboard.numeric(0, title, "")
        if adult_pword == '':
            return
        xbmc.log('Getting current password')
        response = urlopen("https://astreamweb.com/kodi/passcode.txt").read().decode('utf-8')

        if str(adult_pword) != response.strip():
            dialog = xbmcgui.Dialog()
            dialog.ok('Unlock error', "Bad Password")
            return False
    url = base
    response = urlopen(url).read().decode('utf-8')
    json_data = json.loads(response)
    if len(json_data):
        for item in json_data[category_id]:
            label = item["tvg-name"]
            url = item["chlink1"] + login_infos + item["chlink3"]
            xbmc.log('url {}'.format(url))
            iconImage = item["tvg-logo"]
            plugintools.add_item(action="play_vod", url=url, title=label, thumbnail=iconImage,
                                 page='True', isPlayable=True, folder=False)

    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


def play_vod(params):
    urllink = params.get("url")
    plugintools.play_resolved_url(urllink)
    time.sleep(3)
    if not xbmc.Player().isPlaying():
        xbmc.executebuiltin('Notification(Channel Unavailable at this moment,10000)')
