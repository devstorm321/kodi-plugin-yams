# -*- coding: utf-8 -*-
#---------------------------------------------------------------------------
# Plugin Tools v1.0.8
#---------------------------------------------------------------------------
# License: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
# Based on code from youtube, parsedom and pelisalacarta addons
# Author:
# Jesús
# tvalacarta@gmail.com
# http://www.mimediacenter.info/plugintools
#---------------------------------------------------------------------------
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
#---------------------------------------------------------------------------

import urllib.request
import urllib.parse
import urllib.error
import urllib.request
import urllib.error
import urllib.parse
import re
import sys
import os
import time
import socket
import gzip
import traceback
from io import StringIO
from os import path as os_path


import xbmc
import xbmcvfs
import  xbmcplugin
import xbmcaddon
import xbmcgui


ADDON_ID       = xbmcaddon.Addon().getAddonInfo('id')
ADDONTITLE     = 'AStreamWeb'
PATH           = xbmcaddon.Addon().getAddonInfo('path')
HOME             = xbmcvfs.translatePath('special://home/')

ADDON           = xbmcvfs.translatePath(os.path.join(PATH, 'addon.xml'))

#reload(sys)
#sys.setdefaultencoding('utf8')

Module_log_enabled=False
Http_debug_log_enabled=False
LIST="list"
THUMBNAIL="thumbnail"
MOVIES="movies"
TV_SHOWS="tvshows"
SEASONS="seasons"
EPISODES="episodes"
OTHER="other"

# Suggested view codes for each type from different skins (initial list thanks to xbmcswift2 library)
ALL_VIEW_CODES={
    'list': {
        'skin.confluence': 50, # List
        'skin.aeon.nox': 50, # List
        'skin.droid': 50, # List
        'skin.quartz': 50, # List
        'skin.re-touched': 50, # List
    },
    'thumbnail': {
        'skin.confluence': 500, # Thumbnail
        'skin.aeon.nox': 500, # Wall
        'skin.droid': 51, # Big icons
        'skin.quartz': 51, # Big icons
        'skin.re-touched': 500, #Thumbnail
    },
    'movies': {
        'skin.confluence': 500, # Thumbnail 515, # Media Info 3
        'skin.aeon.nox': 500, # Wall
        'skin.droid': 51, # Big icons
        'skin.quartz': 52, # Media info
        'skin.re-touched': 500, #Thumbnail
    },
    'tvshows': {
        'skin.confluence': 500, # Thumbnail 515, # Media Info 3
        'skin.aeon.nox': 500, # Wall
        'skin.droid': 51, # Big icons
        'skin.quartz': 52, # Media info
        'skin.re-touched': 500, #Thumbnail
    },
    'seasons': {
        'skin.confluence': 50, # List
        'skin.aeon.nox': 50, # List
        'skin.droid': 50, # List
        'skin.quartz': 52, # Media info
        'skin.re-touched': 50, # List
    },
    'episodes': {
        'skin.confluence': 504, # Media Info
        'skin.aeon.nox': 518, # Infopanel
        'skin.droid': 50, # List
        'skin.quartz': 52, # Media info
        'skin.re-touched': 550, # Wide
    },
}
def __get_icon(title):
    title = title.replace(' ', '_')
    icon_path = xbmcvfs.translatePath(os.path.join(PATH, 'resources', 'images','%s.png' %title))
    #print icon_path
    if os_path.isfile(icon_path):
        return icon_path
    else:
        log('iconImage for "%s" does not exist!' % title)
        return 'DefaultFolder.png'

def log(message): 
    xbmc.log(message) # Write something on XBMC log
def _log(message): # Write this module messages on XBMC log
    if Module_log_enabled: 
        xbmc.log("" + message, xbmc.LOGINFO)
def get_params(): # Parse XBMC params - based on script.module.parsedom addon
    # _log("get_params")
    param_string = sys.argv[2]
    # param_string = urllib.parse.unquote_plus(param_string)
    _log("get_params >> param_string : %s" % param_string)
    commands={}
    if param_string:
        split_commands = param_string[param_string.find('?') + 1:].split('&')
        for command in split_commands:
            _log("get_params >> command : %s" % command)
            if len(command) > 0:
                if "=" in command: 
                    split_command=command.split('=')
                    key=split_command[0]
                    value=urllib.parse.unquote_plus(split_command[1])
                    commands[key]=value
                else: 
                    commands[command]=""
    _log("get_params >> commands: %s" % repr(commands))
    return commands

# Fetch text content from an URL
def read(url): 
    _log("read "+url)
    f=urllib.request.urlopen(url)
    data=f.read()
    f.close()
    return data

def read_body_and_headers(url,post=None,headers=[],follow_redirects=False,timeout=None):
    _log("read_body_and_headers "+url)
    if post is not None: _log("read_body_and_headers post="+post)
    if len(headers)==0: headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:18.0) Gecko/20100101 Firefox/18.0"])
    # Start cookie lib
    ficherocookies=os.path.join(get_data_path(),'cookies.dat')
    _log("read_body_and_headers cookies_file="+ficherocookies)
    cj=None
    ClientCookie=None
    cookielib=None
    try: 
        _log("read_body_and_headers importing cookielib")
        import http.cookiejar # Let's see if cookielib is available
    except ImportError:
        _log("read_body_and_headers cookielib no disponible") # If importing cookielib fails # let's try ClientCookie
        try: 
            _log("read_body_and_headers importing ClientCookie")
            import ClientCookie
        except ImportError: 
            _log("read_body_and_headers ClientCookie not available")
            urlopen=urllib.request.urlopen
            Request=urllib.request.Request # ClientCookie isn't available either
        else: 
            _log("read_body_and_headers ClientCookie available")
            urlopen=ClientCookie.urlopen
            Request=ClientCookie.Request
            cj=ClientCookie.MozillaCookieJar() # imported ClientCookie
    else:
        _log("read_body_and_headers cookielib available")
        urlopen=urllib.request.urlopen
        Request=urllib.request.Request
        cj=http.cookiejar.MozillaCookieJar() # importing cookielib worked
        # This is a subclass of FileCookieJar # that has useful load and save methods
    if cj is not None: # we successfully imported # one of the two cookie handling modules
        _log("read_body_and_headers Cookies enabled")
        if os.path.isfile(ficherocookies):
            _log("read_body_and_headers Reading cookie file")
            try: cj.load(ficherocookies) # if we have a cookie file already saved # then load the cookies into the Cookie Jar
            except: _log("read_body_and_headers Wrong cookie file, deleting...")
            os.remove(ficherocookies)
        # Now we need to get our Cookie Jar # installed in the opener
        # for fetching URLs
        if cookielib is not None:
            _log("read_body_and_headers opener using urllib2 (cookielib)")
            # if we use cookielib # then we get the HTTPCookieProcessor # and install the opener in urllib2
            if not follow_redirects: 
                opener=urllib.request.build_opener(
                    urllib.request.HTTPHandler(debuglevel=Http_debug_log_enabled),
                    urllib.request.HTTPCookieProcessor(cj),
                    NoRedirectHandler())
            else: opener=urllib.request.build_opener(urllib.request.HTTPHandler(debuglevel=Http_debug_log_enabled),urllib.request.HTTPCookieProcessor(cj))
            urllib.request.install_opener(opener)
        else:
            _log("read_body_and_headers opener using ClientCookie")
            # if we use ClientCookie # then we get the HTTPCookieProcessor # and install the opener in ClientCookie
            opener=ClientCookie.build_opener(ClientCookie.HTTPCookieProcessor(cj))
            ClientCookie.install_opener(opener)
    # -------------------------------------------------
    # Cookies instaladas, lanza la petición
    # -------------------------------------------------
    inicio=time.perf_counter() # Contador
    txheaders={} # Diccionario para las cabeceras
    if post is None: 
        _log("read_body_and_headers GET request") # Construye el request
    else: 
        _log("read_body_and_headers POST request")
    _log("read_body_and_headers ---------------------------") # Añade las cabeceras
    
    for header in headers: 
        _log("read_body_and_headers header %s=%s" % (str(header[0]),str(header[1])))
        txheaders[header[0]]=header[1]
    
    _log("read_body_and_headers ---------------------------")
    req=Request(url,post,txheaders)
    if timeout is None: 
        handle=urlopen(req)
    else:
        #Disponible en python 2.6 en adelante --> handle = urlopen(req, timeout=timeout) #Para todas las versiones:
        try: 
            deftimeout=socket.getdefaulttimeout()
            socket.setdefaulttimeout(timeout) 
            handle=urlopen(req)
            socket.setdefaulttimeout(deftimeout)
        except:
            for line in sys.exc_info(): _log( "%s" % line )
    cj.save(ficherocookies) # Actualiza el almacén de cookies
    # Lee los datos y cierra
    if handle.info().get('Content-Encoding')=='gzip': 
        buf=StringIO(handle.read())
        f=gzip.GzipFile(fileobj=buf)
        data=f.read()
    else: 
        data=handle.read()
        info=handle.info()
    _log("read_body_and_headers Response")
    returnheaders=[]
    _log("read_body_and_headers ---------------------------")
    for header in info: 
        _log("read_body_and_headers "+header+"="+info[header])
        returnheaders.append([header,info[header]])
    handle.close()
    _log("read_body_and_headers ---------------------------")
    # Tiempo transcurrido
    fin=time.perf_counter()
    _log("read_body_and_headers Downloaded in %d seconds " % (fin-inicio+1))
    _log("read_body_and_headers body="+data)
    return data,returnheaders

class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
            try:
                from urllib import addinfourl
            except:
                from six.moves.urllib import addinfourl    
            infourl = addinfourl(fp, headers, req.get_full_url())
            infourl.status = code
            infourl.code = code
            return infourl
    http_error_300 = http_error_302
    http_error_301 = http_error_302
    http_error_303 = http_error_302
    http_error_307 = http_error_302


def add_item(action="",title="",plot="",url="",thumbnail="",fanart="",iconImage="",show="",episode="",extra="",page="",info_labels=None,isPlayable=False,folder=True):
    _log("add_item action=["+action+"] title=["+title+"] url=["+url+"] thumbnail=["+thumbnail+"] fanart=["+fanart+"] show=["+show+"] episode=["+episode+"] extra=["+extra+"] page=["+page+"] isPlayable=["+str(isPlayable)+"] folder=["+str(folder)+"]")
    listitem = xbmcgui.ListItem(title)
    listitem.setArt({'icon':"DefaultVideo.png", 'thumb':thumbnail})

    if info_labels is None: 
        info_labels={"Title":title,"FileName":title,"Plot":plot}
        listitem.setInfo( "video", info_labels )
    if thumbnail != "":
        listitem.setArt({'poster':thumbnail, 'icon':thumbnail}) #,"fanart" : thumbnail if not fanart else fanart})

    #if fanart!="": listitem.setProperty('fanart_image',fanart)#
    xbmcplugin.setPluginFanart(int(sys.argv[1]),fanart)
    if url.startswith("plugin://"):
        itemurl = url
        listitem.setProperty('IsPlayable','true')
    elif isPlayable:
        listitem.setProperty("Video","true")
        listitem.setProperty('IsPlayable','true');
        try :
            itemurl='%s?action=%s&title=%s&url=%s&thumbnail=%s&plot=%s&extra=%s&page=%s'%(sys.argv[0],action,urllib.parse.quote_plus(title),urllib.parse.quote_plus(url),urllib.parse.quote_plus(thumbnail),urllib.parse.quote_plus(plot),
                urllib.parse.quote_plus(extra),urllib.parse.quote_plus(page))

        except Exception as e :
            if 'KeyError' in str(e):
                urllib.parse.quote_plus(title.encode('utf-8'), safe=':/'.encode('utf-8'))
                urllib.parse.quote_plus(url.encode('utf-8'), safe=':/'.encode('utf-8'))
                itemurl='%s?action=%s&title=%s&url=%s&thumbnail=%s&plot=%s&extra=%s&page=%s'%(sys.argv[0],action,title,url,urllib.parse.quote_plus(thumbnail),plot,urllib.parse.quote_plus(extra),urllib.parse.quote_plus(page))
            else :
                itemurl ='%s?action=%s'%(sys.argv[0],action)
    else:
        try :
            itemurl = '%s?action=%s&title=%s&url=%s&thumbnail=%s&plot=%s&extra=%s&page=%s'%(sys.argv[0],action,urllib.parse.quote_plus(title),urllib.parse.quote_plus(url),urllib.parse.quote_plus(thumbnail),urllib.parse.quote_plus(plot),
                urllib.parse.quote_plus(extra),urllib.parse.quote_plus(page))
        except Exception as e :
            raise e
            if 'KeyError' in str(e):
                xbmc.log('erreur excep {}'.format(e))
                urllib.parse.quote_plus(title.encode('utf-8'), safe=':/'.encode('utf-8'))
                urllib.parse.quote_plus(url.encode('utf-8'), safe=':/'.encode('utf-8'))
                urllib.parse.quote_plus(extra.encode('utf-8'), safe=':/'.encode('utf-8'))
                itemurl='%s?action=%s&title=%s&url=%s&thumbnail=%s&plot=%s&extra=%s&page=%s'%(sys.argv[0],action,title,url,urllib.parse.quote_plus(thumbnail),urllib.parse.quote_plus(plot),extra,urllib.parse.quote_plus(page))

            else :
                urllib.parse.quote_plus(title.encode('utf-8'), safe=':/'.encode('utf-8'))
                urllib.parse.quote_plus(url.encode('utf-8'), safe=':/'.encode('utf-8'))
                urllib.parse.quote_plus(extra.encode('utf-8'), safe=':/'.encode('utf-8'))
                itemurl='%s?action=%s&title=%s&url=%s&thumbnail=%s&plot=%s&extra=%s&page=%s'%(sys.argv[0],action,title,url,urllib.parse.quote_plus(thumbnail),urllib.parse.quote_plus(plot),extra,urllib.parse.quote_plus(page))
                xbmc.log('erreur itemurl {}'.format(itemurl))
    _log('Item url: %s' % url)
    try:
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=itemurl, listitem=listitem, isFolder=folder)
    except:
        traceback.print_exc()

def add_itemcontext(action="",title="",plot="",url="",thumbnail="",fanart="",iconImage="",show="",episode="",extra="",page="",info_labels=None,contextmenu=None,isPlayable=False,folder=True):
    _log("add_item action=["+action+"] title=["+title+"] url=["+url+"] thumbnail=["+thumbnail+"] fanart=["+fanart+"] show=["+show+"] episode=["+episode+"] extra=["+extra+"] page=["+page+"] isPlayable=["+str(isPlayable)+"] folder=["+str(folder)+"]")
    listitem=xbmcgui.ListItem(title)
    listitem.setArt({'icon':"DefaultVideo.png", 'thumb':thumbnail})
    if info_labels is None: 
        info_labels={"Title":title,"FileName":title,"Plot":plot}
        listitem.setInfo( "video", info_labels )
    if thumbnail != "":
        listitem.setArt({'poster': thumbnail, 'icon': thumbnail}) #,"fanart" : thumbnail if not fanart else fanart})

    #if fanart!="": listitem.setProperty('fanart_image',fanart)#
    xbmcplugin.setPluginFanart(int(sys.argv[1]),fanart)

    if plot :
        plot = plot.replace("’"," ").encode('ascii', 'ignore');xbmc.log('corrige plot {}'.format(plot))
    if url.startswith("plugin://"): 
        itemurl = url
        listitem.setProperty('IsPlayable','true')
    elif isPlayable:
        listitem.setProperty("Video","true")
        listitem.setProperty('IsPlayable','true')
        try :
            itemurl='%s?action=%s&title=%s&url=%s&thumbnail=%s&plot=%s&extra=%s&page=%s'%(sys.argv[0],action,urllib.parse.quote_plus(title),urllib.parse.quote_plus(url),urllib.parse.quote_plus(thumbnail),urllib.parse.quote_plus(plot),
                urllib.parse.quote_plus(extra),urllib.parse.quote_plus(page))

        except Exception as e :
            if 'KeyError' in str(e):
                xbmc.log('erreur excep {}'.format(e))
                urllib.parse.quote_plus(title.encode('utf-8'), safe=':/'.encode('utf-8'))
                urllib.parse.quote_plus(url.encode('utf-8'), safe=':/'.encode('utf-8'))
                itemurl='%s?action=%s&title=%s&url=%s&thumbnail=%s&plot=%s&extra=%s&page=%s'%(sys.argv[0],action,title,url,urllib.parse.quote_plus(thumbnail),urllib.parse.quote_plus(plot),urllib.parse.quote_plus(extra),urllib.parse.quote_plus(page))

    else:
        try :
            itemurl='%s?action=%s&title=%s&url=%s&thumbnail=%s&plot=%s&extra=%s&page=%s'%(sys.argv[0],action,urllib.parse.quote_plus(title),urllib.parse.quote_plus(url),urllib.parse.quote_plus(thumbnail),urllib.parse.quote_plus(plot),
                urllib.parse.quote_plus(extra),urllib.parse.quote_plus(page))
        except Exception as e :
            if 'KeyError' in str(e):
                xbmc.log('erreur excep {}'.format(e))
                urllib.parse.quote_plus(title.encode('utf-8'), safe=':/'.encode('utf-8'))
                urllib.parse.quote_plus(url.encode('utf-8'), safe=':/'.encode('utf-8'))
                itemurl='%s?action=%s&title=%s&url=%s&thumbnail=%s&plot=%s&extra=%s&page=%s'%(sys.argv[0],action,title,url,urllib.parse.quote_plus(thumbnail),urllib.parse.quote_plus(plot),urllib.parse.quote_plus(extra),urllib.parse.quote_plus(page))

    if not contextmenu == None: 
        listitem.addContextMenuItems(contextmenu)

    try:
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=itemurl, listitem=listitem, isFolder=folder)
    except:
        traceback.print_exc()

def close_item_list(): 
    _log("close_item_list")
    xbmcplugin.endOfDirectory(handle=int(sys.argv[1]),succeeded=True,cacheToDisc=False)

def play_resolved_url(url,title=''):
    _log("play_resolved_url ["+url+"]")
    listitem=xbmcgui.ListItem(path=url)
    listitem.setProperty('IsPlayable','true')
    if title: 
        listitem.setLabel(title)
    return xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)

def direct_play(url,title=""):
    _log("direct_play ["+url+"]")
    try: 
        xlistitem=xbmcgui.ListItem(title, path=url)
    except: 
        xlistitem=xbmcgui.ListItem(title)
    
    xlistitem.setArt({'icon':"DefaultVideo.png"})
    #xlistitem.setInfo("video",{"Title":title})
    playlist=xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    playlist.add(url,xlistitem)
    player_type=xbmc.PLAYER_CORE_AUTO
    xbmcPlayer=xbmc.Player(player_type)
    xbmcPlayer.play(playlist)
    xlistitem.setInfo("video",{"Title":title})
    playlist=xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    playlist.add(url,xlistitem)
    xbmcPlayer=xbmc.Player()
    xbmcPlayer.play(playlist)

def show_picture(url):
    local_folder=os.path.join(get_data_path(),"images")
    if not os.path.exists(local_folder):
        try: 
            os.mkdir(local_folder)
        except: 
            pass
    local_file=os.path.join(local_folder,"temp.jpg")
    urllib.request.urlretrieve(url,local_file) # Download picture
    xbmc.executebuiltin("SlideShow("+local_folder+")") # Show picture
def get_temp_path(): 
    _log("get_temp_path")
    dev = xbmcvfs.translatePath("special://temp/")
    _log("get_temp_path ->'"+str(dev)+"'")
    return dev

def get_runtime_path(): 
    _log("get_runtime_path")
    dev=xbmcvfs.translatePath(__settings__.getAddonInfo('Path'))
    _log("get_runtime_path ->'"+str(dev)+"'")
    return dev

def get_data_path():
    _log("get_data_path")
    dev=xbmcvfs.translatePath(__settings__.getAddonInfo('Profile'))
    if not os.path.exists(dev): 
        os.makedirs(dev) # Parche para XBMC4XBOX
        _log("get_data_path ->'"+str(dev)+"'")
    return dev

def get_setting(name): 
    _log("get_setting name='"+name+"'")
    dev=__settings__.getSetting(name)
    _log("get_setting ->'"+str(dev)+"'")
    return dev

def set_setting(name,value): 
    _log("set_setting name='"+name+"','"+value+"'")
    __settings__.setSetting( name,value )

def open_settings_dialog(): 
    _log("open_settings_dialog")
    __settings__.openSettings()

def get_localized_string(code):
    _log("get_localized_string code="+str(code))
    dev=__language__(code)
    try: 
        dev=dev.encode("utf-8")
    except: 
        pass
    _log("get_localized_string ->'"+dev+"'")
    return dev
def keyboard_input(default_text="",title="",hidden=False):
    _log("keyboard_input default_text='"+default_text+"'")
    keyboard=xbmc.Keyboard(default_text,title,hidden)
    keyboard.doModal()
    if (keyboard.isConfirmed()): 
        tecleado=keyboard.getText()
    else: 
        tecleado=""
    _log("keyboard_input ->'"+tecleado+"'")
    return tecleado
def message(text1,text2="",text3=""):
    _log("message text1='"+text1+"', text2='"+text2+"', text3='"+text3+"'")
    if text3=="": 
        xbmcgui.Dialog().ok(text1,text2)
    elif text2=="": 
        xbmcgui.Dialog().ok("",text1)
    else: 
        xbmcgui.Dialog().ok(text1,text2,text3)
def message_yes_no(text1,text2="",text3=""):
    _log("message_yes_no text1='"+text1+"', text2='"+text2+"', text3='"+text3+"'")
    if text3=="": 
        yes_pressed=xbmcgui.Dialog().yesno(text1,text2)
    elif text2=="": 
        yes_pressed=xbmcgui.Dialog().yesno("",text1)
    else: 
        yes_pressed=xbmcgui.Dialog().yesno(text1,text2,text3)
    return yes_pressed
def selector(option_list,title="Select one"):
    _log("selector title='"+title+"', options="+repr(option_list))
    dia=xbmcgui.Dialog()
    selection=dia.select(title,option_list)
    return selection
def set_view(view_mode, view_code=0):
    _log("set_view view_mode='"+view_mode+"', view_code="+str(view_code))
    # Set the content for extended library views if needed
    if view_mode==MOVIES: 
        _log("set_view content is movies")
        xbmcplugin.setContent( int(sys.argv[1]) ,"movies" )
    elif view_mode==TV_SHOWS: 
        _log("set_view content is tvshows")
        xbmcplugin.setContent( int(sys.argv[1]) ,"tvshows" )
    elif view_mode==SEASONS: 
        _log("set_view content is seasons")
        xbmcplugin.setContent( int(sys.argv[1]) ,"seasons" )
    elif view_mode==EPISODES: 
        _log("set_view content is episodes")
        xbmcplugin.setContent( int(sys.argv[1]) ,"episodes" )
    skin_name=xbmc.getSkinDir() # Reads skin name
    _log("set_view skin_name='"+skin_name+"'")
    try:
        if view_code==0:
            _log("set_view view mode is "+view_mode)
            view_codes=ALL_VIEW_CODES.get(view_mode)
            view_code=view_codes.get(skin_name)
            _log("set_view view code for "+view_mode+" in "+skin_name+" is "+str(view_code))
            xbmc.executebuiltin("Container.SetViewMode("+str(view_code)+")")
        else:
            _log("set_view view code forced to "+str(view_code))
            xbmc.executebuiltin("Container.SetViewMode("+str(view_code)+")")
    except:
        _log("Unable to find view code for view mode "+str(view_mode)+" and skin "+skin_name)

# Kill Kodi
def killxbmc():
    choice = message_yes_no(
        "Force Close Kodi", "You are about to close Kodi", "Would you like to continue?")
    if choice == 0:
        return
    elif choice == 1:
        pass
    myplatform = str(platform())
    print("Platform: " + str(myplatform))
    try:
        os._exit(1)
    except:
        pass

    if myplatform == 'osx':
        print("############   try osx force close  #################")
        try:
            os.system('killall -9 XBMC')
        except:
            pass
        try:
            os.system('killall -9 Kodi')
        except:
            pass
        message(ADDONTITLE, "If you\'re seeing this message it means the force close was unsuccessful. Please force close XBMC/Kodi [COLOR=lime]DO NOT[/COLOR] exit cleanly via the menu.")
    elif myplatform == 'linux':
        print("############   try linux force close  #################")
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
        message(ADDONTITLE, "If you\'re seeing this message it means the force close was unsuccessful. Please force close XBMC/Kodi [COLOR=lime]DO NOT[/COLOR] exit cleanly via the menu.", '')
    elif myplatform == 'android':
        print("############   try android force close  #################")
        try:
            os._exit(1)
        except:
            pass
        try:
            os.system('adb shell am force-stop org.xbmc.kodi')
        except:
            pass
        try:
            os.system('adb shell am force-stop org.kodi')
        except:
            pass
        try:
            os.system('adb shell am force-stop org.xbmc.xbmc')
        except:
            pass
        try:
            os.system('adb shell am force-stop org.xbmc')
        except:
            pass
        try:
            os.system('adb shell am force-stop com.semperpax.spmc16')
        except:
            pass
        try:
            os.system('adb shell am force-stop com.spmc16')
        except:
            pass
        time.sleep(5)
        message(
            ADDONTITLE, "Press the HOME button on your remote and [COLOR=red][B]FORCE STOP[/B][/COLOR] KODI via the Manage Installed Applications menu in settings on your Amazon home page then re-launch KODI")
    elif myplatform == 'windows':
        print("############   try windows force close  #################")
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
            os.system('TASKKILL /im Kodi.exe /f')
        except:
            pass
        try:
            os.system('@ECHO off')
            os.system('TASKKILL /im XBMC.exe /f')
        except:
            pass
        message(ADDONTITLE, "If you\'re seeing this message it means the force close was unsuccessful. Please force close XBMC/Kodi [COLOR=lime]DO NOT[/COLOR] exit cleanly via the menu.", "Use task manager and NOT ALT F4")
    else:
        print("############   try atv force close  #################")
        try:
            os._exit(1)
        except:
            pass
        try:
            os.system('killall AppleTV')
        except:
            pass
        print("############   try raspbmc force close  #################")
        try:
            os.system('sudo initctl stop kodi')
        except:
            pass
        try:
            os.system('sudo initctl stop xbmc')
        except:
            pass
        message(ADDONTITLE, "If you\'re seeing this message it means the force close was unsuccessful. Please force close XBMC/Kodi [COLOR=lime]DO NOT[/COLOR] exit via the menu.", "iOS detected.  Press and hold both the Sleep/Wake and Home button for at least 10 seconds, until you see the Apple logo.")


# Get Current platform
def platform():
    if xbmc.getCondVisibility('system.platform.android'):
        return 'android'
    elif xbmc.getCondVisibility('system.platform.linux'):
        return 'linux'
    elif xbmc.getCondVisibility('system.platform.windows'):
        return 'windows'
    elif xbmc.getCondVisibility('system.platform.osx'):
        return 'osx'
    elif xbmc.getCondVisibility('system.platform.atv2'):
        return 'atv2'
    elif xbmc.getCondVisibility('system.platform.ios'):
        return 'ios'
################################################################################


__settings__=xbmcaddon.Addon(id=ADDON_ID)
__language__=__settings__.getLocalizedString
