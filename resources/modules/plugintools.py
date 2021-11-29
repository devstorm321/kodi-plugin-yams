# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Plugin Tools v1.0.8
# ---------------------------------------------------------------------------
# License: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
# Based on code from youtube, parsedom and pelisalacarta addons
# Author:
# Jesús
# tvalacarta@gmail.com
# http://www.mimediacenter.info/plugintools
# ---------------------------------------------------------------------------
# Changelog:
# 1.0.0
# - First release
# 1.0.1
# - If find_single_match can't find anything, it returns an empty string
# - Remove addon id from this module, so it remains clean
# 1.0.2
# - Added parameter on "add_item" to say that item is playable
# 1.0.3
# - Added direct play
# - Fixed bug when video isPlayable=True
# 1.0.4
# - Added get_temp_path, get_runtime_path, get_data_path
# - Added get_setting, set_setting, open_settings_dialog and get_localized_string
# - Added keyboard_input
# - Added message
# 1.0.5
# - Added read_body_and_headers for advanced http handling
# - Added show_picture for picture addons support
# - Added optional parameters "title" and "hidden" to keyboard_input
# 1.0.6
# - Added fanart, show, episode and infolabels to add_item
# 1.0.7
# - Added set_view function
# 1.0.8
# - Added selector
# ---------------------------------------------------------------------------

import os
import sys
import traceback
import urllib.error
import urllib.error
import urllib.parse
import urllib.parse
import urllib.request
import urllib.request
from os import path as os_path

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs

ADDON_ID = xbmcaddon.Addon('plugin.video.yams').getAddonInfo('id')
ADDONTITLE = 'AStreamWeb'
PATH = xbmcaddon.Addon('plugin.video.yams').getAddonInfo('path')
HOME = xbmcvfs.translatePath('special://home/')

ADDON = xbmcvfs.translatePath(os.path.join(PATH, 'addon.xml'))

Module_log_enabled = False
Http_debug_log_enabled = False
LIST = "list"
THUMBNAIL = "thumbnail"
MOVIES = "movies"
TV_SHOWS = "tvshows"
SEASONS = "seasons"
EPISODES = "episodes"
OTHER = "other"


def __get_icon(title):
    title = title.replace(' ', '_')
    icon_path = xbmcvfs.translatePath(os.path.join(PATH, 'resources', 'images', '%s.png' % title))
    # print icon_path
    if os_path.isfile(icon_path):
        return icon_path
    else:
        log('iconImage for "%s" does not exist!' % title)
        return 'DefaultFolder.png'


def log(message):
    xbmc.log(message)  # Write something on XBMC log


def _log(message):  # Write this module messages on XBMC log
    if Module_log_enabled:
        xbmc.log("" + message, xbmc.LOGINFO)


def get_params():  # Parse XBMC params - based on script.module.parsedom addon
    # _log("get_params")
    param_string = sys.argv[2]
    # param_string = urllib.parse.unquote_plus(param_string)
    _log("get_params >> param_string : %s" % param_string)
    commands = {}
    if param_string:
        split_commands = param_string[param_string.find('?') + 1:].split('&')
        for command in split_commands:
            _log("get_params >> command : %s" % command)
            if len(command) > 0:
                if "=" in command:
                    split_command = command.split('=')
                    key = split_command[0]
                    value = urllib.parse.unquote_plus(split_command[1])
                    commands[key] = value
                else:
                    commands[command] = ""
    _log("get_params >> commands: %s" % repr(commands))
    return commands


# Fetch text content from an URL
def read(url):
    _log("read " + url)
    f = urllib.request.urlopen(url)
    data = f.read()
    f.close()
    return data


def add_item(action="", title="", plot="", url="", thumbnail="", fanart="", iconImage="", show="", episode="", extra="",
             page="", info_labels=None, isPlayable=False, folder=True):
    _log(
        "add_item action=[" + action + "] title=[" + title + "] url=[" + url + "] thumbnail=[" + thumbnail + "] fanart=[" + fanart + "] show=[" + show + "] episode=[" + episode + "] extra=[" + extra + "] page=[" + page + "] isPlayable=[" + str(
            isPlayable) + "] folder=[" + str(folder) + "]")
    listitem = xbmcgui.ListItem(title)
    listitem.setArt({'icon': "DefaultVideo.png", 'thumb': thumbnail})

    if info_labels is None:
        info_labels = {"Title": title, "FileName": title, "Plot": plot}
        listitem.setInfo("video", info_labels)
    if thumbnail != "":
        listitem.setArt({'poster': thumbnail, 'icon': thumbnail})  # ,"fanart" : thumbnail if not fanart else fanart})

    # if fanart!="": listitem.setProperty('fanart_image',fanart)#
    xbmcplugin.setPluginFanart(int(sys.argv[1]), fanart)
    if url.startswith("plugin://"):
        itemurl = url
        listitem.setProperty('IsPlayable', 'true')
    elif isPlayable:
        listitem.setProperty("Video", "true")
        listitem.setProperty('IsPlayable', 'true');
        try:
            itemurl = '%s?action=%s&title=%s&url=%s&thumbnail=%s&plot=%s&extra=%s&page=%s' % (
                sys.argv[0], action, urllib.parse.quote_plus(title), urllib.parse.quote_plus(url),
                urllib.parse.quote_plus(thumbnail), urllib.parse.quote_plus(plot),
                urllib.parse.quote_plus(extra), urllib.parse.quote_plus(page))

        except Exception as e:
            if 'KeyError' in str(e):
                urllib.parse.quote_plus(title, safe=':/')
                urllib.parse.quote_plus(url, safe=':/')
                itemurl = '%s?action=%s&title=%s&url=%s&thumbnail=%s&plot=%s&extra=%s&page=%s' % (
                    sys.argv[0], action, title, url, urllib.parse.quote_plus(thumbnail), plot,
                    urllib.parse.quote_plus(extra), urllib.parse.quote_plus(page))
            else:
                itemurl = '%s?action=%s' % (sys.argv[0], action)
    else:
        try:
            itemurl = '%s?action=%s&title=%s&url=%s&thumbnail=%s&plot=%s&extra=%s&page=%s' % (
                sys.argv[0], action, urllib.parse.quote_plus(title), urllib.parse.quote_plus(url),
                urllib.parse.quote_plus(thumbnail), urllib.parse.quote_plus(plot),
                urllib.parse.quote_plus(extra), urllib.parse.quote_plus(page))
        except Exception as e:
            if 'KeyError' in str(e):
                xbmc.log('erreur excep {}'.format(e))
                urllib.parse.quote_plus(title, safe=':/')
                urllib.parse.quote_plus(url, safe=':/')
                urllib.parse.quote_plus(extra, safe=':/')
                itemurl = '%s?action=%s&title=%s&url=%s&thumbnail=%s&plot=%s&extra=%s&page=%s' % (
                    sys.argv[0], action, title, url, urllib.parse.quote_plus(thumbnail), urllib.parse.quote_plus(plot),
                    extra, urllib.parse.quote_plus(page))

            else:
                urllib.parse.quote_plus(title, safe=':/')
                urllib.parse.quote_plus(url, safe=':/')
                urllib.parse.quote_plus(extra, safe=':/')
                itemurl = '%s?action=%s&title=%s&url=%s&thumbnail=%s&plot=%s&extra=%s&page=%s' % (
                    sys.argv[0], action, title, url, urllib.parse.quote_plus(thumbnail), urllib.parse.quote_plus(plot),
                    extra, urllib.parse.quote_plus(page))
                xbmc.log('erreur itemurl {}'.format(itemurl))
    _log('Item url: %s' % url)
    try:
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=itemurl, listitem=listitem, isFolder=folder)
    except:
        traceback.print_exc()


def add_itemcontext(action="", title="", plot="", url="", thumbnail="", fanart="", iconImage="", show="", episode="",
                    extra="", page="", info_labels=None, contextmenu=None, isPlayable=False, folder=True):
    _log(
        "add_item action=[" + action + "] title=[" + title + "] url=[" + url + "] thumbnail=[" + thumbnail + "] fanart=[" + fanart + "] show=[" + show + "] episode=[" + episode + "] extra=[" + extra + "] page=[" + page + "] isPlayable=[" + str(
            isPlayable) + "] folder=[" + str(folder) + "]")
    listitem = xbmcgui.ListItem(title)
    listitem.setArt({'icon': "DefaultVideo.png", 'thumb': thumbnail})
    if info_labels is None:
        info_labels = {"Title": title, "FileName": title, "Plot": plot}
        listitem.setInfo("video", info_labels)
    if thumbnail != "":
        listitem.setArt({'poster': thumbnail, 'icon': thumbnail})  # ,"fanart" : thumbnail if not fanart else fanart})

    # if fanart!="": listitem.setProperty('fanart_image',fanart)#
    xbmcplugin.setPluginFanart(int(sys.argv[1]), fanart)

    if plot:
        plot = plot.replace("’", " ")
        xbmc.log('corrige plot {}'.format(plot))
    if url.startswith("plugin://"):
        itemurl = url
        listitem.setProperty('IsPlayable', 'true')
    elif isPlayable:
        listitem.setProperty("Video", "true")
        listitem.setProperty('IsPlayable', 'true')
        try:
            itemurl = '%s?action=%s&title=%s&url=%s&thumbnail=%s&plot=%s&extra=%s&page=%s' % (
                sys.argv[0], action, urllib.parse.quote_plus(title), urllib.parse.quote_plus(url),
                urllib.parse.quote_plus(thumbnail), urllib.parse.quote_plus(plot),
                urllib.parse.quote_plus(extra), urllib.parse.quote_plus(page))

        except Exception as e:
            if 'KeyError' in str(e):
                xbmc.log('erreur excep {}'.format(e))
                urllib.parse.quote_plus(title, safe=':/')
                urllib.parse.quote_plus(url, safe=':/')
                itemurl = '%s?action=%s&title=%s&url=%s&thumbnail=%s&plot=%s&extra=%s&page=%s' % (
                    sys.argv[0], action, title, url, urllib.parse.quote_plus(thumbnail), urllib.parse.quote_plus(plot),
                    urllib.parse.quote_plus(extra), urllib.parse.quote_plus(page))

    else:
        try:
            itemurl = '%s?action=%s&title=%s&url=%s&thumbnail=%s&plot=%s&extra=%s&page=%s' % (
                sys.argv[0], action, urllib.parse.quote_plus(title), urllib.parse.quote_plus(url),
                urllib.parse.quote_plus(thumbnail), urllib.parse.quote_plus(plot),
                urllib.parse.quote_plus(extra), urllib.parse.quote_plus(page))
        except Exception as e:
            if 'KeyError' in str(e):
                xbmc.log('erreur excep {}'.format(e))
                urllib.parse.quote_plus(title, safe=':/')
                urllib.parse.quote_plus(url, safe=':/')
                itemurl = '%s?action=%s&title=%s&url=%s&thumbnail=%s&plot=%s&extra=%s&page=%s' % (
                    sys.argv[0], action, title, url, urllib.parse.quote_plus(thumbnail), urllib.parse.quote_plus(plot),
                    urllib.parse.quote_plus(extra), urllib.parse.quote_plus(page))

    if contextmenu:
        listitem.addContextMenuItems(contextmenu)

    try:
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=itemurl, listitem=listitem, isFolder=folder)
    except:
        traceback.print_exc()


def play_resolved_url(url, title=''):
    _log("play_resolved_url [" + url + "]")
    listitem = xbmcgui.ListItem(path=url)
    listitem.setProperty('IsPlayable', 'true')
    if title:
        listitem.setLabel(title)
    return xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)


def direct_play(url, title=""):
    _log("direct_play [" + url + "]")
    try:
        xlistitem = xbmcgui.ListItem(title, path=url)
    except:
        xlistitem = xbmcgui.ListItem(title)

    xlistitem.setArt({'icon': "DefaultVideo.png"})
    # xlistitem.setInfo("video",{"Title":title})
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    playlist.add(url, xlistitem)
    player_type = xbmc.PLAYER_CORE_AUTO
    xbmcPlayer = xbmc.Player(player_type)
    xbmcPlayer.play(playlist)
    xlistitem.setInfo("video", {"Title": title})
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    playlist.add(url, xlistitem)
    xbmcPlayer = xbmc.Player()
    xbmcPlayer.play(playlist)


def get_setting(name):
    _log("get_setting name='" + name + "'")
    dev = __settings__.getSetting(name)
    _log("get_setting ->'" + str(dev) + "'")
    return dev


def set_setting(name, value):
    _log("set_setting name='" + name + "','" + value + "'")
    __settings__.setSetting(name, value)


def open_settings_dialog():
    _log("open_settings_dialog")
    __settings__.openSettings()


def message(text1, text2="", text3=""):
    _log("message text1='" + text1 + "', text2='" + text2 + "', text3='" + text3 + "'")
    if text3 == "":
        xbmcgui.Dialog().ok(text1, text2)
    elif text2 == "":
        xbmcgui.Dialog().ok("", text1)
    else:
        xbmcgui.Dialog().ok(text1, text2, text3)


def message_yes_no(text1, text2="", text3=""):
    _log("message_yes_no text1='" + text1 + "', text2='" + text2 + "', text3='" + text3 + "'")
    if text3 == "":
        yes_pressed = xbmcgui.Dialog().yesno(text1, text2)
    elif text2 == "":
        yes_pressed = xbmcgui.Dialog().yesno("", text1)
    else:
        yes_pressed = xbmcgui.Dialog().yesno(text1, text2, text3)
    return yes_pressed


################################################################################


__settings__ = xbmcaddon.Addon(id=ADDON_ID)
__language__ = __settings__.getLocalizedString
