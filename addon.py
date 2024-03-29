import os
import base64
import urllib.request
import urllib.error
import urllib.parse
import requests
import subprocess
import re

from os import path as os_path
import datetime as dt
import traceback

import importlib
import zipfile
import math

from resources.modules import (scraper, yamsutils, asiptvs, engchannels)
from resources.modules.asiptvs import *
from resources.modules.engchannels import *
from resources.modules.utils import ApiError, postHtml
from resources.modules.loginobf import login_info

import xbmc, xbmcaddon, xbmcgui, xbmcplugin, xbmcvfs
from common import http_request
from boxname import boxname

# import SimpleDownloader as downloader
# downloader = downloader.SimpleDownloader()

# try:
#     import StorageServer
# except:
#     import resources.modules.storageserverdummy as StorageServer

##########################################
ADDON_INFO = xbmcaddon.Addon().getAddonInfo
Path = xbmcaddon.Addon().getAddonInfo('path')
dataPath = xbmcvfs.translatePath(ADDON_INFO('profile'))
icon = xbmcvfs.translatePath(os.path.join(Path, 'icon.png'))
fanart = xbmcvfs.translatePath(os.path.join(Path, ''))

#########################################
username = plugintools.get_setting('username')
password = plugintools.get_setting('password')

digest = yamsutils.__digest(Path)
# scraper.__set_digest(digest)
# xbmc.log("d2Fpc3Rpbmd5b3VydGltZV9hY2NvdW50YmxvY2tlZA {}".format(digest))
scraper.__set_digest('39e8d194da075e2c41d8f8648ae94764a6a8c9f98a8fb05ae4d8a62f3ce1ea91')

dialog = xbmcgui.Dialog()
cookie_file = os.path.join(os.path.join(dataPath, ''), 'snhdcookie.lwp')
agentType = '0'

vijayVODUrl_ori = f'''https://api.yamsonline.com/astream?name=hotstarnew&username={username}&password={password}'''

importlib.reload(sys)
# sys.setdefaultencoding('utf8') # deprecated in python3
params = plugintools.get_params()

HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
}


def run():
    if xbmc.getCondVisibility("System.Platform.Android") == 1:
        if not os.path.exists(xbmcvfs.translatePath('/storage/emulated/0/DCIM/Android_0/')):
            os.mkdir(xbmcvfs.translatePath('/storage/emulated/0/DCIM/Android_0/'))
    if params.get("action") is None:
        if xbmc.getInfoLabel("System.BuildVersion") >= "19.3":
            home(params)
        else:
            dialog.ok('APP EXPIRED',
                      "Please upgrade app(current:" + xbmc.getInfoLabel(
                          "System.BuildVersion") + "),\nFollow guide: http://tiny.cc/newinstall")
            return
    else:
        if xbmc.getInfoLabel("System.BuildVersion") >= "19.3":
            action = params.get("action")
            exec(action + "(params)")
        else:
            dialog.ok('APP EXPIRED',
                      "Please upgrade app(current:" + xbmc.getInfoLabel(
                          "System.BuildVersion") + "),\nFollow guide: http://tiny.cc/newinstall")
            return


def home(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies2')

    try:
        authenticated, status_code = __check_login()
        xbmc.log(f'''Authenticated {authenticated}''', xbmc.LOGINFO)
        xbmc.log(f'''Status {status_code}''', xbmc.LOGINFO)

        if status_code == 0 or status_code == 8:
            plugintools.add_item(action="show_restart", title="restart AstreamWeb",
                                 thumbnail=__get_icon('resetastreamweb'), folder=False)

        if status_code == 4 or status_code == 5:
            plugintools.add_item(action="show_restart1", title="restart AstreamWeb",
                                 thumbnail=__get_icon('resetastreamweb'), folder=False)

        # 1 Add Link to Favourites
        if authenticated:
            plugintools.add_item(action="api_yamsonline_providers", title="My Notify", thumbnail=__get_icon('notify'),
                                 page='1', extra='notify', folder=True)  # pagenum = '1'

        if authenticated:
            plugintools.add_item(action="api_yamsonline_providers", title="My Favourite", thumbnail=__get_icon('hint'),
                                 page='1', extra='favorite', folder=True)  # pagenum = '1'

        xbmc.log('show_index end')
        if xbmc.getCondVisibility(
                '!Skin.HasSetting(HomeMenuNoBasicButton)') and authenticated:
            plugintools.add_item(action="show_iptv_favourite", title="IPTV Favourite", thumbnail=__get_icon('iptvf'),
                                 page='1', folder=True)  # pagenum = '1'

        # 2 Add search movies
        if authenticated:
            plugintools.add_item(action="search", title="Multi Search", thumbnail=__get_icon('Search by title'),
                                 folder=True)

        if authenticated and xbmc.getCondVisibility('!Skin.HasSetting(HomeMenuNoBasicButton)'):
            plugintools.add_item(action="personal", title="Personal", thumbnail=__get_icon('personal'), folder=True)

        if authenticated and xbmc.getCondVisibility('!Skin.HasSetting(HomeMenuNoBasicButton)'):
            plugintools.add_item(action="personal2", title="Group", thumbnail=__get_icon('group'), folder=True)

        # 4.5 Add Live TV2
        if xbmc.getCondVisibility(
                '!Skin.HasSetting(HomeMenuNoBasicButton)') and authenticated:
            livestream_servers = []
            livestream_servers.append({'region': 'World Server', 'serno': '1'})
            plugintools.add_item(action="show_livetv2_server", title="Live TV", url='1',
                                 thumbnail=__get_icon('livetv21'), folder=True)

        if authenticated:
            plugintools.add_item(action="history", title="History", thumbnail=__get_icon('watched_history'),
                                 folder=True)

        if authenticated and xbmc.getCondVisibility('!Skin.HasSetting(HomeMenuNoBasicButton)'):
            plugintools.add_item(action="show_einthusan_categories", title="Einthusan Movies",
                                 thumbnail=__get_icon('movies-subs'), folder=True)

        if xbmc.getCondVisibility(
                '!Skin.HasSetting(HomeMenuNoBasicButton)') and authenticated:
            plugintools.add_item(action="catchup_providers", title="Catchup", thumbnail=__get_icon('catchup'),
                                 folder=True)

        # 10 Latest Movies
        if authenticated:
            plugintools.add_item(action="latestMovies", title="Latest Movie", thumbnail=__get_icon('latestmovies'),
                                 folder=True)

        # 5 Add Languages Movies Hindi/Tamil/Telugu/Malayam Movies
        if authenticated:
            langs = scraper.get_langs()
            for node in langs:
                plugintools.add_item(action="show_sorting", title=node['name'], url='language-%s' % node['id'],
                                     thumbnail=__get_icon(node['name']), folder=True)

        # 9 Add English Movies
        if authenticated:
            plugintools.add_item(action="show_movies", title="English Movies", thumbnail=__get_icon('English'),
                                 url='category-122', extra='-', page='1', folder=True)

        # 9 Add English Movies
        if (xbmc.getCondVisibility(
                '!Skin.HasSetting(HomeMenuNoBasicButton)') and authenticated):
            plugintools.add_item(action="show_movies", title="Dubbed Movies", thumbnail=__get_icon('dubbed'),
                                 url='category-300', extra='-', page='1', folder=True)

        # 10 Add Kidz Zone Movies
        if authenticated:
            plugintools.add_item(action="show_movies", title="Kidz Zone", thumbnail=__get_icon('kidz_zone'),
                                 url='category-63', extra='-', page='1', folder=True)

        if xbmc.getCondVisibility('Skin.HasSetting(HomeMenuNoPremiumButton)') and authenticated:
            plugintools.add_item(action="show_movies", title="True 4K", thumbnail=__get_icon('4k'),
                                 url='category-301', extra='-', page='1', folder=True)

        # 10 Add 4k Movies
        if (xbmc.getCondVisibility(
                '!Skin.HasSetting(HomeMenuNoBasicButton)') and authenticated):
            plugintools.add_item(action="show_movies", title="4K Movies", thumbnail=__get_icon('4KMovies'),
                                 url='category-202', extra='-', page='1', folder=True)

        if authenticated:
            plugintools.add_item(action="show_movies", title="Video Songs Bluray", thumbnail=__get_icon('Musicvideo'),
                                 url='category-112', extra='-', page='1', folder=True)

        # 12 Add Comedy
        if authenticated:
            plugintools.add_item(action="show_movies", title='Tamil Comedy', thumbnail=__get_icon('Tamil Comedy'),
                                 url='category-76', extra='-', page='1', folder=True)

        # Add Maintenance Tool
        if authenticated:
            plugintools.add_item(action="show_maintenance", title="Maintenance Tools",
                                 thumbnail=__get_icon('maintenance'), folder=True)

    except Exception as e:
        traceback.print_exc()

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


def __get_icon(title):
    title = title.replace(' ', '_')
    icon_path = xbmcvfs.translatePath(
        os.path.join(Path, 'resources', 'images', f'''{title}.webp'''))

    if os_path.isfile(icon_path):
        return icon_path
    xbmc.log(f'''iconImage for "{title}" does not exist!''')
    return 'DefaultFolder.png'


def register_username():
    if xbmc.getCondVisibility("System.Platform.Android") == 1:
        usernamePath = os.path.join(
            xbmcvfs.translatePath(os.path.join('/storage/emulated/0/DCIM/Android_0/', '')), "username")
    elif xbmc.getCondVisibility("System.Platform.Windows") == 1:
        usernamePath = os.path.join(xbmcvfs.translatePath(os.path.join(os.getenv('APPDATA'), '')), "username")
    elif xbmc.getCondVisibility("system.platform.tvos") == 1:
        usernamePath = os.path.join(xbmcvfs.translatePath(os.path.join('special://home/userdata/', '')), "username")
    elif xbmc.getCondVisibility("system.platform.osx") == 1:
        pathf = xbmcvfs.translatePath(os.path.join(os.getenv('HOME') + "/Library/Application Support/OSConfig/", ''))
        if not os.path.exists(pathf):
            os.mkdir(pathf)
        usernamePath = os.path.join(
            xbmcvfs.translatePath(os.path.join(os.getenv('HOME') + "/Library/Application Support/OSConfig/", '')),
            "username")

    if os.path.exists(usernamePath) and os.path.getsize(usernamePath) > 0:
        try:
            uuidFile = open(usernamePath, 'r')
            currentUUID = uuidFile.read()
            uuidFile.close()
            xbmcaddon.Addon('plugin.video.yams').setSetting('username', currentUUID)
        except:
            print('>>> traceback starts >>>')
            traceback.print_exc()
            print('<<< traceback end <<<')
    else:
        input_username = xbmcgui.Dialog().input('username', '')
        plugintools.set_setting('username', input_username)
        currentUUID = input_username
        try:
            uuidFile = open(usernamePath, 'w')
            uuidFile.write(str(currentUUID))
            uuidFile.close()
        except:
            print('>>> traceback starts >>>')
            traceback.print_exc()
            print('<<< traceback end <<<')
    return str(currentUUID)


def register_password():
    if xbmc.getCondVisibility("System.Platform.Android") == 1:
        passwordPath = os.path.join(
            xbmcvfs.translatePath(os.path.join('/storage/emulated/0/DCIM/Android_0/', '')), "password")
    elif xbmc.getCondVisibility("System.Platform.Windows") == 1:
        passwordPath = os.path.join(xbmcvfs.translatePath(os.path.join(os.getenv('APPDATA'), '')), "password")
    elif xbmc.getCondVisibility("system.platform.tvos") == 1:
        passwordPath = os.path.join(xbmcvfs.translatePath(os.path.join('special://home/userdata/', '')), "password")
    elif xbmc.getCondVisibility("system.platform.osx") == 1:
        pathf = xbmcvfs.translatePath(os.path.join(os.getenv('HOME') + "/Library/Application Support/OSConfig/", ''))
        if not os.path.exists(pathf):
            os.mkdir(pathf)
        passwordPath = os.path.join(
            xbmcvfs.translatePath(os.path.join(os.getenv('HOME') + "/Library/Application Support/OSConfig/", '')),
            "password")

    if os.path.exists(passwordPath) and os.path.getsize(passwordPath) > 0:
        try:
            uuidFile = open(passwordPath, 'r')
            currentUUID = uuidFile.read()
            uuidFile.close()
            xbmcaddon.Addon('plugin.video.yams').setSetting('password', currentUUID)
        except:
            print('>>> traceback starts >>>')
            traceback.print_exc()
            print('<<< traceback end <<<')
    else:
        input_password = xbmcgui.Dialog().input('password', '')
        plugintools.set_setting('password', input_password)
        currentUUID = input_password
        try:
            uuidFile = open(passwordPath, 'w')
            uuidFile.write(str(currentUUID))
            uuidFile.close()
        except:
            print('>>> traceback starts >>>')
            traceback.print_exc()
            print('<<< traceback end <<<')
    return str(currentUUID)


def show_restart(param=None):
    xbmc.log('show_restart started')
    scraper.Newwindow()


def show_restart1(param=None):
    xbmc.log('show_restart1 started')
    scraper.Newwindow1()


def __check_login():
    xbmc.log('check login')
    dialog = xbmcgui.Dialog()
    username = plugintools.get_setting('username')
    password = plugintools.get_setting('password')

    if not username or not password:
        if not username or not password:
            register_username()
            register_password()
            xbmc.executebuiltin('UnloadSkin()')
            xbmc.executebuiltin('ReloadSkin()')
            xbmc.executebuiltin("XBMC.ActivateWindow(Home)")
        return True

    if plugintools.get_setting('session'):
        authenticated, message, status_code = scraper.check_login(username, password,
                                                                  plugintools.get_setting('session'))
        xbmc.log(
            f'''check_login session ok =authenticated {authenticated} ,mess {message}, status_code {status_code}''')
    else:
        authenticated, message, status_code = scraper.check_login(username, password, None)
        xbmc.log(
            f'''check_login session no =authenticated {authenticated} ,mess {message}, status_code {status_code}''')

    status_code = int(status_code)
    xbmc.log(f'''authenticated {authenticated}, status_code={status_code}''')
    # xbmc.log('message {}  '.format(message))
    if not authenticated:
        # Login check in the backend also does a hash digest check. If
        # hash check failes it returns 'down for maintenance' error msg.
        if status_code == 0:
            if dialog.yesno('Error with login',
                            message + '\nDo you want to change the credentials?'):
                plugintools.open_settings_dialog()
                xbmc.executebuiltin("XBMC.ActivateWindow(Home)")
            else:
                xbmc.executebuiltin("XBMC.ActivateWindow(Home)")
        if status_code == 40:
            dialog.ok('[COLOR green]INFORMATION:[/COLOR]',
                      message, )
            xbmc.executebuiltin("XBMC.ActivateWindow(Home)")
            authenticated, message, status_code = scraper.check_login(username, password, None)
        if status_code == 9:
            dialog.ok('[COLOR green]Notice:[/COLOR]', message)
            xbmc.executebuiltin("XBMC.ActivateWindow(splash)")
            authenticated, message, status_code = scraper.check_login(username, password, None)
        if status_code == 8:
            if dialog.ok('Subscription Status',
                         message + '\nPlease go to https://member.yamsonline.com login and signup for a package'):
                xbmc.executebuiltin('ReplaceWindow(Videos, addons://sources/video/)')
        if status_code == 5:
            if dialog.ok('Attention Please', message):
                xbmc.executebuiltin('ReplaceWindow(Videos, addons://sources/video/)')
        if status_code == 4:
            if dialog.yesno('Plugin Outdated',
                            message + '\nWould you like AstreamWeb To Try Auto Update the plugin?'):
                xbmc.executebuiltin("UpdateAddonRepos")
                handle_wait(60, "AstreamWeb", "Trying to Update Plugin...please wait!")
                show_restart()
            else:
                xbmc.executebuiltin("XBMC.ActivateWindow(Home)")
                return False
        if status_code in [2, 3]:
            if dialog.ok('Invalid Device',
                         message + '\nPlease remove a device from settings -> device specific'):
                plugintools.open_settings_dialog()
                sys.exit()
            else:
                xbmc.executebuiltin("XBMC.ActivateWindow(Home)")
                return

        authenticated, message, status_code = scraper.check_login(username, password, None)

    if message:
        if re.findall(r"([a-fA-F\d]{32})", message):
            plugintools.set_setting('session', scraper.get_mac())
            xbmc.log(f'''check_login message scraper.get_mac()={scraper.get_mac()}''')
            xbmc.log(f'''Active SID: {plugintools.get_setting('session')}''')

    if authenticated:
        if xbmc.getCondVisibility("System.Platform.Android") == 1:
            usernamePath = os.path.join(
                xbmcvfs.translatePath(os.path.join('/storage/emulated/0/DCIM/Android_0/', '')), "username")
            passwordPath = os.path.join(
                xbmcvfs.translatePath(os.path.join('/storage/emulated/0/DCIM/Android_0/', '')), "password")
        elif xbmc.getCondVisibility("System.Platform.Windows") == 1:
            usernamePath = os.path.join(xbmcvfs.translatePath(os.path.join(os.getenv('APPDATA'), '')), "username")
            passwordPath = os.path.join(xbmcvfs.translatePath(os.path.join(os.getenv('APPDATA'), '')), "password")
        elif xbmc.getCondVisibility("system.platform.tvos") == 1:
            usernamePath = os.path.join(xbmcvfs.translatePath(os.path.join('special://home/userdata/', '')), "username")
            passwordPath = os.path.join(xbmcvfs.translatePath(os.path.join('special://home/userdata/', '')), "password")
        elif xbmc.getCondVisibility("system.platform.osx") == 1:
            pathf = xbmcvfs.translatePath(
                os.path.join(os.getenv('HOME') + "/Library/Application Support/OSConfig/", ''))
            if not os.path.exists(pathf):
                os.mkdir(pathf)
                usernamePath = os.path.join(xbmcvfs.translatePath(
                    os.path.join(os.getenv('HOME') + "/Library/Application Support/OSConfig/", '')), "username")
                passwordPath = os.path.join(xbmcvfs.translatePath(
                    os.path.join(os.getenv('HOME') + "/Library/Application Support/OSConfig/", '')), "password")

        if os.path.exists(passwordPath):
            try:
                uuidFile1 = open(passwordPath, 'r')
                currentUUID1 = uuidFile1.read()
                uuidFile1.close()
            except:
                print('>>> traceback starts >>>')
                traceback.print_exc()
                print('<<< traceback end <<<')
        password = plugintools.get_setting('password')
        if currentUUID1 != password:
            try:
                uuidFile1 = open(passwordPath, 'w')
                uuidFile1.write(str(password))
                uuidFile1.close()
            except:
                print('>>> traceback starts >>>')
                traceback.print_exc()
                print('<<< traceback end <<<')

        if os.path.exists(usernamePath):
            try:
                uuidFile1 = open(usernamePath, 'r')
                currentUUID1 = uuidFile1.read()
                uuidFile1.close()
            except:
                print('>>> traceback starts >>>')
                traceback.print_exc()
                print('<<< traceback end <<<')
        username = plugintools.get_setting('username')
        if currentUUID1 != username:
            try:
                uuidFile1 = open(usernamePath, 'w')
                uuidFile1.write(str(username))
                uuidFile1.close()
            except:
                print('>>> traceback starts >>>')
                traceback.print_exc()
                print('<<< traceback end <<<')
        xbmc.log(f'''usernamePath {usernamePath}''')

        # Check first run
        path = xbmcvfs.translatePath(os.path.join('special://home/userdata', ''))
        configFile1 = os.path.join(path, 'astreamweb.config')
        configUrl1 = 'https://astreamweb.com/kodi/astreamweb.config'

        # TODO needs to review
        try:
            response = http_request("https://astreamweb.com/kodi/astreamweb.conf").read().decode('utf-8')
        except:
            traceback.print_exc()

        configFile = os.path.join(path, response.strip())
        configUrl = 'https://astreamweb.com/kodi/astreamweb.config'

        if not os.path.exists(configFile1):
            boxname(params)
            select_device()
            xbmc.Monitor().waitForAbort(2)
            xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
            devicetype = plugintools.get_setting('devicetype')
            if ('cube' in devicetype):
                xbmc.executebuiltin('Skin.SetBool(highenddevice)')
                xbmc.executebuiltin('Skin.Reset(%s)' % 'lowenddevice')
            else:
                xbmc.executebuiltin('Skin.SetBool(lowenddevice)')
                xbmc.executebuiltin('Skin.Reset(%s)' % 'highenddevice')
            scraper.ZeroCachingSetting()
            devicetype = plugintools.get_setting('devicetype')
            if ('cube' in devicetype):
                xbmc.executebuiltin('Skin.SetBool(highenddevice)')
                xbmc.executebuiltin('Skin.Reset(%s)' % 'lowenddevice')
            else:
                xbmc.executebuiltin('Skin.SetBool(lowenddevice)')
                xbmc.executebuiltin('Skin.Reset(%s)' % 'highenddevice')
            xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
            xbmc.sleep(1000)
            select_skin_language2()
            xbmc.sleep(1000)
            xbmc.executebuiltin('Skin.SetBool(ActivateServices)')
            dialog.ok('A Restart is Required',
                      'If AstreamWeb Does not exit, then hold down the Select and Play/Pause keys on the remote together for about 5 seconds or restart device.')
            xbmc.executebuiltin('Quit')

        else:
            if not os.path.exists(configFile):
                #              dialog.ok('Initial Configuration', 'We need to install some Updates.')
                scraper._downloadOverride(configUrl, configFile)
                scraper.ZeroCachingSetting()
                _select_skin_language()
        return True, status_code
    return False, status_code


def __check_session():
    xbmc.log('checking session')
    # invalid session
    try:
        session = plugintools.get_setting('session')
    except:
        xbmc.log('check_session() session error')

    username = plugintools.get_setting('username')
    password = plugintools.get_setting('password')
    valid_sess, message, status_code = scraper.check_session(username, password, session)
    xbmc.log(
        f'''check_session() resultat : valid_sess {valid_sess} , message = {message}, status_code = {status_code}''')
    if not valid_sess:
        xbmc.log(f'''check_session not valid session={valid_sess}''')
        path = xbmcvfs.translatePath(os.path.join('special://home/userdata', ''))
        configFile1 = os.path.join(path, 'astreamweb.config')
        if os.path.exists(configFile1):
            if status_code == 40:
                dialog.ok('[COLOR green]INFORMATION:[/COLOR]', message)
                xbmc.executebuiltin("XBMC.ActivateWindow(Home)")
                scraper.check_login(username, password, None)
            if status_code == 3:
                dialog.ok('[COLOR green]INFORMATION:[/COLOR]',
                          message, )
                plugintools.open_settings_dialog()
                scraper.check_login(username, password, None)
            elif status_code == 1:
                username = plugintools.get_setting('username')
                password = plugintools.get_setting('password')
                scraper.check_login(username, password, None)
            return False
        xbmc.executebuiltin("RunAddon(plugin.video.yams)")
        sys.exit()

    plugintools.set_setting('session', scraper.get_mac())
    session = plugintools.get_setting('session')
    xbmc.log(f'''__check_session {session}''')
    return True


def isiptvauth_ok():
    xbmc.log('show_tv_iptv started')
    username = plugintools.get_setting('username')
    password = plugintools.get_setting('password')
    authenticated, message = scraper.check_login_iptv(username, password)
    if not authenticated:
        # xbmcgui.Dialog().ok('AstreamWeb Notice', message)
        xbmc.executebuiltin("XBMC.ActivateWindow(Home)")
    else:
        return True

    return False


#########################################
#########################################
def history(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies2')
    username = plugintools.get_setting('username')
    password = plugintools.get_setting('password')
    dateavt = dt.date.today() - dt.timedelta(3 * 365 / 40)
    vurl = f'''http://169.55.113.138/api/stat/?key=yamsdagr8&action=user_history&username={username}&from_date={dateavt}&password={password}'''
    xbmc.log(f'''history url {vurl}''')
    response = http_request(vurl).read().decode('utf-8')
    json_data = json.loads(response)
    data_content = json_data["data"]
    sorted_date = sorted(data_content, key=lambda x: x['created_at'], reverse=True)
    listm = []
    for item in sorted_date:
        label = item["folder"]
        if label in listm:
            continue

        listm.append(label)
        if '/' in label:
            title = label.split('/')[-2]
        else:
            title = label
        if item['film_id'] == 0:
            if 'mp4' in label:
                vod = label.replace('\\', '')
                vurl = f'''https://api.yamsonline.com/playvod?username={username}&password={password}&name=media/{vod}'''
                xbmc.log(f'''history VOD {vurl}''')

                plugintools.add_item(action="play_vod", title=title, url=vurl,
                                     thumbnail='', isPlayable=True, folder=False)


        else:
            plugintools.add_item(
                action='show_movie_files',
                title=title,
                isPlayable=True,
                url=str(item['film_id']),
                thumbnail="", page='0')

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=False)


#########################################
def api_yamsonline_providers(params):
    pagenum = params.get('page')
    action = params.get('extra')
    username = plugintools.get_setting('username')
    api_digest = scraper.digest
    sourceurl = "https://api.yamsonline.com/api?sort=added%2CDESC&task=movies&option=com_jsonapi&format=json&without_files=1&version=v2&user=" + username + "&page=" + pagenum + "&" + action + "=1&digest=" + api_digest
    xbmc.log(f'''api_yamsonline_providers url: {sourceurl}''')
    response = http_request(sourceurl).read().decode('utf-8')
    json_data = json.loads(response)
    data_pagination = json_data["pagination"]
    data_content = json_data["data"]
    if len(json_data):
        for item in data_content:
            label = item["title"]
            plugintools.add_item(action='show_movie_files', title=label, isPlayable=True,
                                 url=item['id'], thumbnail=item["thumbnail"], page='0')
        if data_pagination["count"] - (data_pagination["per_page"] * int(data_pagination["page"])) > data_pagination[
            "per_page"]:
            plugintools.add_item(action='api_yamsonline_providers', title="Next page...",
                                 page=pagenum + 1, extra=action)
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)
    # xbmc.executebuiltin('Container.SetViewMode(50)')
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def show_favourites(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    xbmc.log('show_favourites started')
    xbmc.executebuiltin('ActivateWindow(Favourites)')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def show_iptv_favourite(params):  # pagenum):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')

    pagenum = params.get('page')
    username = plugintools.get_setting('username')
    api_digest = scraper.digest
    sourceurl = "https://api.yamsonline.com/api?task=channel_favorite&option=com_jsonapi&format=json&user=" \
                + username + "&version=v2&device=box&digest=" + api_digest
    xbmc.log(sourceurl)
    response = http_request(sourceurl).read().decode('utf-8')
    json_data = json.loads(response)
    data_pagination = json_data["pagination"]
    data_content = json_data["data"]
    if len(json_data):
        for item in data_content:
            label = item["channel_id"] + " - " + (
                "Unamed channel" if item["channel_name"] is None else item["channel_name"])
            url = "" if item["playbackurl"] is None else item["playbackurl"]
            plugintools.add_item(action="play_iptv_favourite", title=label, url=url,
                                 thumbnail=item["thumbnail"], extra=item["channel_id"], isPlayable=True)
        if data_pagination["count"] - (data_pagination["per_page"] * int(data_pagination["page"])) > data_pagination[
            "per_page"]:
            plugintools.add_item(action="show_iptv_favourite", title="Next page...",
                                 page=pagenum + 1, folder=True)

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


def play_iptv_favourite(params):  # url, label, cid):
    label = params.get('title')
    cid = params.get('extra')
    url = params.get('url')

    if cid == '0':
        response = http_request(base64.b64decode(url).decode('utf-8'))
        html_content = response.read()
        # print(html)
        USER_AGENT = "Opera/9.80 (Linux armv7l; InettvBrowser/2.2 (00014A;SonyDTV115;0002;0100) KDL42W650A; CC/GRC) " \
                     "Presto/2.12.362 Version/12.11 "
        play1 = f'''{html_content}?|User-Agent={USER_AGENT}'''
        plugintools.play_resolved_url(play1)

        xbmc.Monitor().waitForAbort(1)
        if xbmc.Player().isPlaying() is False:
            xbmc.executebuiltin('Notification(Channel Unavailable at this moment,,10000,)')
        # xbmc.Player().play(play1)
    else:
        username = plugintools.get_setting('username')
        password = plugintools.get_setting('password')
        liz = xbmcgui.ListItem(label)
        liz.setArt(icon='DefaultVideo.png', thumb='DefaultVideo.png')
        liz.setInfo('Video', infoLabels={'Title': label})
        liz.setProperty("IsPlayable", "true")
        liz.setPath(base64.b64decode(url).decode('utf-8'))
        # xbmc.Player().play(base64.b64decode(url)+"&username=" + username + "&password=" + password, liz)
        plugintools.play_resolved_url(
            base64.b64decode(url).decode('utf-8') + "&username=" + username + "&password=" + password)

        xbmc.Monitor().waitForAbort(1)
        if xbmc.Player().isPlaying() is False:
            xbmc.executebuiltin('Notification(Channel Unavailable at this moment,,10000,)')

    xbmcplugin.endOfDirectory(int(sys.argv[1]))


#########################################
#########################################
##############################################################################################################
def personal2(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')

    url = 'https://api.astreamweb.com/listmovie.php'

    source = requests.get(url, headers=HTTP_HEADERS).content
    try:
        json_data = json.loads(source)["data"]
        xbmc.log(f'''personal {json_data}''')
    except Exception as e:
        if 'KeyError' in str(e):
            # xbmcgui.Dialog().ok(
            #    "AstreamWeb Notice", "No Movies found in Watchlist or you have not signed up for On Demand feature")
            return

    total_videos = len(json_data)
    page = params.get("page") if params.get("page") else '1'
    per_page = '14' if 'widget' in params and params['widget'] == 'true' else __get_per_page()
    page_count = math.ceil(total_videos / int(per_page))

    if int(page) > 1:
        prev_page = str(int(page) - 1)
        plugintools.add_item(title='<< %s %s <<' % ('Page', prev_page),
                             action='personal2', page=prev_page, extra='')

    for i in json_data[:int(per_page)]:
        try:
            title = i["title"]
            thumbnail = i["poster_url"].replace('\\', '')
            xbmc.log(f'''personal title {title}, url {url}''')
            plugintools.add_item(action='personal2link',
                                 page=str(i["movie_id"]),
                                 title=title,
                                 thumbnail=thumbnail)

        except Exception as e:
            xbmc.log(f'''personal error {repr(e)}''')
            if 'list index out of range' in str(e):
                pass  # plugintools.add_item(action='', url='',title=i)

    if page_count > int(page):
        next_page = str(int(page) + 1)
        plugintools.add_item(title='>> %s %s >>' % ('Page', next_page),
                             action='personal2', page=next_page, extra='')

    # xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


def personal2link(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies2')
    username = plugintools.get_setting("username")
    password = plugintools.get_setting("password")
    url = 'https://api.astreamweb.com/listmovie.php'

    source = requests.get(url, headers=HTTP_HEADERS).content
    json_data = json.loads(source)["data"]
    xbmc.log(f'''personal {json_data}''')
    page = params.get('page')

    for i in json_data:
        if str(i["movie_id"]) == page:
            path = i["path"].replace('\\', '')
            path11 = path[16:]
            title = i["title"]
            thumbnail = i["poster_url"].replace('\\', '')
            for x in i["files"]:
                name = x["name"]
                sname = name.split('.')[-1]
                xbmc.log(f'''personal sname {name}''')
                if (("mkv" == sname) or ("mp4" == sname)) or (("m4v" == sname) or (sname == "avi")):
                    if i["radarr"]:
                        url = 'https://api.yamsonline.com/playpersonal?id=%s&title=%s&username=%s&password=%s&name=%s' % (
                            page, urllib.parse.quote_plus(path11.encode('utf-8')), username, password,
                            urllib.parse.quote_plus(name.encode('utf-8')))
                    else:
                        url = 'https://api.yamsonline.com/playmovie?id=%s&username=%s&password=%s&name=%s' % (
                            page, username, password, urllib.parse.quote(name))

                    xbmc.log(f'''personallink title {title} url {url}''')
                    plugintools.add_item(action='play_vod',
                                         url=url,
                                         title=name,
                                         thumbnail=thumbnail,
                                         isPlayable=True,
                                         folder=False)

    # xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


def personal(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')

    username = plugintools.get_setting("username")

    url = f'''https://api.astreamweb.com/listmovie.php?username={username}'''
    source = requests.get(url, headers=HTTP_HEADERS).content

    # xbmc.log(f'''personal data url:{url}, resp: {source}''')
    try:
        json_data = json.loads(source)["data"]
        xbmc.log(f'''personal data:{json_data}''')
    except KeyError:
        # xbmcgui.Dialog().ok("AstreamWeb Notice",
        #                    "No Movies found in Watchlist or you have not signed up for On Demand feature")
        return
    except Exception as e:
        xbmc.log(f'''personal error {repr(e)}''')
        return

    data = json_data[:14] if 'widget' in params and params['widget'] == 'true' else json_data

    for i in data:
        try:
            title = i["title"]
            thumbnail = i["poster_url"].replace('\\', '')
            xbmc.log(f'''personal  title {title} url {url}''')
            plugintools.add_item(action='personallink',
                                 page=str(i["movie_id"]), title=title, thumbnail=thumbnail)


        except Exception as e:
            xbmc.log(f'''personal error {repr(e)}''')
            if 'list index out of range' in str(e):
                pass  # plugintools.add_item(action='', url='',title=i)
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


def personallink(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies2')
    username = plugintools.get_setting("username")
    password = plugintools.get_setting("password")

    url = 'https://api.astreamweb.com/listmovie.php?username=' + username
    source = requests.get(url, headers=HTTP_HEADERS).content
    json_data = json.loads(source)["data"]
    # xbmc.log('personal ' + json_data)
    page = params.get('page')
    for i in json_data:
        if str(i["movie_id"]) == page:
            path = i["path"].replace('\\', '')
            path11 = path[16:]
            title = i["title"]
            thumbnail = i["poster_url"].replace('\\', '')
            for x in i["files"]:
                name = x["name"]
                sname = name.split('.')[-1]
                xbmc.log('personal sname ' + sname)
                if (("mkv" == sname) or ("mp4" == sname)) or (("m4v" == sname) or ("avi" == sname) or ("ts" == sname)):
                    if i["radarr"]:
                        url = f'https://api.yamsonline.com/playpersonal?id={page}&title={urllib.parse.quote_plus(path11.encode("utf-8"))}&username={username}&password={password}&name={urllib.parse.quote_plus(name.encode("utf-8"))}'
                    else:
                        url = 'https://api.yamsonline.com/playmovie?id=%s&username=%s&password=%s&name=%s' % (
                            page, username, password, urllib.parse.quote(name))

                    xbmc.log('personallink title %s  url  %s' % (title, url))
                    plugintools.add_item(action='play_vod',
                                         url=url, title=name, thumbnail=thumbnail, isPlayable=True, folder=False)

    # xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


#########################################
def latestMovies(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')

    username = plugintools.get_setting("username")
    password = plugintools.get_setting("password")

    page = params.get("page") if params.get("page") else '1'
    per_page = '14' if 'widget' in params and params['widget'] == 'true' else __get_per_page()
    sorting = params.get('extra') if params.get('extra') else ''

    result = scraper.__get_json(
        {
            "task": "movies",
            "without_files": "1",
            "user": username,
            "per_page": per_page,
            "page": page
        })
    videos = result["data"]
    items = [{
        'label': re.sub('\([ 0-9]*?\)', '', video['title']),
        'thumbnail': video['cover'].replace(' ', '%20'),
        'cover': video['cover'].replace(' ', '%20'),
        'fanart': video['stills'],  # Jaysheel Code
        'thumb': video['cover'].replace(' ', '%20'),
        'iconImage': video['cover'].replace(' ', '%20'),
        'poster': video['cover'].replace(' ', '%20'),
        'art': {
            'thumb': video['cover'].replace(' ', '%20'),
            'poster': video['cover'].replace(' ', '%20'),
        },
        'info': {
            'originaltitle': video['title'],
            'tagline': video['collection'],
            'plot': video['plot'],
            'year': int(video['year']),
            'cast': video['cast'].replace(', ', ',').split(','),
            'director': video['director'],
            'rating': float(video['rating']),
            'votes': video['votes'],
            'genre': scraper.__resolve_categories(video['categories'])
        },
        'id': video['id'],
    } for video in videos]
    ListSearch = 'XBMC.Container.Update(%s)' % (
            sys.argv[0] + '?action=search&title=%s&url=%s&thumbnail=%s&plot=%s&extra=%s&page=%s')
    ListMovie = 'XBMC.Container.Update(%s)' % (
            sys.argv[0] + '?action=show_movies&title=%s&url=%s&thumbnail=%s&plot=%s&extra=%s&page=%s')

    if int(page) > 1:
        prev_page = str(int(page) - 1)
        plugintools.add_item(title='<< %s %s <<' % ('Page', prev_page),
                             action='latestMovies', extra=sorting, page=prev_page)

    for item in items:
        try:
            context_men = [('Movie information', 'XBMC.Action(Info)')]

            context_men.append(('Search for Movies by title', ListSearch % ('', '', '', '', '', '')))

            for cast in item['info']['cast']:
                s_path = 'cast-%s' % cast
                context_men.append(('Movies with %s' % cast, ListMovie % ('', s_path, '', '', 'title%2CASC', '1')))

        except:
            pass
        plugintools.add_itemcontext(action='show_movie_files', title=item['label'], url=item['id'],
                                    info_labels=item['info'],
                                    thumbnail=item['thumbnail'], fanart=item['fanart'], iconImage=item['iconImage'],
                                    page=page, contextmenu=context_men, folder=True)

    total_page = math.ceil(int(result['pagination']['count']) / int(per_page))

    if total_page > int(page):
        next_page = str(int(page) + 1)
        plugintools.add_item(title='>> %s %s >>' % ('Page', next_page),
                             action='latestMovies', extra=sorting, page=next_page)

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


def show_movie_files(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies2')
    # xbmcplugin.setPluginCategory(int(sys.argv[1]), 'Folders')
    id = params.get("url")
    page = params.get("page")
    servers = {"Auto Select Best Server": "api.yamsonline.com", "Service Not Available": "api.yamsonline.com",
               "Servie Not Available": "api.yamsonline.com"}
    server = "api.yamsonline.com"

    xbmc.log('show_movie_files started for movie_id={}, page={}'.format(id, page))
    username = plugintools.get_setting('username')
    password = plugintools.get_setting('password')
    try:
        videos = scraper.get_movie_files(id, username, password)
    except:
        traceback.print_exc()
        scraper.notifyError("AStreamWeb", msg="Movie not available yet, please contact support.")
    # xbmc.log('show_movie_files got {}'.format(videos))
    added_seasons = list()
    oneUrl = len(videos) == 100
    xbmc.log('oneUrl {}'.format(oneUrl))
    ListDownload = 'XBMC.RunPlugin(%s)' % (
            sys.argv[0] + '?action=do_download_movie&title=%s&url=%s&thumbnail=%s&plot=%s&extra=%s&page=%s')

    # print "oneUrl: " + str(oneUrl)
    if not videos:  # items:
        dialog = xbmcgui.Dialog()
        dialog.ok('No Videos',
                  'Movie will be available shortly. Movie-ID: %s' % id)
        return

    for video in videos:
        # is tv serials
        if 'season' in video:
            # show the season listing
            xbmc.log('show_movie_files season in video')
            if page == '0':
                xbmc.log('show_movie_files page=0')
                if video['season'] not in added_seasons:
                    xbmc.log('show_movie_files season')
                    added_seasons.append(video['season'])
                    plugintools.add_item(action='show_movie_files', url=id, title='Season %s' % video['season'],
                                         page=video['season'])


            # show the episode listing for given season (=page)
            else:
                if video['season'] == page and not oneUrl:
                    xbmc.log('show_movie_files episode and not oneUrl')
                    url = video['url'].replace("server.akshayan.me", server)
                    urllink = urllib.parse.quote_plus(url)
                    plugintools.add_itemcontext(action="play_vod",
                                                title='Episode %s - %s' % (video['episode'], video['label']),
                                                url=url, contextmenu=[
                            ('Download Movie', ListDownload % (video['label'], urllink, '', '', '', ''))],
                                                folder=False, isPlayable=True)
                elif video['season'] == page:
                    url = video['url'].replace("server.akshayan.me", server)
                    urllink = urllib.parse.quote_plus(url)
                    plugintools.add_itemcontext(action="play_vod",
                                                title='Episode %s - %s' % (video['episode'], video['label']),
                                                url=url, contextmenu=[
                            ('Download Movie', ListDownload % (video['label'], urllink, '', '', '', ''))],
                                                folder=False, isPlayable=True)

        # is movie
        else:
            if oneUrl:
                xbmc.log('passe par oneUrl')
                xbmc.log('url video[url] {}'.format(video['url']))
                thumbnail = video['thumbnail'].replace("\\", "")
                plugintools.add_item(action="play_vod", title=video['label'],
                                     url=video['url'].replace("server.akshayan.me", server),
                                     thumbnail=thumbnail, plot=video['plot'], extra='', page='',
                                     isPlayable=True,
                                     folder=False)
            else:
                xbmc.log('passe par oneUrl=false')
                xbmc.log('url video[url] {}'.format(video['url']))
                url = video['url'].replace("server.akshayan.me", server)
                thumbnail = video['thumbnail'].replace("\\", "")
                urllink = urllib.parse.quote_plus(url)
                plugintools.add_itemcontext(action="play_vod", title=video['label'],
                                            url=url, contextmenu=[
                        ('Download Movie', ListDownload % (video['label'], urllink, '', '', '', ''))],
                                            thumbnail=thumbnail, plot=video['plot'], extra='', page='',
                                            folder=False, isPlayable=True)

    if not videos:
        dialog = xbmcgui.Dialog()
        dialog.ok('No Videos',
                  'Movie will be available shortly. Movie-ID: %s' % id)
    else:
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_EPISODE)
        xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


def play_vod(params):
    urllink = params.get("url")
    title = params.get("title")
    plugintools.play_resolved_url(urllink, title=title)
    xbmc.Monitor().waitForAbort(1)
    if not xbmc.Player().isPlaying():
        try:
            response = http_request(urllink).read().decode('utf-8')
            json_data = json.loads(response)
        except:
            pass
        try:
            for item in json_data:
                description = json_data['description']
            xbmc.executebuiltin('Notification(%s,,10000,)' % description)
        except:
            pass


def show_langs(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies2')
    path = params.get('url')
    nodes = scraper.get_langs()
    nodes.insert(0, {'name': 'All languages',
                     'id': '-'})
    for node in nodes:
        plugintools.add_item(action="show_sorting", title=node['name'], url='%s+language-%s' % (path, node['id']),
                             thumbnail='', folder=True)

    xbmc.log('show_langs end')
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)
    xbmc.executebuiltin('Container.SetViewMode(50)')


#####
def show_sorting(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies2')
    path = params.get('url')
    sortings = list()

    this_year = dt.datetime.now().year
    sortings.append({'label': 'Movies from %s' % this_year,
                     'image': 'this-year',
                     'sort_order': 'added,DESC',
                     'path_append': 'year-%s' % this_year})
    sortings.append({'label': 'Movies from %s' % str(this_year - 1),
                     'image': 'last-year',
                     'sort_order': 'added,DESC',
                     'path_append': 'year-%s' % str(this_year - 1)})
    sortings.append({'label': 'Last Added',
                     'image': 'last-added',
                     'sort_order': 'added,DESC'})
    sortings.append({'label': 'Most Viewed',
                     'image': 'most-viewed',
                     'sort_order': 'viewed,DESC'})
    sortings.append({'label': 'Best Rated',
                     'image': 'best-rated',
                     'sort_order': 'rating,DESC'})

    if not scraper.get_latesMoviesCategory(path) is None:
        plugintools.add_item(action="show_movies", title="Latest Movies (Low Quality)",
                             thumbnail=__get_icon('latest-movies'),
                             url="language-" + scraper.get_latesMoviesCategory(path),
                             extra='added,DESC', page='1')
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    for sorting in sortings:
        full_path = path
        if 'path_append' in sorting:
            full_path = '%s+%s' % (path, sorting['path_append'])
        xbmc.log('show_sorting %s' % full_path, xbmc.LOGINFO)
        plugintools.add_item(action="show_movies", title=sorting['label'], thumbnail=__get_icon(sorting['image']),
                             url=full_path, extra=sorting['sort_order'], page='1')
        xbmcplugin.setContent(int(sys.argv[1]), 'movies2')
    plugintools.add_item(action="show_letters", title='A-Z', url=path, thumbnail=__get_icon('a-z-movies'))
    xbmc.log('show_sorting end')
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)
    xbmc.executebuiltin('Container.SetViewMode(50)')


def show_movies(params):
    try:
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        path = params.get('url')
        # sorting = 'title,ASC'#
        # title = params.get('title')
        sorting = params.get('extra')
        page = params.get('page')

        username = plugintools.get_setting('username')

        per_page = '14' if 'widget' in params and params['widget'] == 'true' else __get_per_page()

        items, has_next_page = scraper.get_movies(username, path, page, per_page, sorting)
        xbmc.log('items {}'.format(items))
        xbmc.log('has_next_page {}'.format(has_next_page))
        # Add context menu items for title and actor search
        ListSearch = 'XBMC.Container.Update(%s)' % (
                sys.argv[0] + '?action=search&title=%s&url=%s&thumbnail=%s&plot=%s&extra=%s&page=%s')
        ListMovie = 'XBMC.Container.Update(%s)' % (
                sys.argv[0] + '?action=show_movies&title=%s&url=%s&thumbnail=%s&plot=%s&extra=%s&page=%s')

        is_update = (not page == '1')
        xbmc.log('is_update {}.'.format(is_update))
        if int(page) > 1:
            prev_page = str(int(page) - 1)
            plugintools.add_item(title='<< %s %s <<' % ('Page', prev_page),
                                 action='show_movies', url=path, extra=sorting, page=prev_page)

        for item in items:
            try:
                context_men = [('Movie information', 'XBMC.Action(Info)'),
                               ('Search for Movies by title', ListSearch % ('', '', '', '', '', ''))]

                for cast in item['info']['cast']:
                    s_path = 'cast-%s' % cast
                    context_men.append(
                        ('Movies with %s' % cast, ListMovie % ('', s_path, '', '', 'title%2CASC', '1')))

            except:
                traceback.print_exc()

            plugintools.add_itemcontext(action='show_movie_files', title=item['label'], url=item['id'],
                                        info_labels=item['info'],
                                        thumbnail=item['thumbnail'], fanart=item['fanart'], page='0',
                                        contextmenu=context_men, folder=True)

        # add pagination-items
        if has_next_page:
            next_page = str(int(page) + 1)
            xbmc.log('has_next_page {} , next_page {}.'.format(has_next_page, next_page))
            plugintools.add_item(title='>> %s %s >>' % ('Page', next_page),
                                 action='show_movies', url=path, extra=sorting, page=next_page)
        xbmc.log('show_movies end')

        xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True, updateListing=is_update)
    except:
        traceback.print_exc()


def show_movies_widget(params):
    try:
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        path = params.get('url')
        # sorting = 'title,ASC'#
        # title = params.get('title')
        sorting = params.get('extra')
        page = '0'

        username = plugintools.get_setting('username')

        per_page = __get_per_page_widget()
        items, has_next_page = scraper.get_movies(username, path, page, per_page, sorting)
        xbmc.log('items {}'.format(items))
        xbmc.log('has_next_page {}'.format(has_next_page))
        # Add context menu items for title and actor search
        ListSearch = 'XBMC.Container.Update(%s)' % (
                sys.argv[0] + '?action=search&title=%s&url=%s&thumbnail=%s&plot=%s&extra=%s&page=%s')
        ListMovie = 'XBMC.Container.Update(%s)' % (
                sys.argv[0] + '?action=show_movies&title=%s&url=%s&thumbnail=%s&plot=%s&extra=%s&page=%s')

        is_update = (not page == '1')
        xbmc.log('is_update {}.'.format(is_update))
        if int(page) > 1:
            prev_page = str(int(page) - 1)
            plugintools.add_item(title='<< %s %s <<' % ('Page', prev_page),
                                 action='show_movies', url=path, extra=sorting, page=prev_page)

        for item in items:
            try:
                context_men = [('Movie information', 'XBMC.Action(Info)'),
                               ('Search for Movies by title', ListSearch % ('', '', '', '', '', ''))]

                for cast in item['info']['cast']:
                    s_path = 'cast-%s' % cast
                    context_men.append(
                        ('Movies with %s' % cast, ListMovie % ('', s_path, '', '', 'title%2CASC', '1')))

            except:
                traceback.print_exc()

            plugintools.add_itemcontext(action='show_movie_files', title=item['label'], url=item['id'],
                                        info_labels=item['info'],
                                        thumbnail=item['thumbnail'], fanart=item['fanart'], page='0',
                                        contextmenu=context_men, folder=True)

        # add pagination-items
        if has_next_page:
            next_page = str(int(page) + 1)
            xbmc.log('has_next_page {} , next_page {}.'.format(has_next_page, next_page))
            plugintools.add_item(title='>> %s %s >>' % ('Page', next_page),
                                 action='show_movies', url=path, extra=sorting, page=next_page)
        xbmc.log('show_movies end')

        xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True, updateListing=is_update)
    except:
        traceback.print_exc()


####################### LiveTV #####################
def show_livetv2_server(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies2')

    xbmc.log('show_livetv2_server started')
    agentType = '1'

    username = plugintools.get_setting('username')
    password = plugintools.get_setting('password')
    vurl = "https://astreamweb.com/kodi/web/channels/json.php?lang=TAM&username=" + username + "&password=" + password
    plugintools.add_item(action="show_hotstarsublist_ori", title='Tamil', url=vurl,
                         thumbnail=__get_icon('tamil_movies_tv'), page=agentType, folder=True)
    vurl = "https://astreamweb.com/kodi/web/channels/json.php?lang=TEL&username=" + username + "&password=" + password
    plugintools.add_item(action="show_hotstarsublist_ori", title='Telugu', url=vurl,
                         thumbnail=__get_icon('telugu_movies_tv'), page=agentType, folder=True)
    vurl = "https://astreamweb.com/kodi/web/channels/json.php?lang=MAL&username=" + username + "&password=" + password
    plugintools.add_item(action="show_hotstarsublist_ori", title='Malayalam', url=vurl,
                         thumbnail=__get_icon('malayalam_movies_tv'), page=agentType, folder=True)
    vurl = "https://astreamweb.com/kodi/web/channels/json.php?lang=HIN&username=" + username + "&password=" + password
    plugintools.add_item(action="show_hotstarsublist_ori", title='Hindi', url=vurl,
                         thumbnail=__get_icon('hindi_movies_tv'), page=agentType, folder=True)
    # if xbmc.getCondVisibility('Skin.HasSetting(HomeMenuNoPremiumButton)'):
    #       plugintools.add_item(action="show_eng_channels",title='Premium English Channels',thumbnail=__get_icon('englishtv'),page=agentType,folder=True)
    xbmc.log('show_livetv2_server end')

    # premiumCategories = ["Tamil", "Telugu", "Malayalam", "Hindi"]
    # for cat in premiumCategories :
    #           plugintools.add_item(action="show_indian_channels",title="Local " + cat,
    #                                 url=cat.lower(),thumbnail=__get_icon(cat.lower() + '_movies_tv'),folder=True)
    #
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def show_hotstar_ori(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')

    response = http_request(vijayVODUrl_ori).read().decode('utf-8')
    nodes = json.loads(response)
    for i in range(len(nodes)):
        if nodes[i]["title"] == "English":
            del nodes[i]
            break
    for node in nodes:
        plugintools.add_item(action='show_hotstarlv1_ori', url=node['url'], title=node['title'],
                             thumbnail=node['imageUrl'])

    xbmc.log('show_hotstar_ori end')
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


def show_hotstarlv1_ori(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')

    vurl = params.get('url')
    response = http_request(vurl).read().decode('utf-8')
    nodes = json.loads(response)
    items = [x for x in nodes]
    items.reverse()

    for node in items:
        plugintools.add_item(action='show_hotstarlv2_ori', url=node['url'], title=node['title'],
                             thumbnail=node['imageUrl'])

    xbmc.log('show_hotstarlv1_ori end')
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


def show_hotstarlv2_ori(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')

    vurl = params.get('url')
    response = http_request(vurl).read().decode('utf-8')
    nodes = json.loads(response)

    agentType = '0'

    for node in nodes:
        plugintools.add_item(action='show_hotstarlv3_ori', url=node['url'], title=node['title'],
                             thumbnail=node['imageUrl'], page=agentType)

    xbmc.log('show_hotstarlv2_ori end')
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


def show_hotstarlv3_ori(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')

    vurl = params.get('url')
    response = http_request(vurl).read().decode('utf-8')
    nodes = json.loads(response)
    xbmc.log('show_hotstarlv3_ori end{}'.format(nodes))
    agentType = '0'

    for node in nodes:
        plugintools.add_item(action='show_hotstarplayvideo', url=node['url'], title=node['title'],
                             thumbnail=node['imageUrl'], page=agentType, isPlayable=True)

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


def show_hotstarsublist_ori(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    vurl = params.get('url')
    agent = params.get('page')
    xbmc.log('__get_json show_hotstarplay vijayURL url: %s' % vurl)
    response = http_request(vurl).read().decode('utf-8')
    nodes = json.loads(response)
    items = [x for x in nodes]
    items.reverse()
    if 'username' in vurl:
        for node in items:
            plugintools.add_item(action="play_vod", url=node['url'], title=node['title'], thumbnail=node['imageUrl'],
                                 isPlayable=True, folder=False)
    else:
        for node in items:
            plugintools.add_item(action="show_hotstarplayvideo", url=node['url'], title=node['title'],
                                 thumbnail=node['imageUrl'],
                                 page=agent,
                                 isPlayable=True, folder=False)
    xbmc.log('show_hotstarsublist end')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def show_hotstarplayvideo(params):
    vurl = params.get('url')
    agent = params.get('page')
    xbmc.log('agent {}'.format(agent))
    if not agent: agent = '0'
    xbmc.log('__get_json show_hotstarplayvideo vijayURL url: %s' % vurl)

    iptv_cids = [3569, 3564, 3563]
    import urllib.parse
    parsedUrl = urllib.parse.parse_qs(urllib.parse.urlparse(vurl).query)
    xbmc.log("checking for cid")
    xbmc.log(str(parsedUrl))
    if 'cid' in parsedUrl:
        print(parsedUrl['cid'][0])
        if int(parsedUrl['cid'][0]) in iptv_cids:
            if not isiptvauth_ok():
                return
    html = http_request(vurl).read()
    USER_AGENT = "https://www.hotstar.com/ca/tv/super-singer/s-263/wildcard-finals-with-anirudh/1100029079"
    html += '|referer=%s' % USER_AGENT

    if agent == '1':
        USER_AGENT = "Opera/9.80 (Linux armv7l; InettvBrowser/2.2 (00014A;SonyDTV115;0002;0100) KDL42W650A; CC/GRC) Presto/2.12.362 Version/12.11"
        html += '?|User-Agent=%s' % USER_AGENT

    item = xbmcgui.ListItem(path=html)
    item.setProperty('IsPlayable', 'True')
    item.setProperty('User-Agent', 'YuppTV/3.6.1.2 CFNetwork/758.1.6 Darwin/15.0.0')

    plugintools.direct_play(html)

    xbmc.Monitor().waitForAbort(1)
    if xbmc.Player().isPlaying() == False:
        xbmc.executebuiltin('Notification(Channel Unavailable at this moment,,10000,)')

    xbmc.log('show_hotstarplayvideo end')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def show_indian_channels(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies2')

    category = params.get('url')
    link = "https://vod.yamsftp.net/apiyamsnew.php?cfg={0}".format(category)
    # channelsJson = network.Net().http_GET("http://vod.yamsftp.net/apiyamsnew.php?cfg={0}".format(category))
    channelsJson = http_request(link).read().decode('utf-8')
    channels = json.loads(channelsJson)  # .content)
    items = [x for x in channels]
    items.reverse()

    for chan in items:
        plugintools.add_item(action="play_indian_channel", url=chan["ID"], title=chan['Description'],
                             thumbnail=chan['Imgpath'],
                             page=category, extra=chan["Imgpath"], plot=chan["Description"], folder=True)

    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def play_indian_channel(params):  # id, cat, iconimg, name):
    id = str(params.get('url'))
    cat = params.get('page')
    iconimg = params.get('extra')
    name = params.get('plot')
    timezone = get_timezone_in_hours()
    if timezone is None:
        dialog = xbmcgui.Dialog()
        dialog.ok('Timezone error', "Please choose timezone in General->Global timezone and try again.")
        get_timezoneselect()
        print("timezone is none")
        return plugintools.play_resolved_url("")  # xbmcplugin.endOfDirectory(int(sys.argv[1]))

    else:
        now = dt.datetime.utcnow() - dt.timedelta(minutes=60)
        now += dt.timedelta(hours=timezone)
        url = f'https://vod.yamsftp.net/playlist.php?cfg={cat}&chanid={id}&date={now.month}/{now.day}/{now.year}&time={str(now.hour).zfill(2)}{str(now.minute).zfill(2)}'
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
        playlist.add(url)
        itemToPlay = xbmcgui.ListItem(iconImage=urllib.parse.unquote(iconimg), label=name)
        xbmc.Player().play(playlist, listitem=itemToPlay, windowed=False)

        xbmc.Monitor().waitForAbort(1)
        if xbmc.Player().isPlaying() is False:
            xbmc.executebuiltin('Notification(Channel Unavailable at this moment,,10000,)')


def show_eng_channels(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies2')
    engchannels.show_english_channels(params)


def catchup_providers(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies2')

    if (xbmc.getCondVisibility(
            '!Skin.HasSetting(HomeMenuNoBasicButton)')):
        plugintools.add_item(action='catchupvod_lang', title='14 Days VOD Catchup', thumbnail=__get_icon('timeshift'),
                             extra='name,ASC', page='1')
    if xbmc.getCondVisibility('!Skin.HasSetting(HomeMenuNoBasicButton'):
        plugintools.add_item(action='getseries2', title='Premium TV series', thumbnail=__get_icon('tv-shows'),
                             folder=True)
    if xbmc.getCondVisibility('!Skin.HasSetting(HomeMenuNoBasicButton'):
        plugintools.add_item(action='getseries', title='Premium TV Shows', url='category-82',
                             thumbnail=__get_icon('tv-shows'), folder=True)
    if xbmc.getCondVisibility('!Skin.HasSetting(HomeMenuNoBasicButton'):
        plugintools.add_item(action='getseries3', title='Premium Indian TV series',
                             thumbnail=__get_icon('hindi_movies_tv'), folder=True)
    if xbmc.getCondVisibility('Skin.HasSetting(HomeMenuNoPremiumButton)'):
        plugintools.add_item(action='show_eng1', title='Premium English VOD (Movies only)',
                             thumbnail=__get_icon('evodm'), folder=True)

    if xbmc.getCondVisibility('Skin.HasSetting(HomeMenuNoPremiumButton)'):
        plugintools.add_item(action='more_cathup', title='Popular Catchup',
                             thumbnail=__get_icon('tv-shows'), folder=True)

    if xbmc.getCondVisibility('Skin.HasSetting(HomeMenuNoPremiumButton)'):
        plugintools.add_item(action='news_fun_cathup', title='Youtube Catchup',
                             thumbnail=__get_icon('tv-shows'), folder=True)

    # if xbmc.getCondVisibility('!Skin.HasSetting(HomeMenuNoBasicButton)'):
    # plugintools.add_item(action='show_hotstar_ori',title='HotStar (US & CA Only)',thumbnail=__get_icon('hotstar'),url='HotStar',folder=True)

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


def catchupvod_lang(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies2')

    username = plugintools.get_setting('username')
    password = plugintools.get_setting('password')
    yuppUrl = "https://api.yamsonline.com/astream?username=" + username + "&password=" + password + "&name=VOD&mod=channels&cfg="

    if xbmc.getCondVisibility('!Skin.HasSetting(HomeMenuNoBasicButton)'):
        plugintools.add_item(action='catchupvod_channels', url=yuppUrl + "tamil", title='Tamil', extra='tamil',
                             thumbnail=__get_icon('tamil_movies_tv'))
    plugintools.add_item(action='catchupvod_channels', url=yuppUrl + "telugu", title='Telugu', extra='telugu',
                         thumbnail=__get_icon('telugu_movies_tv'))
    plugintools.add_item(action='catchupvod_channels', url=yuppUrl + "malayalam", title='Malayalam', extra='malayalam',
                         thumbnail=__get_icon('malayalam_movies_tv'))
    plugintools.add_item(action='catchupvod_channels', url=yuppUrl + "hindi", title='Hindi', extra='hindi',
                         thumbnail=__get_icon('hindi_movies_tv'))
    xbmc.log('catchupvod_lang end')

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


def more_cathup(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies2')

    username = plugintools.get_setting('username')
    password = plugintools.get_setting('password')

    vurl = "https://api.yamsonline.com/api?username=" + username + "&password=" + password + "&task=catchtamil&type=channel"

    response = http_request(vurl).read().decode('utf-8')
    nodes = json.loads(response)
    for node in nodes:
        v_url = "https://api.yamsonline.com/api?task=catchtamil&type=shows&channel=" + urllib.parse.quote(
            node['name'].strip())

        plugintools.add_item(
            action='more_cathup_channels',
            title=node['name'],
            url=v_url,
            thumbnail=node['thumb_img'],
            folder=True)

    # Add all shows
    v_url = "https://api.yamsonline.com/api?task=catchtamil&type=shows"
    plugintools.add_item(
        action='more_cathup_shows',
        title='All Shows',
        url=v_url,
        thumbnail=__get_icon('personal'),
        folder=True)

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


def news_fun_cathup(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies2')

    vurl = "https://astreamweb.com/kodi/youtube/api.php?task=youtube&listplaylist=yes"

    response = http_request(vurl).read().decode('utf-8')
    nodes = json.loads(response)
    for node in nodes:
        v_url = "https://astreamweb.com/kodi/youtube/api.php?task=youtube&playlistname=" + urllib.parse.quote(
            node['playlist_name'].strip())

        plugintools.add_item(
            action='news_fun_cathup_videos',
            title=node['playlist_name'],
            url=v_url,
            thumbnail=__get_icon('personal'),
            folder=True)

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


def news_fun_cathup_videos(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')

    vurl = params.get('url')
    self_url = vurl
    response = http_request(vurl).read().decode('utf-8')
    nodes = json.loads(response)

    username = plugintools.get_setting('username')
    password = plugintools.get_setting('password')

    per_page = '14' if 'widget' in params and params['widget'] == 'true' else __get_per_page()

    for node in nodes[:int(per_page)]:
        tmp = node['playback_url'].split('?')
        v_url = tmp[0] + '?name=' + urllib.parse.quote(
            tmp[1].split('=')[1]) + '&username=' + username + '&password=' + password

        plugintools.add_itemcontext(action="play_vod",
                                    title=node['title'],
                                    url=v_url,
                                    thumbnail=node['thumb_url'], folder=False, isPlayable=True)

    if 'widget' in params and params['widget'] == 'true' and len(nodes) > int(per_page):
        plugintools.add_item(action='news_fun_cathup_videos', url=self_url, title='>> %s %s >>' % ('Page', 2))

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


def more_cathup_shows(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    vurl = params.get('url')
    self_url = vurl

    response = http_request(vurl).read().decode('utf-8')

    nodes = json.loads(response)

    per_page = '14' if 'widget' in params and params['widget'] == 'true' else __get_per_page()

    for node in nodes[:int(per_page)]:
        v_url = "https://api.yamsonline.com/api?task=catchtamil&type=episodes&show_name=" + urllib.parse.quote(
            node['show_name']) + "&username=" + username + "&password=" + password
        plugintools.add_item(
            action='more_cathup_by_name',
            title=node['show_name'],
            url=v_url,
            thumbnail=node['thumb_img'],
            folder=True)

    if 'widget' in params and params['widget'] == 'true' and len(nodes) > int(per_page):
        plugintools.add_item(action='more_cathup_shows', url=self_url, title='>> %s %s >>' % ('Page', 2))

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


def more_cathup_channels(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    vurl = params.get('url')

    username = plugintools.get_setting('username')
    password = plugintools.get_setting('password')

    response = http_request(vurl).read().decode('utf-8')

    nodes = json.loads(response)
    for node in nodes:
        v_url = "https://api.yamsonline.com/api?task=catchtamil&type=episodes&show_name=" + urllib.parse.quote(
            node['show_name']) + "&username=" + username + "&password=" + password
        plugintools.add_item(
            action='more_cathup_by_name',
            title=node['show_name'],
            url=v_url,
            thumbnail=node['thumb_img'],
            folder=True)

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


def more_cathup_by_name(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies2')

    vurl = params.get('url')

    response = http_request(vurl).read().decode('utf-8')

    nodes = json.loads(response)
    for node in nodes:
        if node['video_mp4']:
            url = node['video_mp4']
        else:
            url = node['vimeo_video_urls']

        plugintools.add_itemcontext(action="play_vod",
                                    title=node['episode_slug'],
                                    url=url,
                                    thumbnail=node['series_img'], folder=False, isPlayable=True)

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


def catchupvod_channels(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')

    username = plugintools.get_setting('username')
    password = plugintools.get_setting('password')

    lang = params.get('extra') if 'extra' in params else 'tamil'
    vurl = f'''https://api.yamsonline.com/astream?username={username}&password={password}&name=VOD&mod=channels&cfg={lang}'''

    xbmc.log('catchupvod_channels url: %s' % vurl, xbmc.LOGINFO)

    response = http_request(vurl).read().decode('utf-8')
    nodes = json.loads(response)

    per_page = '14' if 'widget' in params and params['widget'] == 'true' else __get_per_page()

    for node in nodes[:int(per_page)]:
        plugintools.add_item(action='catchupvod_dates', title=node['Description'], url=vurl + "&chanid=" + node['ID'],
                             thumbnail=node['Imgpath'], folder=True)

    if 'widget' in params and params['widget'] == 'true' and len(nodes) > int(per_page):
        lang = params.get('title').lower() if 'title' in params else 'tamil'
        plugintools.add_item(action='catchupvod_channels', url='', title='>> %s %s >>' % ('Page', 2), extra=lang)

    xbmc.log('catchupvod_channels end')
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


def catchupvod_dates(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies2')
    vurl = params.get('url')

    t = dt.datetime.now()
    agentType = '2'

    for i in range(0, 30):
        d = t.strftime('%d').lstrip("0")
        m = t.strftime('%m').lstrip("0")
        y = t.strftime('%Y')
        datestr = t.strftime('%m/%d/%Y')
        plugintools.add_item(action='show_catchupvod_ori', title=datestr, url=vurl + "&date=" + m + "/" + d + "/" + y,
                             extra=agentType)
        t = t - dt.timedelta(days=1)

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


def show_catchupvod_ori(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies2')
    vurl = params.get('url')
    agent = params.get('extra')
    xbmc.log('agent {}'.format(agent))
    if not agent: agent = '0'
    response = http_request(vurl).read().decode('utf-8')
    ##print vurl
    nodes = json.loads(response)
    items = [x for x in nodes]
    items.reverse()
    if agent == "2":
        for node in items:
            plugintools.add_item(action="play_vod", title=node['title'], url=secure_catchupvod_url(node['url']),
                                 thumbnail=node['imageUrl'], isPlayable=True, folder=False)
        ##print nodes
    else:
        for node in items:
            plugintools.add_item(action='show_hotstarplayvideo', title=node['title'],
                                 thumbnail=node['imageUrl'], isPlayable=True, folder=False)
        ##print nodes

    xbmc.log('show_catchupvod_ori end')
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


def secure_catchupvod_url(src_url):
    # secret = "psanni56"
    # print(src_url)
    # url = urllib.parse.urlparse(src_url).path
    # if url[0] == "/": url = url[1:]

    # future = dt.datetime.utcnow() + dt.timedelta(minutes=60)
    # expiry = calendar.timegm(future.timetuple())

    # secure_link = "{key}{url}{expiry}".format(key=secret,url=url,expiry=expiry)
    # hash = hashlib.md5(secure_link.encode('utf-8')).digest()
    # encoded_hash = base64.urlsafe_b64encode(hash).rstrip('=')
    # url = src_url
    # print(src_url)
    return src_url


# catchup_providers/eng1
def show_eng1(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')

    asiptvs.asiptvs_vod()


# catchup_providers/eng2
def show_eng2l(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    for l in ascii_lowercase:
        plugintools.add_item(title=l.upper(), action='show_eng2', url=l)

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


# catchup_providers/eng2
def show_eng2(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    lettre = params.get('url')

    asiptvs.asiptvs_vod_videos2("70", lettre)


#########################################
# Premium TV Shows'
def getseries(params):
    params.update({'category_id': '82'})
    getseries_bycategory(params)


# Premium Indian TV series
def getseries3(params):
    params.update({'category_id': '78'})
    getseries_bycategory(params)


# Premium TV series
def getseries2(params):
    params.update({'category_id': ''})
    getseries_bycategory(params)


# series
def show_series(params):  # (path, sorting, page):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    path = params.get('url')
    sorting = 'title,ASC'  # params.get('title')+','+params.get('extra')
    page = params.get('page')
    username = plugintools.get_setting('username')
    per_page = __get_per_page()
    items, has_next_page = scraper.get_series(username, path, page, per_page, sorting)
    xbmc.log('items {}'.format(items))
    xbmc.log('has_next_page {}'.format(has_next_page))

    # Add context menu items for title and actor search
    ListSearch = 'XBMC.Container.Update(%s)' % (
            sys.argv[0] + '?action=search&title=%s&url=%s&thumbnail=%s&plot=%s&extra=%s&page=%s')
    ListMovie = 'XBMC.Container.Update(%s)' % (
            sys.argv[0] + '?action=show_series&title=%s&url=%s&thumbnail=%s&plot=%s&extra=%s&page=%s')
    # figure out if this is a page refresh
    is_update = (not page == '1')
    # add pagination-items
    if has_next_page:
        next_page = str(int(page) + 1)
        xbmc.log('has_next_page {} , next_page {}.'.format(has_next_page, next_page))
        plugintools.add_item(title='>> %s %s >>' % ('Page', next_page),
                             action='show_series', url=path, extra=sorting, page=next_page)

    for item in items:
        xbmc.log('getseries info {}'.format(item["info"]["cast"]))
        xbmc.log('getseries info {}'.format(item["id"]))
        try:
            context_men = [('Movie information', 'XBMC.Action(Info)'),
                           ('Search for Movies by title', ListSearch % ('', '', '', '', '', ''))]

            for cast in item['info']['cast']:
                s_path = 'cast-%s' % cast
                context_men.append(('Movies with %s' % cast, ListMovie % ('', s_path, '', '', 'title%2CASC', '1')))

        except:
            traceback.print_exc()
        plugintools.add_itemcontext(action='show_series_files', title=item['label'], url=item['id'],
                                    info_labels=item['info'],
                                    thumbnail=item['thumbnail'], fanart=item['fanart'], page='0',
                                    contextmenu=context_men, folder=True)

    if int(page) > 1:
        prev_page = str(int(page) - 1)
        plugintools.add_item(title='<< %s %s <<' % ('Page', prev_page),
                             action='show_series', url=path, extra=sorting, page=prev_page)
    xbmc.log('show_series end')
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True, updateListing=is_update)


# series_files v1
def show_series_files(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    idx = params.get("url")
    page = params.get("page")
    servers = {"Auto Select Best Server": "api.yamsonline.com"}
    server = "api.yamsonline.com"

    xbmc.log('show_series_files started for movie_id={}, page={}'.format(id, page))
    username = plugintools.get_setting('username')
    password = plugintools.get_setting('password')
    try:
        videos = scraper.get_series_files(idx, username, password)
        data = scraper.get_seasons(idx, username, password, page)
        xbmc.log('seasons data {} '.format(data))
    except Exception as e:
        xbmc.log('seasons error {} '.format(e))
        scraper.notifyError("AStreamWeb", msg="Movie not available yet, please contact support.")
        return
    xbmc.log('show_series_files got {}'.format(videos))
    added_seasons = list()
    oneUrl = len(videos) == 100
    xbmc.log('oneUrl {}'.format(oneUrl))

    for video in videos:
        # is tv serials
        if 'season' in video:
            # show the season listing
            xbmc.log('show_series_files season in video{}'.format(video))
            try:
                thumbnail = video['thumbnail']
            except:
                thumbnail = ''
            if page == '0':
                xbmc.log('show_series_files page=0')
                if video['season'] not in added_seasons:
                    for item in data:
                        xbmc.log('seasons item {} video {}'.format(item['label'], video['season']))
                        if int(item['label']) == int(video['season']):
                            thumbnail = item['thumbnail']
                            break
                        else:
                            thumbnail = ''

                    xbmc.log('show_series_files season {}'.format(video))
                    added_seasons.append(video['season'])
                    plugintools.add_item(action='show_series_files', url=idx, title='Season %s' % video['season'],
                                         page=video['season'], thumbnail=thumbnail)


            # show the episode listing for given season (=page)
            else:
                if video['season'] == page and not oneUrl:
                    xbmcplugin.setContent(int(sys.argv[1]), 'movies2')
                    # xbmc.log('page {} show_series_files episode and not oneUrl{}'.format(page,video['episode']))
                    for item in data:
                        for c in item['info']:
                            xbmc.log(
                                'episode_number {} episode test  {}'.format(c['episode_number'], video['episode']))
                            if int(c['episode_number']) == int(video['episode']):
                                thumbnail = c['poster']
                                plot = c['plot']
                                break
                            else:
                                thumbnail = ''
                                plot = ''
                            if thumbnail: break

                    url = video['url'].replace("server.akshayan.me", server)
                    xbmc.log('episode plot %s' % plot)
                    xbmc.log('thumbnail %s' % thumbnail)
                    if not thumbnail:
                        thumbnail = ''
                    plugintools.add_itemcontext(action="play_vod",
                                                title='Episode %s - %s' % (video['episode'], video['label']),
                                                plot=plot, url=url,
                                                thumbnail=thumbnail, folder=False, isPlayable=True)
                elif video['season'] == page:
                    # xbmc.log('show_series_files episode and  oneUrl{}'.format(video))
                    xbmc.log('page {} show_series_files episode and  oneUrl{}'.format(page, video['season']))

                    for item in data:
                        # xbmc.log('seasons item {} video {}'.format(item['label'] , video['season']))
                        for c in item['info']:
                            if int(c['episode_number']) == int(video['episode']):
                                thumbnail = c['poster']
                                plot = c['plot'].encode('utf-8')
                                break
                            else:
                                thumbnail = ''
                                plot = ''
                            if thumbnail:
                                break

                    url = video['url'].replace("server.akshayan.me", server)
                    if not thumbnail:
                        thumbnail = ''
                    plugintools.add_itemcontext(action="play_vod",
                                                title='Episode %s - %s' % (video['episode'], video['label']),
                                                url=url,
                                                thumbnail=thumbnail, plot=plot, folder=False, isPlayable=True)

        # is movie
        else:
            if oneUrl:
                xbmc.log('passe par oneUrl')
                xbmc.log('url video[url] {}'.format(video['url']))
                plugintools.add_item(action="play_vod", title=video['label'],
                                     url=video['url'].replace("server.akshayan.me", server),
                                     thumbnail='', plot='', extra='', page='',
                                     folder=False, isPlayable=True)
            else:
                xbmc.log('passe par oneUrl=false')
                xbmc.log('url video[url] {}'.format(video['url']))
                url = video['url'].replace("server.akshayan.me", server)
                plugintools.add_itemcontext(action="play_vod", title=video['label'],
                                            url=url,
                                            folder=False, isPlayable=True)

    if not videos:  # items:
        dialog = xbmcgui.Dialog()
        dialog.ok('No Videos',
                  'movie will be available shortly',
                  'Alternative contact support',
                  'Movie-ID: %s' % idx)
    else:
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_EPISODE)
        xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


############################################
# search
def search(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies2')
    plugintools.add_item(title="Search by Movie", action='searchByName')
    plugintools.add_item(title="Search by Series", action='searchBySeries')
    plugintools.add_item(title="Search by Actor", action='searchByActor')
    plugintools.add_item(title="Search by Actress", action='searchByActress')
    plugintools.add_item(title="Multi-Search", action='multiSearch')
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


# multiSearch
def multiSearch(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    langs = scraper.get_langs()
    plugintools.add_item(title="All", action='multiSearchLangs', url="-", thumbnail=__get_icon("ALL"))
    for node in langs:
        plugintools.add_item(title=node['name'], action='multiSearchLangs', url='language-%s' % node['id'],
                             thumbnail=__get_icon(node['name']))

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


# multiSearchLangs
def multiSearchLangs(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies2')
    path = params.get('url')
    plugintools.add_item(title='All', action='multiSearchYears', url=path)
    if path == "-":
        path = ""
    else:
        path += "+"
    years = list(range(1950, dt.datetime.now().year + 1))
    years.reverse()
    for year in years:
        plugintools.add_item(title=str(year), action='multiSearchYears', url=path + "year-" + str(year))
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)
    xbmc.executebuiltin('Container.SetViewMode(50)')


# multiSearchYears
def multiSearchYears(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies2')
    path = params.get('url')
    plugintools.add_item(title='All', action='multiSearchGenres', url=path)
    if path == "-":
        path = ""
    else:
        path += "+"
    nodes = scraper.get_genres()
    nodes.remove({'name': 'Bluray', 'id': '72'})
    for node in nodes:
        plugintools.add_item(title=node["name"], action='multiSearchGenres', url=path + "category-" + node["id"])

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


# multiSearchGenres
def multiSearchGenres(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    path = params.get('url')
    plugintools.add_item(title="All", action='multiSearchType', url=path)
    if path == "-":
        path = ""
    else:
        path += "+"
    plugintools.add_item(title="Bluray only", action='multiSearchType', url=path + "category-72")
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


# multiSearchType
def multiSearchType(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    path = params.get('url')
    plugintools.add_item(title="All", action='show_movies', url=path, extra="title,ASC", page="1")
    if path == "-":
        path = ""
    else:
        path += "+"
    plugintools.add_item(title="Search by actor", action='multiSearchActor', url=path)
    plugintools.add_item(title="Search by actress", action='multiSearchActress', url=path)
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)
    xbmc.executebuiltin('Container.SetViewMode(50)')


# multiSearchActor
def multiSearchActor(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    path = params.get('url')
    actors = scraper.ACTORS
    if path == "-":
        path = ""
    else:
        path += "+"
    for actor in actors:
        s_path = path + "cast-%s" % actor
        plugintools.add_item(title=actor, action='show_movies', url=s_path, extra='title,ASC', page='1',
                             thumbnail="https://astreamweb.com/kodi/actorimage/{0}.webp".format(
                                 actor.replace(' ', '%20')))
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)

    xbmc.executebuiltin('Container.SetViewMode(54)')


# multiSearchActress
def multiSearchActress(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    path = params.get('url')
    actresses = scraper.ACTRESSES
    if path == "-":
        path = ""
    else:
        path += "+"
    for actress in actresses:
        s_path = path + "cast-%s" % actress
        plugintools.add_item(title=actress, action='show_movies', url=s_path, extra='title,ASC', page='1',
                             thumbnail="https://astreamweb.com/kodi/actorimage/{0}.webp".format(
                                 actress.replace(' ', '%20')))
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


# searchByActor
def searchByActor(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    actors = scraper.ACTORS
    for actor in actors:
        cast_path = "cast-%s" % actor
        xbmc.log("https://astreamweb.com/kodi/actorimage/{0}.webp".format(actor))
        plugintools.add_item(title=actor, action='show_movies', url=cast_path, extra='title,ASC', page='1',
                             thumbnail="https://astreamweb.com/kodi/actorimage/{0}.webp".format(
                                 actor.replace(' ', '%20')))
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


# searchByActress/
def searchByActress(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    actresses = scraper.ACTRESSES
    for actress in actresses:
        cast_path = "cast-%s" % actress
        plugintools.add_item(title=actress, action='show_movies', url=cast_path, extra='title,ASC', page='1',
                             thumbnail="https://astreamweb.com/kodi/actorimage/{0}.webp".format(
                                 actress.replace(' ', '%20')))
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


def searchByName(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    username = plugintools.get_setting('username')
    per_page = __get_per_page()
    page = '1'
    keyboard = xbmc.Keyboard('', 'Enter Search String')
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        search_string = keyboard.getText()
        xbmc.log('search gots a string: "%s"' % search_string)
        if '*' not in search_string:
            search_string = '*%s*' % search_string
            xbmc.log('altered search string to: "%s"' % search_string)
        path = 'title-%s' % search_string
        items, has_next_page = scraper.get_movies(username, path, page, per_page,
                                                  'title,ASC')
        xbmc.log('items {}'.format(items))
        xbmc.log('has_next_page {}'.format(has_next_page))

        # Add context menu items for title and actor search
        context_men = []
        ListMovie = 'XBMC.Container.Update(%s)' % (
                sys.argv[0] + '?action=show_movies&title=%s&url=%s&thumbnail=%s&plot=%s&extra=%s&page=%s')
        for item in items:
            try:
                for cast in item['info']['cast']:
                    s_path = 'cast-%s' % cast
                    context_men.append(('Movies with %s' % cast, ListMovie % ('', s_path, '', '', '-', '1')))

            except:
                xbmc.log('has_next_page {}'.format(has_next_page))
                ""
            plugintools.add_itemcontext(action='show_movie_files', title=item['label'], url=item['id'],
                                        info_labels=item['info'],
                                        thumbnail=item['thumbnail'], fanart=item['fanart'], page='0',
                                        contextmenu=context_men, folder=True)

        xbmc.log('search end')
        xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


def searchBySeries(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    per_page = __get_per_page()
    page = '1'
    keyboard = xbmc.Keyboard('', 'Enter Search String')
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        search_string = keyboard.getText()
        xbmc.log('search gots a string: "%s"' % search_string)
        if '*' not in search_string:
            search_string = '*%s*' % search_string
            xbmc.log('altered search string to: "%s"' % search_string)
        path = 'title-%s' % search_string
        items, has_next_page = scraper.get_series(username, path, page, per_page,
                                                  'title,ASC')
        xbmc.log('items {}'.format(items))
        xbmc.log('has_next_page {}'.format(has_next_page))

        # Add context menu items for title and actor search
        context_men = []
        ListMovie = 'XBMC.Container.Update(%s)' % (
                sys.argv[0] + '?action=show_movies&title=%s&url=%s&thumbnail=%s&plot=%s&extra=%s&page=%s')
        for item in items:
            try:
                for cast in item['info']['cast']:
                    s_path = 'cast-%s' % cast
                    context_men.append(('Movies with %s' % cast, ListMovie % ('', s_path, '', '', '-', '1')))

            except:
                xbmc.log('has_next_page {}'.format(has_next_page))
                ""
            plugintools.add_itemcontext(action='show_series_files', title=item['label'], url=item['id'],
                                        info_labels=item['info'],
                                        thumbnail=item['thumbnail'], fanart=item['fanart'], page='0',
                                        contextmenu=context_men, folder=True)

        xbmc.log('search end')
        xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


def show_letters(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies2')
    path = params.get('url')

    for l in ascii_lowercase:
        path = '%s+title-%s*' % (path, l)
        plugintools.add_item(action='show_movies', title=l.upper(), url=path, extra='title,ASC', page='1')

    xbmc.log('show_letters end')
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


###########################################
def show_maintenance(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies2')
    # plugintools.add_item(action="show_speedtest", title='Speedtest',
    #                      thumbnail=__get_icon('speed'))
    # plugintools.add_item(action="show_ping", title='Ping',
    #                     thumbnail=__get_icon('ping'))
    plugintools.add_item(action="select_device_maintenance", title='Update Device Type',
                         thumbnail=__get_icon('resetastreamweb'))
    plugintools.add_item(action="send_log", title='Send log',
                         thumbnail=__get_icon('sendlog'))
    plugintools.add_item(action="debug_off", title='Disable Debugging Mode',
                         thumbnail=__get_icon('clearcache'))
    plugintools.add_item(action="debug_on", title='Enable Debugging Mode',
                         thumbnail=__get_icon('clearcache'))
    plugintools.add_item(action="show_zerosetting", title='Apply AstreamWeb Settings',
                         thumbnail=__get_icon('enablezerocache'), isPlayable=False, folder=False)
    plugintools.add_item(action="show_advancedsetting", title='Verify Advanced Settings',
                         thumbnail=__get_icon('verifyzerocache'))
    plugintools.add_item(action="show_calibration", title='Screen Calibration',
                         thumbnail=__get_icon('resetastreamweb'))
    plugintools.add_item(action="select_skin_language2", title='Select Skin Language',
                         thumbnail=__get_icon('resetastreamweb'), folder=False)

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


# settings
def show_settings(params):
    xbmc.log('show_settings started')
    plugintools.open_settings_dialog()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def show_removedevice():
    xbmc.executebuiltin('XBMC.RunScript(special://home/addons/plugin.video.yams/killSessions.py)', True)
    xbmc.executebuiltin('Container.Refresh(plugin://plugin.video.yams)')


def debug_off(params):
    choice = xbmcgui.Dialog().yesno('AstreamWeb',
                                    'Please confirm that you wish to disable log debugging mode immediately')
    if choice == 1:
        xbmc.executebuiltin("ToggleDebug")
        xbmc.executebuiltin("Container.Refresh")
    else:
        quit()


def debug_on(params):
    choice = xbmcgui.Dialog().yesno('AstreamWeb',
                                    'Please confirm that you wish to enable log debugging mode immediately')
    if choice == 1:
        xbmc.executebuiltin("ToggleDebug")
        xbmc.executebuiltin("Container.Refresh")
    else:
        quit()


def show_speedtest(params):
    xbmc.executebuiltin('Runscript("special://home/addons/plugin.video.yams/fastload.py")')


def show_ping(params):
    xbmc.log("------------=> Ping...")
    progress = xbmcgui.DialogProgress()  # utils.progress
    progress.create('Ping', 'Calculating ping...')
    progress.update(25, "Calculating ping to France Server...")
    dcms = -1
    sjms = __ping("s4.yamsftp.net")
    if sjms == -1:
        if dialog.ok('Error', "Impossible to ping to San Jose Server."):
            progress.update(50, "Calculating ping to Washington DC Server...")
            dcms = __ping("server.akshayan.me")
    else:
        progress.update(50, "Calculating ping to Washington DC Server...")
        dcms = __ping("server.akshayan.me")
    if dcms == -1:
        dialog.ok('Error', "Impossible to ping to Washington DC Server.")
    if dcms == -1 and sjms == -1:
        progress.update(100, "Ping failed")
        return
    progress.update(100, "Ping finished")
    dialog.ok('Result',
              "San Jose Server (" + (str(sjms) + " ms" if sjms != -1 else "Failed") + "), Washington DC Server (" + (
                  str(dcms) + " ms" if dcms != -1 else "Failed") + ")", '')


def __ping(host):
    xbmc.log("------------=> Ping to " + host)

    try:
        if xbmc.getCondVisibility('system.platform.windows'):
            p = subprocess.Popen(["ping", "-n", "4", host], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        else:
            p = subprocess.Popen(["ping", "-c", "4", host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ping_results = re.compile("=(.*?)ms").findall(p.communicate()[0])
    except Exception as e:
        x = sys.exc_info()[0]
        xbmc.log("Platform doesn't support ping. %s " % e)
        return -1

    if ping_results:
        avg_ping = __averageList(ping_results)
        return avg_ping
    else:
        xbmc.log("Couldn't get ping")
        return -1


def __averageList(lst):
    avg_ping = 0
    avg_ping_cnt = 0
    for p in lst:
        try:
            avg_ping += int(p)  # float(p)
            avg_ping_cnt += 1
        except:
            xbmc.log("Couldn't convert %s to float" % repr(p))
    if avg_ping_cnt == 0:
        return -1
    else:
        return int(avg_ping / avg_ping_cnt)


def send_log(params):
    choice = xbmcgui.Dialog().yesno('AstreamWeb',
                                    'Have you ensured to enable [COLOR red]debuging mode[/COLOR], and execute the problem and only hereafter click on send log.')
    if choice == 1:
        xbmc.executebuiltin("RunAddon(script.kodi.loguploader)")
    else:
        dialog.ok('AstreamWeb',
                  "Please click on [COLOR red]Enable Debuging Mode[/COLOR] Icon under Maintenance Icon, and then run the problem again and hereafter click on Send Log.",
                  '')


def __sendlog():
    LOGPATH = xbmcvfs.translatePath('special://logpath')
    logfilePath = os.path.join(LOGPATH, 'kodi.log')

    fp = open(logfilePath, 'r')
    msg = fp.read()
    fp.close()
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    try:
        params = {'data': base64.b64encode(msg).encode(), 'username': plugintools.get_setting('username')}
    except:
        params = {'data': base64.b64encode(msg), 'username': plugintools.get_setting('username')}
    url = 'https://astreamweb.com/kodi/web/kodilog.php'
    return postHtml(url, params, headers)
    # print utils.postHtml(url, params, headers)


def show_zerosetting(params):
    dialog = xbmcgui.Dialog()
    dialog.ok('AstreamWeb Maintenance', 'Installing configuration files, Please restart device.')
    scraper.ZeroCachingSetting()


def show_advancedsetting(params):
    scraper.VerifyAdvancedSetting()


def show_calibration(params):
    scraper.Calibration()


def handle_wait(time_to_wait, title, text):
    mensagemprogresso = xbmcgui.DialogProgress()
    secs = 0
    increment = int(100 / time_to_wait)
    cancelled = False
    while secs < time_to_wait:
        secs += 1
        percent = increment * secs
        secs_left = str((time_to_wait - secs))
        remaining_display = "Still " + str(secs_left) + "seconds left"
        mensagemprogresso.update(percent, text, remaining_display)
        xbmc.Monitor().waitForAbort(1)
        if mensagemprogresso.iscanceled():
            cancelled = True
            break
    if cancelled == True:
        return False
    else:
        mensagemprogresso.close()
        return False


def _select_skin_language(langs=None):
    xbmc.log(f'language changes to {langs}', xbmc.LOGINFO)
    url = "https://yamshost.org/amember/api/check-access/by-login?_key=HODzCPbEpwmz4ufir2jimobile&login=%s" % username
    response = http_request(url).read().decode('utf-8')
    jsonResp = json.loads(response)
    categories = [int(a) for a in list(jsonResp["categories"].keys())]
    category = ""
    # print(categories)
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

    xbmc.executebuiltin('Skin.SetString(subs, %s)' % category)

    catPath = xbmcvfs.translatePath(os.path.join('special://home/userdata', ''))
    catFile = open(os.path.join(catPath, "astream.category"), 'w')
    catFile.write(category)
    catFile.close()

    if not langs:
        langs = plugintools.get_setting('channellanguage')
    # selecting skin Languages
    try:
        # lang lib zip file download and extract
        lib_file = f"https://astreamweb.com/kodi/skin/{langs.capitalize()}.zip"
        lib_path = xbmcvfs.translatePath(os.path.join(f'special://home/userdata/{langs.capitalize()}.zip'))
        extract_path = xbmcvfs.translatePath(os.path.join('special://home/userdata/'))
        if not scraper._downloadOverride(lib_file, lib_path):
            lib_path = xbmcvfs.translatePath(os.path.join(f'special://home/userdata/Default.zip'))
            scraper._downloadOverride(lib_file, lib_path)

        with zipfile.ZipFile(lib_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
    except:
        traceback.print_exc()
        # xbmcgui.Dialog().ok('Astreamweb', 'Error occured during setup')


def select_skin_language2(params=None):
    langs = ['Tamil', 'Telugu', 'Malayalam', 'Hindi']
    select = xbmcgui.Dialog().select("Select your Language", langs)
    plugintools.set_setting('channellanguage', langs[select].lower())
    _select_skin_language(langs[select].lower())
    xbmc.Monitor().waitForAbort(1)
    xbmc.executebuiltin("ReloadSkin")


def select_device(params=None):
    device = ['FireTV 4K Stick', 'Fire TV Cube,Max or better']
    select = xbmcgui.Dialog().select("Select your Device Type", device)
    plugintools.set_setting('devicetype', device[select].lower())
    xbmc.Monitor().waitForAbort(1)


def select_device_maintenance(params=None):
    select_device()
    devicetype = plugintools.get_setting('devicetype')
    if ('cube' in devicetype):
        xbmc.executebuiltin('Skin.SetBool(highenddevice)')
        xbmc.executebuiltin('Skin.Reset(%s)' % 'lowenddevice')
    else:
        xbmc.executebuiltin('Skin.SetBool(lowenddevice)')
        xbmc.executebuiltin('Skin.Reset(%s)' % 'highenddevice')
    if xbmc.getCondVisibility('Skin.HasSetting(lowenddevice)'):
        lib_file = "https://astreamweb.com/kodi/skin/lowenddevice.zip"
    else:
        lib_file = "https://astreamweb.com/kodi/skin/highenddevice.zip"
    if xbmc.getCondVisibility("System.Platform.Android") == 1 or xbmc.getCondVisibility("system.platform.tvos") == 1:
        lib_path = xbmcvfs.translatePath(os.path.join('special://xbmc/devicetype.zip'))
        extract_path = xbmcvfs.translatePath(os.path.join('special://xbmc/'))
        if not scraper._downloadOverride(lib_file, lib_path):
            lib_path = xbmcvfs.translatePath(os.path.join('special://xbmc/devicetype.zip'))
            scraper._downloadOverride(lib_file, lib_path)
    elif xbmc.getCondVisibility("System.Platform.Windows") == 1 or xbmc.getCondVisibility("system.platform.osx") == 1:
        lib_path = xbmcvfs.translatePath(os.path.join('special://home/devicetype.zip'))
        extract_path = xbmcvfs.translatePath(os.path.join('special://home/'))
        if not scraper._downloadOverride(lib_file, lib_path):
            lib_path = xbmcvfs.translatePath(os.path.join('special://home/devicetype.zip'))
            scraper._downloadOverride(lib_file, lib_path)

    with zipfile.ZipFile(lib_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    xbmc.Monitor().waitForAbort(1)
    xbmc.executebuiltin('ReloadSkin()')
    xbmc.executebuiltin("XBMC.ActivateWindow(Home)")


def get_timezoneselect():
    timezone = ['None', 'America/Los Angeles', 'America/Chicago', 'America/New York', 'Europe/London',
                'Europe/Amsterdam']
    select = xbmcgui.Dialog().select("Select your local timezone", timezone)
    plugintools.set_setting('globaltimezone', timezone[select])


def __get_per_page():
    per_page = int(plugintools.get_setting('per_page'))
    if per_page not in (list(range(1, 200))):
        per_page = 200
        plugintools.set_setting('per_page', str(per_page))
    return per_page


def __get_per_page_widget():
    per_page = '14'
    return per_page


# show_einthusan_categories
#############
# EINTHUSAN #
#############


def get_einthusan():
    goeinthusan = {"San Francisco": -28800,
                   "Dallas": -21600,
                   "Washington D.C": -18000,
                   "Toronto": 0,
                   "London": 3600,
                   "Sydney": 14400,
                   "No Preference": 18000,
                   "None": 28800}
    choseneinthusan = "No Preference"
    keys = list(goeinthusan.keys())

    if (choseneinthusan == "None" or choseneinthusan == '') or choseneinthusan not in keys:
        return None
    else:
        return goeinthusan[choseneinthusan]


# show_einthusan_categories
def show_einthusan_categories(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies2')
    languages = ["Hindi", "Tamil", "Telugu", "Malayalam", "Kannada", "Bengali", "Marathi", "Punjabi"]
    for lang in languages:
        plugintools.add_item(action="show_einthusan_inner_cats", title=lang,
                             thumbnail=__get_icon("{0}_Movies".format(lang.lower())),
                             url=lang.lower())  # lang=

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


# show_einthusan_inner_cats/<lang>/')
def show_einthusan_inner_cats(params):  # lang, bluray=False):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies2')
    lang = params.get("url")
    postUrl = 'lang=' + lang
    plugintools.add_item(action="show_einthusan_a_z", title='A-Z', thumbnail=__get_icon("einthusan_a_z"), url=lang,
                         extra=postUrl)
    plugintools.add_item(action="show_einthusan_years", title='Years', thumbnail=__get_icon("einthusan_years"),
                         url=lang, extra=postUrl)

    plugintools.add_item(action="show_einthusan_movies", title='Recent', thumbnail=__get_icon("einthusan_recent"),
                         url=lang,
                         extra='https://einthusan.ca/movie/results/?' + postUrl + '&find=Recent', page='1')

    plugintools.add_item(action="show_einthusan_featured", title='Featured', thumbnail=__get_icon("einthusan_featured"),
                         url=lang, extra=postUrl)
    plugintools.add_item(action="show_einthusan_search", title='Search', thumbnail='', url=lang, extra=postUrl)
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)
    xbmc.executebuiltin('Container.SetViewMode(501)')


# show_einthusan_a_z/<lang>/<post>")
def show_einthusan_a_z(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies2')
    post = params.get("extra")

    azlist = list(map(chr, list(range(65, 91))))
    plugintools.add_item(action="show_einthusan_movies", title='Numerical',
                         extra='https://einthusan.ca/movie/results/?find=Numbers&' + post, page='1')

    for letter in azlist:
        plugintools.add_item(
            action="show_einthusan_movies", title=letter,
            extra='https://einthusan.ca/movie/results/?alpha={0}&find=Alphabets&{1}'.format(letter, post),
            page='1')

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


# show_einthusan_years
def show_einthusan_years(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies2')
    post = params.get("extra")
    from datetime import date

    postData = post + '&find=Year&year='
    values = [repr(x) for x in reversed(list(range(1940, date.today().year + 1)))]
    for year in values:
        plugintools.add_item(action="show_einthusan_movies", title=year,
                             extra='https://einthusan.ca/movie/results/?' + postData + str(year), page='1')

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


# show_einthusan_featured
def show_einthusan_featured(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies2')
    lang = params.get("url")
    page_url = 'https://einthusan.ca/movie/browse/?lang=' + lang

    html = requests.get(page_url, headers=HTTP_HEADERS).text
    matches = re.compile(
        'name="newrelease_tab".+?img src="(.+?)".+?href="(.+?)"><h2>(.+?)</h2>.+?i class=(.+?)</div>').findall(html)

    for img, id, name, ishd in matches:
        movieid = id.split('/')[3]
        movielang = id.split('lang=')[1]
        movie = name + ',' + movieid + ',' + movielang
        if 'ultrahd' in ishd:
            title = name + '[COLOR blue]- Ultra HD[/COLOR]'
            movie = movie + ',itshd,' + page_url
        else:
            title = name
            movie = movie + ',itsnothd,' + page_url
        image = 'http:' + img
        plugintools.add_item(action="play_einthusan", title=title, url=movie, thumbnail=image, isPlayable=True,
                             folder=False)

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


# show_einthusan_search
def show_einthusan_search(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    post = params.get("extra")

    url = post
    keyb = xbmc.Keyboard('', 'Search for Movies')
    keyb.doModal()
    if keyb.isConfirmed():
        search_term = urllib.parse.quote_plus(keyb.getText())
        search_url = 'https://einthusan.ca/movie/results/?' + url + '&query=' + search_term
        # headers = {
        #     'Origin': 'https://einthusan.ca',
        #     'Referer': 'https://einthusan.ca/movie/browse/?' + url,
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}

        html = requests.get(search_url, headers=HTTP_HEADERS).text
        match = re.compile(
            '<div class="block1">.*?href=".*?watch\/(.*?)\/\?lang=(.*?)".*?src="(.*?)".*?<h3>(.*?)</h3>.+?i class(.+?)<p').findall(
            html)

        for movie, lang, image, name, ishd in match:
            image = 'http:' + image
            movie = str(name) + ',' + str(movie) + ',' + lang + ','
            if 'ultrahd' in ishd:
                name = name + '[COLOR blue]- Ultra HD[/COLOR]'
                movie = movie + 'itshd,' + search_url
            else:
                movie = movie + 'itsnothd,' + search_url
            # addDir(name, MOVIES_URL + str(movie)+'/?lang='+lang, 2, image, lang)
            plugintools.add_item(action="play_einthusan", title=name, url=movie, thumbnail=image, isPlayable=True,
                                 folder=False)
        try:
            nextpage = re.findall('data-disabled="([^"]*)" href="(.+?)"', html)[-1]
            if nextpage[0] != 'true':
                plugintools.add_item(action="show_einthusan_movies", title=name, thumbnail=image,
                                     extra='https://einthusan.ca/' + nextpage[1], page="2")
        except:
            pass

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


# einthusan fetching
def get_einthusan_location():
    locationStr = "No Preference"  # xbmcplugin.getSetting(int(sys.argv[1]), 'einthusan_location')
    return locationStr


# show_einthusan_movies
def show_einthusan_movies(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    page = params.get("page")
    post = params.get("extra")
    page = int(page)
    referurl = post
    url = post

    html = requests.get(url, verify=False).text
    match = re.compile(
        '<div class="block1">.*?href=".*?watch\/(.*?)\/\?lang=(.*?)".*?src="(.*?)".*?<h3>(.*?)</h3>.+?i class(.+?)<p.+?<span>Wiki</span>(.+?)</div>').findall(
        html)
    nextpage = re.findall('data-disabled="([^"]*)" href="(.+?)"', html)[-1]

    for movie, lang, image, name, ishd, trailer in match:
        image = 'http:' + image
        movie = str(name) + ',' + str(movie) + ',' + lang + ','
        if 'ultrahd' in ishd:
            name = name + '[COLOR blue]- Ultra HD[/COLOR]'
            movie = movie + 'itshd,' + referurl
        else:
            movie = movie + 'itsnothd,' + referurl

        plugintools.add_item(action="play_einthusan", title=name, url=movie, thumbnail=image, isPlayable=True,
                             folder=False)

    curPage = 1
    if nextpage[0] != 'true':
        nextPage_Url = 'https://einthusan.ca' + nextpage[1]
        while curPage < 4:
            print("curPage: " + str(curPage))
            curPage += 1
            html = requests.get(nextPage_Url, verify=False).text
            match = re.compile(
                '<div class="block1">.*?href=".*?watch\/(.*?)\/\?lang=(.*?)".*?src="(.*?)".*?<h3>(.*?)</h3>.+?i class(.+?)<p.+?<span>Wiki</span>(.+?)</div>').findall(
                html)
            nextpage = re.findall('data-disabled="([^"]*)" href="(.+?)"', html)[-1]
            nextPage_Url = 'https://einthusan.ca' + nextpage[1]
            for movie, lang, image, name, ishd, trailer in match:
                image = 'http:' + image
                movie = str(name) + ',' + str(movie) + ',' + lang + ','
                if 'ultrahd' in ishd:
                    name = name + '[COLOR blue]- Ultra HD[/COLOR]'
                    movie = movie + 'itshd,' + referurl
                else:
                    movie = movie + 'itsnothd,' + referurl
                # addDir(name, MOVIES_URL + str(movie)+'/?lang='+lang, 2, image, lang)
                plugintools.add_item(action="play_einthusan", title=name, url=movie, thumbnail=image, isPlayable=True,
                                     folder=False)

            if nextpage[0] == 'true':
                break
        nextPage_Url = 'https://einthusan.ca' + nextpage[1]
        if curPage > 3 and nextpage[0] != 'true':
            plugintools.add_item(action="show_einthusan_movies", title='>>> Next Page >>>',
                                 extra=nextPage_Url, page=str(page + curPage))

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


# einthusan playing
def decodeEInth(lnk):
    t = 10
    r = lnk[0:t] + lnk[-1] + lnk[t + 2:-1]
    return r.encode()


def encodeEInth(lnk):
    t = 10
    r = lnk[0:t] + lnk[-1] + lnk[t + 2:-1]
    return r.encode()


'''
def get_einthusanselect():
        goeinthusan = ['None','San Francisco', 'Dallas', 'Washington D.C', 'Toronto', 'London', 'Sydney', 'No Preference']
        select = xbmcgui.Dialog().select("Select your local timezone", goeinthusan)
        plugintools.set_setting('einthusan_location', goeinthusan[select])
'''


def einthusan_preferred_server(lnk, mainurl):
    '''
    goeinthusan = get_einthusan()
    if goeinthusan == None:
            dialog = xbmcgui.Dialog()
            dialog.ok('Server Selection', "Please select the city closest to you.")
            get_einthusanselect()
    '''
    location = get_einthusan_location()
    xbmc.log(location, level=xbmc.LOGINFO)
    if location != 'No Preference':
        if location == 'Dallas':
            servers = [23, 24, 25, 29, 30, 31, 35, 36, 37, 38, 45]
        elif location == 'Washington D.C':
            servers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 41, 44]
        elif location == 'San Francisco':
            servers = [19, 20, 21, 22, 46]
        elif location == 'Toronto':
            servers = [26, 27]
        elif location == 'London':
            servers = [14, 15, 16, 17, 18, 32, 33, 39, 40, 42]
        else:  # location == 'Sydney'
            servers = [28, 34, 43]

        server_n = lnk.split('.einthusan.ca')[0].strip('https://s')
        SERVER_OFFSET = []
        xbmc.log('lnk {}'.format(lnk))
        xbmc.log('server einthusan {}'.format(server_n))
        if int(server_n) > 100:
            SERVER_OFFSET.append(100)
        else:
            SERVER_OFFSET.append(0)
        servers.append(int(server_n) - SERVER_OFFSET[0])
        vidpath = lnk.split('.tv/')[1]
        new_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
            'Referer': mainurl, 'Origin': 'https://einthusan.ca'}
        for i in servers:
            urltry = ("https://s" + str(i + SERVER_OFFSET[0]) + ".einthusan.ca/" + vidpath)
            isitworking = requests.get(urltry, headers=new_headers).status_code
            xbmc.log(urltry, level=xbmc.LOGINFO)
            xbmc.log(str(isitworking), level=xbmc.LOGINFO)
            if isitworking == 200:
                lnk = urltry
                break
    return lnk


# play_einthusan
def play_einthusan(params):
    url = params.get('url')
    xbmc.log('einthsan url %s' % url)
    s = requests.Session()
    name, url, lang, isithd, referurl = url.split(',')
    if xbmc.getCondVisibility('Skin.HasSetting(HomeMenuNoBasicButton)'):
        s = requests.Session()
        subc = False
    else:
        s, subc = login_info(s, referurl)

    xbmc.log(' result login s %s subc %s' % (s, subc))
    if isithd == 'itshd':
        ret = dialog.select('Quality Options', ['Play UHD', 'Play HD/SD'])
        if ret == 0:
            # isithd = 'itshd'
            if not subc:
                dialog.ok("[COLOR white] Astreamweb[/COLOR]",
                          "To Play UHD please subcribe a Premium account at ' +'https://einthusan.tv/")
                return

            mainurl = 'https://einthusan.tv/movie/watch/%s/?lang=%s&uhd=true' % (url, lang)

        if ret == 1:
            # isithd = 'itsnothd'
            mainurl = 'https://einthusan.tv/movie/watch/%s/?lang=%s' % (url, lang)

    else:
        mainurl = 'https://einthusan.tv/movie/watch/%s/?lang=%s' % (url, lang)

    mainurlajax = 'https://einthusan.tv/ajax/movie/watch/%s/?lang=%s' % (url, lang)
    headers = {'Origin': 'https://einthusan.tv', 'Referer': 'https://einthusan.tv/movie/browse/?lang=hindi',
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}

    import html.parser
    # htm=getUrl(mainurl,headers=headers,cookieJar=cookieJar)
    xbmc.log(mainurl, level=xbmc.LOGINFO)
    htm = s.get(mainurl, headers=headers, cookies=s.cookies, verify=False).text

    if ('SORRY' in htm) and ('Remaining quota is for premium members' in htm):
        dialog.ok("[COLOR white] Astreamweb[/COLOR]",
                  "Sorry Einthusan servers are almost maxed and reserved for Premium members")
        return

    xbmc.log(htm, level=xbmc.LOGINFO)
    lnk = re.findall('data-ejpingables=["\'](.*?)["\']', htm)[0]
    jdata = '{"EJOutcomes":"%s","NativeHLS":false}' % lnk
    h = html.parser.HTMLParser()
    gid = re.findall('data-pageid=["\'](.*?)["\']', htm)[0]
    gid = html.unescape(gid).encode("utf-8")
    postdata = {'xEvent': 'UIVideoPlayer.PingOutcome', 'xJson': jdata, 'arcVersion': '3', 'appVersion': '59',
                'gorilla.csrf.Token': gid}
    rdata = s.post(mainurlajax, headers=headers, data=postdata, cookies=s.cookies, verify=False).text
    r = json.loads(rdata)["Data"]["EJLinks"]
    xbmc.log(base64.b64decode(decodeEInth(r)).decode("utf-8"), level=xbmc.LOGINFO)
    lnk = json.loads(base64.b64decode(decodeEInth(r)).decode("utf-8"))["HLSLink"]
    lnk = einthusan_preferred_server(lnk, mainurl)
    xbmc.log(lnk, level=xbmc.LOGINFO)
    urlnew = lnk + ('|https://einthusan.ca&Referer=%s&User-Agent=%s' % (mainurl,
                                                                        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'))
    plugintools.play_resolved_url(urlnew)
    s.close()

    xbmc.Monitor().waitForAbort(1)
    if xbmc.Player().isPlaying() is False:
        xbmc.executebuiltin('Notification(Channel Unavailable at this moment,,10000,)')

    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def show_livetv(params):
    if xbmc.getCondVisibility('!Skin.HasSetting(HomeMenuNoBasicButton)'):
        vurl = params.get('url')
        self_url = vurl
        lang = params.get('extra')
        agent = '1'
        xbmc.log('__get_json show_hotstarplay vijayURL url: %s' % vurl)

        username = plugintools.get_setting('username')
        password = plugintools.get_setting('password')

        if vurl == '':
            vurl = "https://astreamweb.com/kodi/web/channels/json.php?lang=TEL&username=" + username + "&password=" + password
        if 'username' in vurl:  # vurl == 'password':
            if lang:
                if lang.lower() == 'tamil':
                    vurl = "https://astreamweb.com/kodi/web/channels/json.php?lang=TAM&username=" + username + "&password=" + password
                elif lang.lower() == 'telugu':
                    vurl = "https://astreamweb.com/kodi/web/channels/json.php?lang=TEL&username=" + username + "&password=" + password
                elif lang.lower() == 'malayalam':
                    vurl = "https://astreamweb.com/kodi/web/channels/json.php?lang=MAL&username=" + username + "&password=" + password
                elif lang.lower() == 'hindi':
                    vurl = "https://astreamweb.com/kodi/web/channels/json.php?lang=HIN&username=" + username + "&password=" + password
                else:
                    vurl = "https://astreamweb.com/kodi/web/channels/json.php?lang=" + lang + "&username=" + username + "&password=" + password
            else:
                lang = plugintools.get_setting('channellanguage')[0:3]
                vurl = "https://astreamweb.com/kodi/web/channels/json.php?lang=" + lang + "&username=" + username + "&password=" + password

        response = http_request(vurl).read().decode('utf-8')
        nodes = json.loads(response)

        per_page = '14' if 'widget' in params and params['widget'] == 'true' else __get_per_page()

        items = [x for x in nodes][:int(per_page)]

        items.reverse()

        if 'username' in vurl:
            for node in items:
                plugintools.add_item(action="play_vod", url=node['url'], title=node['title'],
                                     thumbnail=node['imageUrl'],
                                     isPlayable=True, folder=False)
        else:
            for node in items:
                plugintools.add_item(action="show_hotstarplayvideo", url=node['url'], title=node['title'],
                                     thumbnail=node['imageUrl'],
                                     page=agent,
                                     isPlayable=True, folder=False)

        if 'widget' in params and params['widget'] == 'true' and len(nodes) > int(per_page):
            plugintools.add_item(action='show_livetv', url=self_url, title='>> %s %s >>' % ('Page', 2), extra=lang)

        xbmcplugin.endOfDirectory(int(sys.argv[1]))
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    else:
        return False


def getseries_bycategory(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')

    category_id = params['category_id']
    username = plugintools.get_setting("username")
    password = plugintools.get_setting("password")

    page = params.get("page") if params.get("page") else '1'
    per_page = '14' if 'widget' in params and params['widget'] == 'true' else __get_per_page()
    sorting = params.get('extra') if params.get('extra') else ''

    result = scraper.__get_json({
        "task": "series",
        "category": category_id,
        "without_files": "1",
        "user": username,
        "per_page": per_page,
        "page": page
    })

    videos = result["data"]

    items = [{
        'label': re.sub('\([ 0-9]*?\)', '', video['title']),
        'thumbnail': video['cover'].replace(' ', '%20'),
        'cover': video['cover'].replace(' ', '%20'),
        'fanart': video['stills'],  # Jaysheel Code
        'thumb': video['cover'].replace(' ', '%20'),
        'iconImage': video['cover'].replace(' ', '%20'),
        'poster': video['cover'].replace(' ', '%20'),
        'art': {
            'thumb': video['cover'].replace(' ', '%20'),
            'poster': video['cover'].replace(' ', '%20'),
        },
        'info': {
            'originaltitle': video['title'],
            'tagline': video['collection'],
            'plot': video['plot'],
            'year': int(video['year']),
            'cast': video['cast'].replace(', ', ',').split(','),
            'director': video['director'],
            'rating': float(video['rating']),
            'votes': video['votes'],
            'genre': scraper.__resolve_categories(video['categories'])
        },
        'id': video['id'],
    } for video in videos]

    ListSearch = 'XBMC.Container.Update(%s)' % (
            sys.argv[0] + '?action=search&title=%s&url=%s&thumbnail=%s&plot=%s&extra=%s&page=%s')
    ListMovie = 'XBMC.Container.Update(%s)' % (
            sys.argv[0] + '?action=show_series&title=%s&url=%s&thumbnail=%s&plot=%s&extra=%s&page=%s')

    if int(page) > 1:
        prev_page = str(int(page) - 1)
        if category_id == '':
            plugintools.add_item(title='<< %s %s <<' % ('Page', prev_page),
                                 action='getseries2', extra=sorting, page=prev_page)
        elif category_id == '78':
            plugintools.add_item(title='<< %s %s <<' % ('Page', prev_page),
                                 action='getseries3', extra=sorting, page=prev_page)
        elif category_id == '82':
            plugintools.add_item(title='<< %s %s <<' % ('Page', prev_page),
                                 action='getseries', extra=sorting, page=prev_page)

    for item in items:
        xbmc.log('getseries info {}'.format(item["info"]["cast"]))
        xbmc.log('getseries info {}'.format(item["id"]))
        try:
            context_men = [('Movie information', 'XBMC.Action(Info)'),
                           ('Search for Movies by title', ListSearch % ('', '', '', '', '', ''))]

            for cast in item['info']['cast']:
                s_path = 'cast-%s' % cast
                context_men.append(('Movies with %s' % cast, ListMovie % ('', s_path, '', '', 'title%2CASC', '1')))


        except:
            traceback.print_exc()
        plugintools.add_itemcontext(action='show_series_files', title=item['label'], url=item['id'],
                                    info_labels=item['info'],
                                    thumbnail=item['thumbnail'], page='0', contextmenu=context_men, folder=True)

    total_page = math.ceil(int(result['pagination']['count']) / int(per_page))

    if total_page > int(page):
        if 'widget' in params and params['widget'] == 'true':
            next_page = '1'
        else:
            next_page = str(int(page) + 1)

        if category_id == '':
            plugintools.add_item(title='>> %s %s >>' % ('Page', next_page),
                                 action='getseries2', extra=sorting, page=next_page)
        elif category_id == '78':
            plugintools.add_item(title='>> %s %s >>' % ('Page', next_page),
                                 action='getseries3', extra=sorting, page=next_page)
        elif category_id == '82':
            plugintools.add_item(title='>> %s %s >>' % ('Page', next_page),
                                 action='getseries', extra=sorting, page=next_page)

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


###################################################################################################
if __name__ == '__main__':
    try:
        if xbmc.getCondVisibility('Skin.HasSetting(Activateservices)'):
            if xbmcgui.Window(10000).getProperty('My_Service_Running') != 'True':
                xbmc.log('service.py False ')
                xbmc.executebuiltin('XBMC.RunScript(special://home/addons/plugin.video.yams/service.py)', True)

            else:
                xbmc.log('service.py %s' % xbmcgui.Window(10000).getProperty('My_Service_Running'))
        else:
            xbmc.log('service.py %s' % xbmcgui.Window(10000).getProperty('My_Service_Running'))

        run()

    except ApiError as e_reason:
        xbmc.log('ERROR "%s"' % e_reason)
        if str(e_reason) == 'URLError':
            l1, l2, l3 = ('Cannot connect to Astreamweb Services.',
                          'Please ensure your internet is working',
                          'or try again later.',)
        elif str(e_reason) == 'HTTPError':
            l1, l2, l3 = ('Device Not Registered',
                          'Please click on astreamweb button',
                          'to activate device.',)
        else:
            l1, l2, l3 = ('Unknown Network problem',
                          'Please check your network connection',
                          'or try again later.',)
