import re
import traceback
from base64 import b64decode
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode
from urllib.request import pathname2url
from urllib.request import urlopen, Request

import requests as Net

from . import rijndael

try:
    from simplejson import loads as json_loads
except:
    print(('Plugin Error', 'simplejson import error: limited functionality'))
    pass
import xml.etree.ElementTree as ET
import json

import os
from resources.modules.utils import ApiError
import xbmc, xbmcaddon, xbmcgui, xbmcvfs

__settings__ = xbmcaddon.Addon(id='plugin.video.yams')

MaintenanceTitle = "Maintenance Tool"
MAIN_URL = 'https://api.yamsonline.com/api'
VOD_URL = 'https://astreamweb.com/kodi/vod.php'

GOOGLE_API_KEY = 'AIzaSyBuDCshXSkXWc6MuYTxhdLpCmLR1eMLAy8'
to_id = 'plugin.video.yams'

YOUTUBE_BASEAPI = 'https://www.googleapis.com/youtube/v3/'
YOUTUBE_PLAYLIST = 'playlists?part=snippet%%2CcontentDetails&channelId=%s&maxResults=%s&key=' + GOOGLE_API_KEY
YOUTUBE_PLAYLIST_PAGE = 'playlists?part=snippet%%2CcontentDetails&channelId=%s&maxResults=%s&pageToken=%s&key=' + GOOGLE_API_KEY
YOUTUBE_PLAYLISTITEM = 'playlistItems?part=snippet%%2CcontentDetails&playlistId=%s&maxResults=%s&key=' + GOOGLE_API_KEY
YOUTUBE_PLAYLISTITEM_PAGE = 'playlistItems?part=snippet%%2CcontentDetails&playlistId=%s&maxResults=%s&pageToken=%s&key=' + GOOGLE_API_KEY
YOUTUBE_SEARCH = 'https://www.googleapis.com/youtube/v3/search?part=snippet&q=%s&key=' + GOOGLE_API_KEY

digest = '1@121#'
GENRES = [{'name': 'Action', 'id': '34'},
          {'name': 'Adventure', 'id': '62'},
          {'name': 'Animation', 'id': '63'},
          {'name': 'Bluray', 'id': '72'},
          {'name': 'Bollywood', 'id': '54'},
          {'name': 'Comedy', 'id': '35'},
          {'name': 'Comedy Selection', 'id': '76'},
          {'name': 'Concerts and Stage Programs', 'id': '80'},
          {'name': 'Cricket', 'id': '78'},
          {'name': 'Crime', 'id': '64'},
          {'name': 'Digital Isai Thendral', 'id': '73'},
          {'name': 'Documentry', 'id': '36'},
          {'name': 'Drama', 'id': '37'},
          {'name': 'Family', 'id': '38'},
          {'name': 'Fantasy', 'id': '65'},
          {'name': 'Horror', 'id': '39'},
          {'name': 'Kollywood', 'id': '55'},
          {'name': 'Live Streaming Channels', 'id': '81'},
          {'name': 'Mollywood', 'id': '77'},
          {'name': 'Musical', 'id': '40'},
          {'name': 'Mystery', 'id': '66'},
          {'name': 'Romance', 'id': '42'},
          {'name': 'Sci-Fi', 'id': '41'},
          {'name': 'Short', 'id': '68'},
          {'name': 'Tamil Radio Station', 'id': '82'},
          {'name': 'Tamil Serials', 'id': '67'},
          {'name': 'Thriller', 'id': '69'},
          {'name': 'Tollywood', 'id': '56'},
          {'name': 'TV Programs', 'id': '83'},
          {'name': 'Tv Shows', 'id': '79'},
          {'name': 'War', 'id': '70'},
          {'name': 'Western', 'id': '71'}]

LANGS = [{'name': 'Hindi Movies', 'id': '54'},
         {'name': 'Tamil Movies', 'id': '55'},
         {'name': 'Telugu Movies', 'id': '56'},
         {'name': 'Malayalam Movies', 'id': '77'}]

ACCESS_CODES = {
    'PLAYBACK': '-11,22,27,31,32,42,52,62,72,102,112,122,132,142,152,162,172,1,92,2,82,25,182',
    'LIVE_STREAM': '-11,22,27,31,32,42,52,62,72,102,112,122,132,142,152,162,172,'
}

LATESMOVIES = {
    "language-54": "192",
    "language-55": "172",
    # "language-56": "162",
    # "language-77": "182"
}
try:
    with open(os.path.join(xbmcvfs.translatePath(os.path.join('special://home/', '')), 'userdata', 'actors.txt'),
              "r") as actorFile:
        actorFileC = actorFile.read()
        actorFileSplit = actorFileC.split(":")
        ACTORS = actorFileSplit[0].split(",")
        ACTRESSES = actorFileSplit[1].split(",")
except Exception as e:
    print((traceback.print_exc()))
    ACTORS, ACTRESSES = [[], []]


def get_latesMoviesCategory(language):
    try:
        return LATESMOVIES[language]
    except KeyError:
        return None


def get_mac():
    import uuid
    currentUUID = uuid.UUID('00000000-0000-0000-0000-000000000000')
    if xbmc.getCondVisibility("System.Platform.Android") == 1:
        uuidPath = os.path.join(xbmcvfs.translatePath(
            os.path.join('/sdcard/Android/data/com.androidtoid.com/', '')), "config.uuid")
    elif xbmc.getCondVisibility("System.Platform.Windows") == 1:
        uuidPath = os.path.join(
            xbmcvfs.translatePath(os.path.join(os.getenv('APPDATA'), '')), "config.uuid")
    elif xbmc.getCondVisibility("system.platform.tvos") == 1:
        uuidPath = os.path.join(
            xbmcvfs.translatePath(os.path.join('special://home/userdata/', '')), "config.uuid")
    elif xbmc.getCondVisibility("system.platform.osx") == 1:
        pathf = xbmcvfs.translatePath(
            os.path.join(os.getenv('HOME') + "/Library/Application Support/OSConfig/", ''))
        if not os.path.exists(pathf):
            os.mkdir(pathf)
        uuidPath = os.path.join(
            xbmcvfs.translatePath(os.path.join(os.getenv('HOME') + "/Library/Application Support/OSConfig/", '')),
            "config.uuid")
    if os.path.exists(uuidPath):
        try:
            uuidFile = open(uuidPath, 'r')
            currentUUID = uuid.UUID(uuidFile.read())
            uuidFile.close()
        except:
            print('>>> traceback starts >>>')
            traceback.print_exc()
            print('<<< traceback end <<<')
    else:
        currentUUID = uuid.uuid4()
        try:
            uuidFile = open(uuidPath, 'w')
            uuidFile.write(str(currentUUID))
            uuidFile.close()
            xbmcaddon.Addon('plugin.video.yams').setSetting('session', currentUUID)
        except:
            print('>>> traceback starts >>>')
            traceback.print_exc()
            print('<<< traceback end <<<')
    return str(currentUUID)


def get_deviceType():
    type = "None"
    print((xbmc.getCondVisibility("System.Platform.Windows") == 1))
    if (xbmc.getCondVisibility("System.Platform.Linux") == 1 and (
            xbmc.getInfoLabel("System.BatteryLevel") == "100%" or xbmc.getInfoLabel(
            "System.BatteryLevel") == "0%")) or xbmc.getCondVisibility(
            "System.Platform.Linux.RaspberryPi") == 1 or xbmc.getCondVisibility(
            "System.Platform.Windows") == 1 or xbmc.getCondVisibility(
            "System.Platform.OSX") == 1 or xbmc.getCondVisibility("System.Platform.ATV2") or xbmc.getCondVisibility(
            "System.Platform.tvos") == 1 or (xbmc.getCondVisibility("System.Platform.Android") == 1 and (
            xbmc.getInfoLabel("System.BatteryLevel") == "100%" or xbmc.getInfoLabel("System.BatteryLevel") == "0%")):
        type = "box"
    elif xbmc.getCondVisibility("System.Platform.Android") == 1 or xbmc.getCondVisibility("System.Platform.IOS") == 1:
        type = "box"
    return type


device_types = ["Linux", "Android", "IOS", "Linux.RaspberryPi", "Windows", "OSX", "atv2", "tvos"]


def get_device():
    devicetype = ""
    for type in device_types:
        if xbmc.getCondVisibility("System.Platform.{0}".format(type)):
            devicetype += " " + type
    return devicetype


def notifyError(header="AStreamWeb", msg='', duration=5000):
    rootDir = __settings__.getAddonInfo('path')
    if rootDir[-1] == ';':
        rootDir = rootDir[0:-1]
    aicon = xbmcvfs.translatePath(os.path.join(rootDir, 'icon.png'))
    print((aicon, "ikona ikonele"))
    builtin = "XBMC.Notification(%s,%s, %s, %s)" % (header, msg, duration, aicon)
    xbmc.executebuiltin(builtin)


def get_langs(force_online=False):
    if force_online:
        xbmc.log('get_langs forced online')
        json_data = __get_json({'task': 'categories'})
        languages = json_data['language']['categories']
    else:
        languages = LANGS
    xbmc.log('get_langs: %s' % languages)
    return languages


def get_genres(force_online=False):
    if force_online:
        xbmc.log('get_genres forced online')
        json_data = __get_json({'task': 'categories'})
        genres = json_data['all']['categories']
    else:
        genres = GENRES
    xbmc.log('get_genres: %s' % genres)
    return genres


def get_movies(username, path, page, per_page, sorting):
    xbmc.log('get_movies start: path="%s", page="%s", per_page="%s", sorting="%s"'
             % (path, page, per_page, sorting), xbmc.LOGINFO)
    request_dict = {
        'user': username,
        'task': 'movies',
        'without_files': '1',
        'per_page': per_page,
        'page': page,
    }
    if path and path != '-':
        for filter in path.split('+'):
            if filter and filter != '-':
                filter_criteria, id = filter.split('-', 1)
                if filter_criteria and id and id != '-':
                    xbmc.log('get_movies filter %s=%s' % (filter_criteria, id))
                    request_dict[filter_criteria] = id
    if sorting and sorting != '-':
        request_dict['sort'] = sorting
    json_data = __get_json(request_dict)
    data = json_data['data']
    items = [{
        'label': re.sub('\([ 0-9]*?\)', '', video['title']),
        'thumbnail': video['cover'].replace(' ', '%20'),
        'fanart': video.get('stills'),  # jaysheel
        'info': {
            'originaltitle': video['title'],
            'tagline': video['collection'],
            'plot': video['plot'],
            'year': int(video['year']),
            'cast': video['cast'].replace(', ', ',').split(','),
            'director': video['director'],
            'rating': float(video['rating']),
            'votes': video['votes'],
            'genre': __resolve_categories(video['categories'])
        },
        'id': video['id'],
    } for video in data]
    num_entries = int(json_data['pagination']['count'])
    has_next_page = (int(page) * int(per_page) < num_entries)
    xbmc.log('get_movies got items: "%s", np: "%s"' % (items, has_next_page))
    return items, has_next_page


def get_series(username, path, page, per_page, sorting):
    xbmc.log('get_movies start: path="%s", page="%s", per_page="%s", sorting="%s"'
             % (path, page, per_page, sorting))
    request_dict = {
        'user': username,
        'task': 'series',
        'without_files': '1',
        'per_page': per_page,
        'page': page,
    }
    if path and path != '-':
        for filter in path.split('+'):
            if filter and filter != '-':
                filter_criteria, id = filter.split('-', 1)
                if filter_criteria and id and id != '-':
                    xbmc.log('get_movies filter %s=%s' % (filter_criteria, id))
                    request_dict[filter_criteria] = id
    if sorting and sorting != '-':
        request_dict['sort'] = sorting
    json_data = __get_json(request_dict)
    seadata = json_data['data']
    items = [{
        'label': re.sub('\([ 0-9]*?\)', '', video['title']),
        'thumbnail': video['cover'].replace(' ', '%20'),
        'fanart': video.get('stills'),  # jaysheel
        'info': {
            'originaltitle': video['title'],
            'tagline': video['collection'],
            'plot': video['plot'],
            'year': int(video['year']),
            'cast': video['cast'].replace(', ', ',').split(','),
            'director': video['director'],
            'rating': float(video['rating']),
            'votes': video['votes'],
            'genre': __resolve_categories(video['categories'])
        },
        'id': video['id'],
    } for video in seadata]
    num_entries = int(json_data['pagination']['count'])
    has_next_page = (int(page) * int(per_page) < num_entries)
    xbmc.log('get_movies got items: "%s", np: "%s"' % (items, has_next_page))
    return items, has_next_page


def get_tv_streams(username, password):
    xbmc.log('get_tv_streams started with username=%s' % username)
    request_dict = {
        'user': username,
        'task': 'channelurls',
        'sort': 'rank',
        'cleancache': '1'
    }
    json_data = __get_json(request_dict)
    streams = []
    json_data['data'].reverse()
    xbmc.log('get_tv_streams started stream processing')
    for item in json_data['data']:
        stream_servers = []
        for stream in item['files']:
            url = __decrypt(stream['url'])
            if item.get('credentials') == '1':
                regexp = re.compile(r'\?')
                if regexp.search(url) is not None:
                    url += '&%s' % urlencode({'username': username, 'password': password})
                else:
                    url += '?%s' % urlencode({'username': username, 'password': password})

            stream_servers.append({
                'region': 'Server [%s]' % stream['server'].upper(),
                'url': url
            })
        streams.append({
            'id': item.get('id', 'UNKNOWN'),
            'label': item['title'],
            'info': {'overlay': 0},
            'thumbnail': item['cover'].replace(' ', '%20'),
            'credentials': item.get('credentials', 'UNKNOWN'),
            'stream_servers': stream_servers
        })
    xbmc.log('get_tv_streams got streams: "%d"' % len(streams))
    return streams


def get_radio_streams(username, password, rc):
    return __get_streams(username, password, rc, category='82')


def __get_streams(username, password, rc, category):
    xbmc.log('__get_streams started with username=%s, rc=%s, cat=%s' % (username,
                                                                        rc,
                                                                        category))
    request_dict = {'task': 'movies',
                    'user': username,
                    'sort': 'modified,DESC',
                    'category': category,
                    'cleancache': '1'}
    json_data = __get_json(request_dict)
    items = json_data['data']
    streams = list()
    r_valid_prefix = re.compile('strm$', re.IGNORECASE)
    for item in items:
        for file in item['nginx']:
            name = __decrypt(file['name'])
            if not re.search(r_valid_prefix, name):
                xbmc.log('__get_streams ignore "%s" - wrong prefix' % name)
                continue
            if not '[%s]' % rc in name:
                xbmc.log('__get_streams ignore "%s" - wrong region:"%s"' % (name,
                                                                            rc))
                continue
            path = __decrypt(file['name'])
            server = __decrypt(file['server'])
            url = __get_server_url(server, path, username, password,
                                   stream=True, v=ACCESS_CODES['LIVE_STREAM'])
            streams.append({'label': item['title'],
                            'thumbnail': item['cover'].replace(' ', '%20'),
                            'is_playable': True,
                            'is_folder': False,
                            'url': url})
            continue
    xbmc.log('__get_streams got streams: "%s"' % streams)
    return streams


def get_movie_files(movie_id, username, password):
    xbmc.log('get_movie_files started with movie_id=%s, username=%s' % (movie_id,
                                                                        username))
    # location
    r_eu = re.compile('s10.yamsftp.net', re.IGNORECASE)
    r_us = re.compile('s1.yamsftp.net', re.IGNORECASE)
    # songs
    r_videosongs = re.compile('Video Songs', re.IGNORECASE)
    # valid fileprefix
    r_valid = re.compile('(avi|mkv|iso|mp4|ts|mpg|wmv|flv|dat|m4v)$', re.IGNORECASE)
    # quality
    r_1080 = re.compile('(1080)')
    r_2160 = re.compile('(4K)|(2160)|(UltraHD)|(Ultra HD)')
    r_atmos = re.compile('(Atmos)|(2160)')
    r_720 = re.compile('(720)')
    r_good = re.compile('mkv$', re.IGNORECASE)
    r_med = re.compile('(avi|mpg|ts|iso|mp4|dat)$', re.IGNORECASE)
    r_low = re.compile('(tc|pdvd|DVDscr|pirate|cam)', re.IGNORECASE)
    # stream
    r_stream = re.compile('flv$', re.IGNORECASE)
    # tv show
    r_serials = re.compile('S([0-9]+)E([0-9]+)', re.IGNORECASE)
    # invalid server
    r_invalid_serv = re.compile('s3.yamsftp.net', re.IGNORECASE)
    # 3D Movies
    r_3d = re.compile('3D Movies', re.IGNORECASE)
    # languages
    r_tamil = re.compile('tamil', re.IGNORECASE)
    r_telugu = re.compile('telugu', re.IGNORECASE)
    r_hindi = re.compile('hindi', re.IGNORECASE)
    r_mala = re.compile('malayalam', re.IGNORECASE)
    # Override
    r_override = re.compile('209.212.145.158', re.IGNORECASE)

    xbmc.log('get_movie_files start')
    request_dict = {'task': 'movies',
                    'user': username,
                    'id': movie_id,
                    'cleancache': 1}
    json_data = __get_json(request_dict)
    nginx = json_data['data'][0]['nginx']
    videos = list()
    for file in nginx:
        name = __decrypt(file['name'])
        path = __decrypt(file['name'])
        server = __decrypt(file['server'])
        if not re.search(r_valid, name):
            xbmc.log('getVideo invalid: "%s"' % name)
            continue
        if re.search(r_invalid_serv, server):
            xbmc.log('getVideo wrong server "%s" for file %s' % (server, name))
            continue
        url = __get_server_url(server, path, username, password,
                               v=ACCESS_CODES['PLAYBACK'])
        # is tv-serials
        if re.search(r_serials, name):
            season, episode = re.search(r_serials, name).groups()
            videos.append({'season': season,
                           'episode': episode,
                           'label': name,
                           'url': url,
                           'thumbnail': thumbnail,
                           'plot': plot
                           })
        # is movie, needs quality and language tag
        else:
            # detect quality
            if re.search(r_1080, name):
                quality = 'High'
            elif re.search(r_atmos, name):
                quality = 'True 4K'
            elif re.search(r_2160, name):
                quality = 'Super High'
            elif re.search(r_720, name):
                quality = 'Good'
            elif re.search(r_good, name):
                quality = 'Medium'
            elif re.search(r_med, name):
                quality = 'Medium'
            elif re.search(r_stream, name):
                quality = 'Stream'
            else:
                quality = 'Unknown'
            if re.search(r_low, name):
                quality = 'Low'
            # detect language
            if re.search(r_tamil, name + path):
                language = 'Tamil'
            elif re.search(r_telugu, name + path):
                language = 'Telugu'
            elif re.search(r_hindi, name + path):
                language = 'Hindi'
            elif re.search(r_mala, name + path):
                language = 'Malayalam'
            else:
                language = ''
            xbmc.log('getVideo append: "%s" with quality "%s"' % (name, quality))

            # Override .mp4 on live.yamsonline.com
            if re.search(r_med, name) and re.search(r_override, url):
                quality = 'Stream'
            label = '[%s Quality]' % (quality)
            # if language
            if language:
                label = label + ' [%s]' % (language)
            # is EU server
            if re.search(r_eu, server):
                label = label + ' [EU]'
            if (re.search(r_1080, name) or re.search(r_720, name)) and re.search(r_us, server):
                label = label + ' [US]'
            # is video song
            if re.search(r_videosongs, path):
                label = label + ' [Video Song]'
            # is 3D Movies
            if re.search(r_3d, path):
                label = label + ' [3D Movies]'

            label = label + ' - %s' % (name)
            thumbnail = json_data['data'][0]['thumbnail']
            plot = json_data['data'][0]['plot']
            videos.append({
                'label': label,
                'url': url,
                'thumbnail': thumbnail,
                'plot': plot
            })

    return videos


def get_seasons(movie_id, username, password, seasn):
    try:
        if seasn == 0:
            url = 'https://api.yamsonline.com/api?task=season&option=com_jsonapi&format=json&cleancache=1&version=v2&user=%s&id=%s&digest=%s' % (
            username, movie_id, digest)

        else:
            url = 'https://api.yamsonline.com/api?task=season&option=com_jsonapi&format=json&cleancache=1&version=v2&user=%s&id=%s&season_num=%s&digest=%s' % (
            username, movie_id, seasn, digest)
        xbmc.log('get_saisons url %s' % url)
        response = urlopen(url).read().decode('utf-8')
        json_data = json.loads(response)  # ;print(json_data)
    except:
        pass

    data = json_data["data"][0]["series_seasons"]
    for video in data:
        if (video["season_poster"] == 'null') or (video["season_poster"] is None):
            video["season_poster"] = ''
    # xbmc.log(' data de scraper %s'%data)
    items = [{
        'label': video["season_number"],

        'thumbnail': video["season_poster"].replace('\\', ''),
        'info': video["episode_data"]
    } for video in data]

    # xbmc.log('get_saisons started with movie_id=%s, username=%s' % (movie_id,
    return items


def get_series_files(movie_id, username, password):
    xbmc.log('get_series_files started with movie_id=%s, username=%s' % (movie_id,
                                                                         username))
    # location
    r_eu = re.compile('s10.yamsftp.net', re.IGNORECASE)
    r_us = re.compile('s1.yamsftp.net', re.IGNORECASE)
    # songs
    r_videosongs = re.compile('Video Songs', re.IGNORECASE)
    # valid fileprefix
    r_valid = re.compile('(avi|mkv|iso|mp4|ts|mpg|wmv|flv|dat|m4v)$', re.IGNORECASE)
    # quality
    r_low = re.compile('(pdvd|pre-|predvd|DVDscr|pirate|cam|hdcam)', re.IGNORECASE)
    r_1080 = re.compile('(1080)')
    r_2160 = re.compile('(4K)|(2160)|(UltraHD)|(Ultra HD)', re.IGNORECASE)
    r_720 = re.compile('(720)')
    r_good = re.compile('mkv$', re.IGNORECASE)
    r_med = re.compile('(avi|mpg|ts|iso|mp4|dat)$', re.IGNORECASE)
    # stream
    r_stream = re.compile('flv$', re.IGNORECASE)
    # tv show
    r_serials = re.compile('S([0-9]+)E([0-9]+)', re.IGNORECASE)
    # invalid server
    r_invalid_serv = re.compile('s3.yamsftp.net', re.IGNORECASE)
    # 3D Movies
    r_3d = re.compile('3D Movies', re.IGNORECASE)
    # languages
    r_tamil = re.compile('tamil', re.IGNORECASE)
    r_telugu = re.compile('telugu', re.IGNORECASE)
    r_hindi = re.compile('hindi', re.IGNORECASE)
    r_mala = re.compile('malayalam', re.IGNORECASE)
    # Override
    r_override = re.compile('209.212.145.158', re.IGNORECASE)

    xbmc.log('get_series_files start')
    request_dict = {'task': 'series',
                    'user': username,
                    'id': movie_id,
                    'cleancache': 1}
    json_data = __get_json(request_dict)
    nginx = json_data['data'][0]['nginx']
    videos = list()

    for file in nginx:
        name = __decrypt(file['name'])
        path = __decrypt(file['name'])
        server = __decrypt(file['server'])
        if not re.search(r_valid, name):
            xbmc.log('getVideo invalid: "%s"' % name)
            continue
        if re.search(r_invalid_serv, server):
            xbmc.log('getVideo wrong server "%s" for file %s' % (server, name))
            continue
        url = __get_server_url(server, path, username, password,
                               v=ACCESS_CODES['PLAYBACK'])
        xbmc.log('getVideo url server "%s" ' % (url))
        xbmc.log('getVideo name server "%s" ' % (name))
        # is tv-serials
        if re.search(r_serials, name):
            season, episode = re.search(r_serials, name).groups()
            xbmc.log('getseason season episode "%s" "%s" ' % (season, episode))
            videos.append({'season': season,
                           'episode': episode,
                           'label': name,
                           'url': url})
        # is movie, needs quality and language tag
        else:
            # detect quality
            if re.search(r_1080, name):
                quality = 'Super High'
            elif re.search(r_2160, name):
                quality = '4K Ultra HD'
            elif re.search(r_720, name):
                quality = 'High'
            elif re.search(r_good, name):
                quality = 'Good'
            elif re.search(r_med, name):
                quality = 'Medium'
            elif re.search(r_stream, name):
                quality = 'Stream'
            else:
                quality = 'Unknown'
            if re.search(r_low, name):
                quality = 'Low'
            # detect language
            if re.search(r_tamil, name + path):
                language = 'Tamil'
            elif re.search(r_telugu, name + path):
                language = 'Telugu'
            elif re.search(r_hindi, name + path):
                language = 'Hindi'
            elif re.search(r_mala, name + path):
                language = 'Malayalam'
            else:
                language = ''
            xbmc.log('getVideo append: "%s" with quality "%s"' % (name, quality))

            # Override .mp4 on live.yamsonline.com
            if re.search(r_med, name) and re.search(r_override, url):
                quality = 'Stream'

            label = '[%s Quality]' % (quality)
            # if language
            if language:
                label = label + ' [%s]' % (language)
            # is EU server
            if re.search(r_eu, server):
                label = label + ' [EU]'
            if (re.search(r_1080, name) or re.search(r_720, name)) and re.search(r_us, server):
                label = label + ' [US]'
            # is video song
            if re.search(r_videosongs, path):
                label = label + ' [Video Song]'
            # is 3D Movies
            if re.search(r_3d, path):
                label = label + ' [3D Movies]'

            label = label + ' - %s' % (name)
            thumbnail = json_data['data'][0]['thumbnail']
            plot = json_data['data'][0]['plot']
            videos.append({
                'label': label,
                'url': url,
                'thumbnail': thumbnail,
                'plot': plot
            })

    return videos


def get_youtube_playlist(channel, per_page, sorting, pageToken=None):
    xbmc.log('Getting playlist %s %s' % (channel, pageToken))
    nextPage = None
    prevPage = None

    shows = list()
    if pageToken is None:
        url = urlopen(YOUTUBE_BASEAPI + YOUTUBE_PLAYLIST % (channel, str(per_page)))
    else:
        url = urlopen(YOUTUBE_BASEAPI + YOUTUBE_PLAYLIST_PAGE % (channel, str(per_page), pageToken))

    play_list = json.load(url)
    num_entries = play_list['pageInfo']['totalResults']

    if 'nextPageToken' in play_list:
        nextPage = play_list['nextPageToken']
    if 'prevPageToken' in play_list:
        prevPage = play_list['prevPageToken']

    if num_entries > 0:
        for play in play_list['items']:
            # Get HQ thumbnail
            thumbnail = ''
            if 'thumbnails' in play['snippet']:
                thumb = play['snippet']['thumbnails']
                if 'high' in thumb:
                    thumbnail = thumb['high']['url']
                elif 'medium' in thumb:
                    thumbnail = thumb['medium']['url']
                elif 'default' in thumb:
                    thumbnail = thumb['default']['url']

            shows.append({'name': play['snippet']['title'],
                          'icon': thumbnail,
                          'playlist': play['id']})

    return shows, nextPage, prevPage


def get_youtube_playitem(channel, per_page, sorting, pageToken=None):
    xbmc.log('Getting playlist for item %s %s' % (channel, pageToken))
    nextPage = None
    prevPage = None

    shows = list()
    if pageToken is None:
        url = urlopen(YOUTUBE_BASEAPI + YOUTUBE_PLAYLISTITEM % (channel, str(per_page)))
    else:
        url = urlopen(YOUTUBE_BASEAPI + YOUTUBE_PLAYLISTITEM_PAGE % (channel, str(per_page), pageToken))

    play_list = json.load(url)
    num_entries = play_list['pageInfo']['totalResults']

    if 'nextPageToken' in play_list:
        nextPage = play_list['nextPageToken']
    if 'prevPageToken' in play_list:
        prevPage = play_list['prevPageToken']

    if num_entries > 0:
        for play in play_list['items']:
            # Get HQ thumbnail
            thumbnail = ''
            if 'thumbnails' in play['snippet']:
                thumb = play['snippet']['thumbnails']
                if 'high' in thumb:
                    thumbnail = thumb['high']['url']
                elif 'medium' in thumb:
                    thumbnail = thumb['medium']['url']
                elif 'default' in thumb:
                    thumbnail = thumb['default']['url']

            shows.append({'name': play['snippet']['title'],
                          'icon': thumbnail,
                          'channel': play['contentDetails']['videoId']})

    return shows, nextPage, prevPage


'''
    request_dict = {
    'task' : 'vod',
    'sort' : sorting,
    'per_page' : per_page,
    'page' : page
    }
    json_data = __get_json(request_dict)
    items = json_data['data']
    '''


def check_login(username, password, session=None):
    request_dict = {
        'task': 'checklogin',
        'user': username,
        'password': password,
        'session': get_mac(),
        'device': get_deviceType()
    }

    # xbmc.log('login request data: "%s"' % json.dumps(request_dict), level=xbmc.LOGINFO)  # to be removed request data

    json_data = __get_json(request_dict, raiseError=False)
    xbmc.log('check_login result: "%s"' % json_data, level=xbmc.LOGINFO)
    if json_data.get('status') == 'success':
        return True, json_data.get('session'), json_data.get('status_code', '')
    else:
        return False, json_data.get('reason', ''), json_data.get('status_code', '')


def check_session(username, password, session_id):
    request_dict = {
        'task': 'startapi',
        'username': username,
        'password': password,
        'session': get_mac(),
        'v': __settings__.getSetting('boxname')
    }
    json_data = __get_json(request_dict, raiseError=False)
    xbmc.log('check_session result: "%s"' % json_data)
    if json_data.get('status') == 'success':
        return True, session_id, json_data.get('status_code', '')
    else:
        return False, json_data.get('reason', ''), json_data.get('status_code', '')


def check_login_stream(username, password):
    request_dict = {
        'task': 'checkloginstream',
        'user': username,
        'password': password
    }
    json_data = __get_json(request_dict, raiseError=False)
    xbmc.log('check_login_stream result: "%s"' % json_data)
    if json_data.get('status') == 'success':
        return True, ''
    else:
        return False, json_data.get('reason', '')


def check_login_iptv(username, password):
    request_dict = {
        'task': 'checkloginiptv',
        'user': username,
        'password': password
    }
    json_data = __get_json(request_dict, raiseError=False)
    xbmc.log('check_login_stream result: "%s"' % json_data)
    if json_data.get('status') == 'success':
        return True, ''
    else:
        return False, json_data.get('reason', '')


def check_digest(username, password, digest):
    request_dict = {
        'task': 'checkdigest',
        'user': username,
        'password': password,
        'digest': digest
    }
    json_data = __get_json(request_dict, raiseError=False)
    xbmc.log('check_digest result: "%s"' % json_data)
    if json_data.get('status') == 'success':
        return True, ''
    else:
        return False, json_data.get('reason', '')


def check_network():
    return True
    request = Request('https://goo.gl/rbTo3')
    request.get_method = lambda: 'HEAD'
    request.add_header('User-Agent',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 '
                       'Safari/537.1')
    try:
        urlopen(request).info()
    except HTTPError:
        pass
    else:
        return True


def delete_sessions(username, password):
    request_dict = {
        'task': 'deletesessions',
        'username': username,
        'password': password,
    }
    json_data = __get_json(request_dict, raiseError=False)
    xbmc.log('delete session result: "%s"' % json_data)
    if json_data.get('status') == 'success':
        return True, json_data.get('reason', '')
    else:
        return False, json_data.get('reason', '')


def __get_json(data, raiseError=True):
    try:
        xbmc.log('get_json:' + digest, level=xbmc.LOGINFO)
        data['option'] = 'com_jsonapi'
        data['format'] = 'json'
        data['digest'] = digest
        data['version'] = 'v2'
        url = '%s?%s' % (MAIN_URL, urlencode(data))

        xbmc.log('__get_json opening url: %s' % url)
        response = urlopen(url).read().decode('utf-8')
        # xbmc.log('response: ' + response.decode('utf-8'), level=xbmc.LOGINFO)

        json_data = json_loads(response)
        # xbmc.log('__get_json got %d bytes from url: %s' % (len(response), url))
        # log('response: ' + response )
        # log('JSON SESSION DATA: %s' % json_data.get('session'))
        if json_data.get('status') == 'error' and raiseError:
            xbmc.log('__get_json opening url: %s' % url)
            dialog = xbmcgui.Dialog()
            dialog.ok('Access Error', json_data.get('reason'))
            raise ApiError('AccessError')
    except HTTPError:
        raise ApiError('HTTPError')
    except URLError:
        raise ApiError('URLError')
    return json_data


def __resolve_categories(cat_ids):
    found_list = list()
    for cat_id in cat_ids:
        found = [g['name'] for g in GENRES if g['id'] == cat_id]
        if found:
            found_list.append(found[0])
        else:
            xbmc.log('__resolve_categories couldnt find id: %s' % cat_id)
    return ' | '.join(found_list)


def __get_server_url(server, path, username, password,
                     v=ACCESS_CODES['PLAYBACK'], stream=False):
    xbmc.log(('__get_server_url started with server="%s", username="%s"'
              ', path="%s", v="%s", stream="%s"')
             % (server, username, path, v, stream))
    params = urlencode({
        'name': path,
        'username': username,
        'password': password})
    if stream:
        url = 'https://%s/amember_remote/d.strm?%s' % (server, params)
    elif server == 'live.yamsonline.com:81':
        url = '%s%s' % (server, pathname2url(path))
    else:
        url = '%s&%s' % (server, params)
    return url


def __decrypt(encoded):
    key = ')y4&$G[GHT0Fks=%'
    padded_key = key.ljust(16, '\0')
    ciphertext = b64decode(encoded)
    # xbmc.log('decode datatype: %s ' % type(ciphertext))
    r = rijndael.rijndael(padded_key, 32)
    padded_text = ''
    for start in range(0, len(ciphertext), 32):
        padded_text += r.decrypt(ciphertext[start:start + 32])
    plaintext = padded_text.split('\x00', 1)[0]
    return plaintext


def __set_digest(hash):
    global digest
    digest = hash


def clearCache():
    import shutil
    xbmc_cache_path = os.path.join(xbmcvfs.translatePath('special://home'), 'cache')
    print(('hwang paht xbmc_cache_path = ' + xbmc_cache_path))
    if os.path.exists(xbmc_cache_path):
        for root, dirs, files in os.walk(xbmc_cache_path):
            file_count = 0
            file_count += len(files)
            if file_count > 0:

                dialog = xbmcgui.Dialog()
                if dialog.yesno("Delete XBMC Cache Files",
                                str(file_count) + " files found\nDo you want to delete them?"):

                    for f in files:
                        try:
                            os.unlink(os.path.join(root, f))
                        except:
                            pass
                    for d in dirs:
                        try:
                            shutil.rmtree(os.path.join(root, d))
                        except:
                            pass

            else:
                pass


def get_installedversion():
    # retrieve current installed version
    json_query = xbmc.executeJSONRPC(
        '{ "jsonrpc": "2.0", "method": "Application.GetProperties", "params": {"properties": ["version", "name"]}, "id": 1 }')
    json_query = str(json_query, 'utf-8', errors='ignore')
    json_query = json.loads(json_query)
    version_installed = []
    if 'result' in json_query and 'version' in json_query['result']:
        version_installed = json_query['result']['version']
    return version_installed


################################
###       Advanced XML       ###
################################
def _downloadOverride(url, oFile):
    xbmc.log('_downloadOverride %s' % url, xbmc.LOGINFO)
    try:
        # Removing old file
        if os.path.exists(oFile):
            os.remove(oFile)

        # Getting new file
        link = Net.get(url).content
        nFile = open(oFile, 'w')
        nFile.write(link.decode('utf-8'))
        nFile.close()

        # Check write with cache
        with open(oFile, 'r') as myfile:
            data = myfile.read()
        myfile.close()

        if not (data == link):
            return False

        return True
    except:
        print('>>> traceback >>>')
        traceback.print_exc()
        print('<<< file error traceback end <<<')
        xbmc.log('Write Error: %s' % oFile, xbmc.LOGINFO)
        return False


def ZeroCachingSetting():
    try:
        dialog = xbmcgui.Dialog()

        path = xbmcvfs.translatePath(os.path.join('special://home/', ''))

        if xbmc.getCondVisibility('System.Platform.Android'):
            advUrl = 'https://astreamweb.com/kodi/android/advancedsettings.xml'
        else:
            advUrl = 'https://astreamweb.com/kodi/advancedsettings.xml'
        advance = os.path.join(path, 'userdata', 'advancedsettings.xml')

        # guiUrl = 'http://astreamweb.com/kodi/guisettings.xml'
        # guisettings = os.path.join(path, 'userdata', 'guisettings.xml')

        actUrl = 'https://astreamweb.com/kodi/actors.txt'
        actsettings = os.path.join(path, 'userdata', 'actors.txt')

        kbUrl = 'https://astreamweb.com/kodi/keyboard.xml'
        kbPath = os.path.join(path, 'userdata', 'keymaps', )
        if not os.path.exists(kbPath):
            os.makedirs(kbPath)
        remote = os.path.join(kbPath, 'keyboard.xml')

        kbUrl1 = 'https://astreamweb.com/kodi/subtitles/settings.xml'
        kbPath1 = os.path.join(path, 'userdata', 'addon_data', 'service.subtitles.opensubtitles', )
        if not os.path.exists(kbPath1):
            os.makedirs(kbPath1)
        subtitle = os.path.join(kbPath1, 'settings.xml')

        verUrl = 'https://astreamweb.com/kodi/settingsversion.xml'
        verPath = os.path.join(path, 'addons', 'service.xbmc.versioncheck', 'resources')
        if not os.path.exists(verPath):
            os.makedirs(verPath)
        versettings = os.path.join(verPath, 'settings.xml')

        # Retrieve major version
        # version_installed = get_installedversion()
        # xbmc.log(version_installed)

        if not _downloadOverride(advUrl, advance):
            dialog.ok(MaintenanceTitle,
                      'There was an issue applying FireTV advanced settings. Please check your log file.')
            return

        if not _downloadOverride(actUrl, actsettings):
            dialog.ok(MaintenanceTitle, 'There was an issue applying search update. Please check your log file.')
            return
        if not _downloadOverride(verUrl, versettings):
            dialog.ok(MaintenanceTitle, 'There was an issue Disabling VersionCheck. Please check your log file.')
            return
        if not _downloadOverride(kbUrl1, subtitle):
            dialog.ok(MaintenanceTitle, 'There was an issue Disabling VersionCheck. Please check your log file.')
            return

        # if dialog.yesno('Fire TV Only', 'Are you using a Fire TV Device?'):
        #    kbResult = _downloadOverride(kbUrl, remote)
        #    if not kbResult:
        if not _downloadOverride(kbUrl, remote):
            dialog.ok(MaintenanceTitle,
                      'There was an issue applying FireTV remote settings. Please check your log file.')
            return

        # if (version_installed['major'] > 15):
        #    if not _downloadOverride(setUrl, settings):
        #        dialog.ok(MaintenanceTitle, 'There was an issue applying FireTV gui settings. Please check your log file.')
        #        return
        xbmc.executebuiltin('Skin.ResetSettings')
        xbmc.executebuiltin('Skin.SetBool(HomeMenuNoAstreamWebButton)')
        xbmc.executebuiltin('Skin.SetBool(HomeMenuNosystemButton)')
        xbmc.executebuiltin('Skin.SetBool(HomeMenuNoStandardButton)')
        xbmc.executebuiltin('Skin.SetBool(HomeMenuNoPremiumButton)')
        xbmc.executebuiltin('Skin.SetBool(HomeMenuNoCatchupButton)')
        xbmc.executebuiltin('Skin.SetBool(HomeMenuNoLatestButton)')
        xbmc.executebuiltin('Skin.SetBool(HomeMenuNoMyAccountButton)')
        xbmc.executebuiltin('Skin.SetBool(FirstTimeRun)')
        xbmc.executebuiltin("XBMC.ActivateWindow(Home)")
        xbmc.executebuiltin('Skin.SetString(HomeVideosButton1, plugin.video.yams)')
        xbmc.executebuiltin('UnloadSkin()')
        xbmc.executebuiltin('ReloadSkin()')
        xbmc.executebuiltin('Action(reloadkeymaps)')
    except Exception as e:
        xbmc.log('zero {}'.format(str(e)))


def VerifyAdvancedSetting():
    print(('###' + MaintenanceTitle + ' - CHECK ADVANCE XML###'))
    name = 'Verify Advanced Settings'
    path = xbmcvfs.translatePath(os.path.join('special://home/userdata', ''))
    advance = os.path.join(path, 'advancedsettings.xml')
    try:
        a = open(advance).read().decode('utf-8')
        if 'zero' in a:
            name = 'AstreamWeb'
        elif 'tuxen' in a:
            name = 'TUXENS'
    except:
        name = "NO ADVANCED"
    dialog = xbmcgui.Dialog()
    dialog.ok(MaintenanceTitle, "[COLOR yellow]YOU HAVE[/COLOR] " + name + "[COLOR yellow] SETTINGS installed[/COLOR]")


def ResetAstreamWeb():
    xbmc.executebuiltin("ActivateWindow(Programs, plugin://plugin.video.resetastreamweb)")


def Newwindow1():
    xbmc.executebuiltin('ReplaceWindow(Videos, addons://sources/video/)')


def Newwindow():
    xbmc.executebuiltin('RunPlugin(plugin://plugin.video.yams)')
    xbmc.executebuiltin('Container.Refresh(plugin://plugin.video.yams)')


def Calibration():
    dialog = xbmcgui.Dialog()
    dialog.ok('Screen Calibration',
              'On the following page please use the arrow keys to adjust the screen to your Device so u can see the '
              'blue arrow on top \n left and do the same for buttom right. Exit by pressing back button once '
              'completed.')
    xbmc.executebuiltin('ActivateWindow(screencalibration)')


def get1DayBypass(username, password):
    data = __get_json({"task": "get1dayBypass", "username": username, "password": password})
    return data


def get5DayBypass(username, password):
    data = __get_json({"task": "get5dayBypass", "username": username, "password": password})
    return data


def getBypassActive(username):
    data = __get_json({"task": "isbypassactive", "username": username})
    return data
