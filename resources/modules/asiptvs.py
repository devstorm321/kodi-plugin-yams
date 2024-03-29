import json
import sys
import time
from string import ascii_lowercase

import xbmc
import xbmcgui
import xbmcplugin

from . import plugintools
from common import http_request

params = plugintools.get_params()
__get_icon = plugintools.__get_icon
per_page = plugintools.get_setting('per_page')

username = plugintools.get_setting('username')
password = plugintools.get_setting('password')
base = "http://iptv-line.com:8080/player_api.php"
stream_url = "https://api.yamsonline.com/iptv/connect?username=" + username + "&format=stream1&provider=1&password=" + password + "&id="
stream_url1 = "https://api.yamsonline.com/iptv/connect?username=" + username + "&format=vod1&provider=1&password=" + password + "&id="
login_infos = "username=quarantine&password=I5iuxBk5zA"
NOVELAS_CATEGORY_ID = '117'


# ('/asiptvs_vod/')
def asiptvs_vod():
    url = base + "?" + login_infos + "&action=get_vod_categories"
    response = http_request(url).read().decode('utf-8')
    json_data = json.loads(response)
    if len(json_data):
        items = sorted(json_data, key=lambda k: k["category_name"], reverse=False)
        for item in items:
            plugintools.add_item(action='asiptvs_vod_videos', title=item["category_name"], url=item["category_id"])

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)
    xbmcplugin.setContent(int(sys.argv[1]), 'movies2')


# ('/asiptvs_vod_videos/
def asiptvs_vod_videos(params):  # category_id):
    category_id = params.get('url')
    title = params.get('title')
    url = base + "?" + login_infos + "&action=get_vod_streams&category_id=" + category_id
    response = http_request(url).read().decode('utf-8')
    json_data = json.loads(response)
    xbmc.log('jsondata {}'.format(json_data))
    if len(json_data):
        if 'English' in title:
            for l in ascii_lowercase:
                plugintools.add_item(title=l.upper(), action='asiptvs_vod_eng', url=category_id)
            xbmcplugin.setContent(int(sys.argv[1]), 'movies2')
        else:
            items = sorted(json_data, key=lambda k: k['name'], reverse=False)
            add_items(items, stream_url1)
            xbmcplugin.setContent(int(sys.argv[1]), 'movies')

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


def asiptvs_vod_eng(params):  # category_id):
    category_id = params.get('url')
    let = params.get('title').lower()
    url = base + "?" + login_infos + "&action=get_vod_streams&category_id=" + category_id
    response = http_request(url).read().decode('utf-8')
    json_data = json.loads(response)
    xbmc.log('jsondata {}'.format(json_data))
    if len(json_data):
        items = sorted(json_data, key=lambda k: k['name'], reverse=False)
        result = list([x for x in items if (x["name"].lower().replace(' ', '').startswith(let, 0))])
        add_items(result, stream_url1)

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def asiptvs_vod_videos2(category_id, let=None):
    url = base + "?" + login_infos + "&action=get_vod_streams&category_id=" + category_id
    response = http_request(url).read().decode('utf-8')
    json_data = json.loads(response)
    xbmc.log('jsondata {}'.format(json_data))
    if len(json_data):
        items = sorted(json_data, key=lambda k: k['name'], reverse=False)
        result = list([x for x in items if (x["name"].lower().replace(' ', '').startswith(let, 0))]) if let else items
        add_items(result, stream_url1)

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def asiptvs_play_stream(params):  # url, label):
    url = params.get('url')
    label = params.get('title')
    liz = xbmcgui.ListItem(label)
    liz.setArt({'icon': 'DefaultVideo.png', 'thumb': 'DefaultVideo.png'})
    liz.setInfo(type='Video', infoLabels={'Title': label})
    liz.setProperty("IsPlayable", "true")
    liz.setPath(url)
    xbmc.Player().play(url, liz)
    xbmc.Monitor().waitForAbort(1)
    if not xbmc.Player().isPlaying():
        xbmc.executebuiltin('Notification(Channel Unavailable at this moment,,10000,)')


def add_items(items, base_url):
    for item in items:
        label = item["name"]
        url = base_url + str(item["stream_id"]) + "&type=" + str(item["container_extension"])
        iconImage = item["stream_icon"]
        if item["stream_icon"] is None:
            iconImage = ''
        plugintools.add_item(action="asiptvs_play_stream", title=label, url=url, thumbnail=iconImage,
                             isPlayable=True)