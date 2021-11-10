import re
import sys
import json,time
from datetime import datetime
from time import sleep
import urllib.request, urllib.error, urllib.parse
from urllib.request import urlopen
from string import ascii_lowercase
import xbmcgui, xbmc, xbmcplugin
import resources.modules.scraper as scraper
from resources.modules.utils import ApiError, log
from . import plugintools

params = plugintools.get_params()
__get_icon = plugintools.__get_icon
per_page = int(plugintools.get_setting('per_page'))

username = plugintools.get_setting('username')
password = plugintools.get_setting('password')
base = "http://iptv-line.com:8080/player_api.php"
stream_url = "https://api.yamsonline.com/iptv/connect?username=" + username + "&format=stream1&provider=1&password=" + password + "&id="
stream_url1 = "https://api.yamsonline.com/iptv/connect?username=" + username + "&format=vod1&provider=1&password=" + password + "&id="
login_infos = "username=quarantine&password=I5iuxBk5zA"
NOVELAS_CATEGORY_ID = '117'


#('/asiptvs_vod/')
def asiptvs_vod():
    items = []
    url = base + "?" + login_infos + "&action=get_vod_categories"
    response = urlopen(url).read()
    json_data = json.loads(response)
    if len(json_data):
        items = sorted(json_data, key=lambda k: k["category_name"], reverse=False)
        for item in items:
            plugintools.add_item(action='asiptvs_vod_videos' ,title=item["category_name"],url = item["category_id"])

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)
    xbmc.executebuiltin('Container.SetViewMode(50)')

#('/asiptvs_vod_videos/
def asiptvs_vod_videos(params):#category_id):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies4')
    category_id = params.get('url')
    title = params.get('title')
    items = []
    url = base + "?" + login_infos + "&action=get_vod_streams&category_id=" + category_id
    response = urlopen(url).read()
    json_data = json.loads(response)
    xbmc.log('jsondata {}'.format(json_data))
    if len(json_data):
        if 'English' in title :
            for l in ascii_lowercase:
                plugintools.add_item(title=l.upper(),action='asiptvs_vod_eng',url=category_id)
        else :
            items = sorted(json_data, key=lambda k: k['name'], reverse=False)
            for item in items:
                label = item["name"]
                url = stream_url1 + str(item["stream_id"]) + "&type=" + str(item["container_extension"])
                iconImage = item["stream_icon"]
                if item["stream_icon"] == None :  iconImage = ''
                plugintools.add_item(action="asiptvs_play_stream",title=label.encode("utf-8"),url = url,thumbnail=iconImage,
                                     isPlayable=True)

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)

def asiptvs_vod_eng(params):#category_id):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies4')
    category_id = params.get('url')
    let = params.get('title').lower()
    items = []
    url = base + "?" + login_infos + "&action=get_vod_streams&category_id=" + category_id
    response = urlopen(url).read()
    json_data = json.loads(response)
    xbmc.log('jsondata {}'.format(json_data))
    if len(json_data):
        items = sorted(json_data, key=lambda k: k['name'], reverse=False)
        result = list([x for x in items if (x["name"].lower().replace(' ','').startswith(let,0))])

        for item in result:
            label = item["name"]
            url = stream_url1 + str(item["stream_id"]) + "&type=" + str(item["container_extension"])
            iconImage = item["stream_icon"]
            if item["stream_icon"] == None :  iconImage = ''
            plugintools.add_item(action="asiptvs_play_stream",title=label.encode("utf-8"),url = url,thumbnail=iconImage,
                                 isPlayable=True)

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


def asiptvs_vod_videos2(category_id):
    items = []
    url = base + "?" + login_infos + "&action=get_vod_streams&category_id=" + category_id
    response = urlopen(url).read()
    json_data = json.loads(response)
    xbmc.log('jsondata {}'.format(json_data))
    if len(json_data):
        items = sorted(json_data, key=lambda k: k['name'], reverse=False)
        for item in items:
            label = item["name"]
            url = stream_url1 + str(item["stream_id"]) + "&type=" + str(item["container_extension"])
            iconImage = item["stream_icon"]
            if item["stream_icon"] == None :  iconImage = ''
            plugintools.add_item(action="asiptvs_play_stream",title=label.encode("utf-8"),url = url,thumbnail=iconImage,
                                 isPlayable=True)

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)
    xbmc.executebuiltin('Container.SetViewMode(500)')


def asiptvs_vod_videos2l(category_id,let):
    items = []
    url = base + "?" + login_infos + "&action=get_vod_streams&category_id=" + category_id
    response = urlopen(url).read()
    json_data = json.loads(response)
    xbmc.log('jsondata {}'.format(json_data))
    if len(json_data):
        items = sorted(json_data, key=lambda k: k['name'], reverse=False)
        result = list([x for x in items if (x["name"].lower().replace(' ','').startswith(let,0))])

        for item in result:
            label = item["name"]
            url = stream_url1 + str(item["stream_id"]) + "&type=" + str(item["container_extension"])
            iconImage = item["stream_icon"]
            if item["stream_icon"] == None :  iconImage = ''
            plugintools.add_item(action="asiptvs_play_stream",title=label.encode("utf-8"),url = url,thumbnail=iconImage,
                                 isPlayable=True)

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)

def asiptvs_play_stream(params):#url, label):
    url = params.get('url')
    label = params.get('title')
    liz = xbmcgui.ListItem(label)
    liz.setArt(icon='DefaultVideo.png', thumb='DefaultVideo.png')
    liz.setInfo(type='Video', infoLabels={'Title':label})
    liz.setProperty("IsPlayable","true")
    liz.setPath(url)
    xbmc.Player().play(url, liz)
    time.sleep(3)
    if xbmc.Player().isPlaying() == False:
        xbmc.executebuiltin('Notification(Channel Unavailable at this moment,,10000,)')
