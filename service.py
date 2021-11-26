import importlib
import os
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request

import feedparser
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

import resources.modules.scraper as scraper
import resources.modules.yamsutils as yamsutils
from resources.modules.scraper import get_mac

try:
    import simplejson as json
except:
    print(('Plugin Error', 'simplejson import error: limited functionality'))
    pass

import threading
from urllib.request import urlopen
import urllib.request, urllib.parse, urllib.error

Addon = xbmcaddon.Addon(id='plugin.video.yams')
# Addon = xbmcaddon.Addon(id='service.yams-msg')

PATH = xbmcvfs.translatePath(Addon.getAddonInfo('profile'))
ADDON_PATH = xbmcvfs.translatePath(Addon.getAddonInfo('path'))
FILE = os.path.join(PATH, 'items.json')
RSS_URLS = [
    'http://api.astreamweb.com/feed.php?username=%s' % (xbmcaddon.Addon('plugin.video.yams').getSetting("username")),
    'http://astreamweb.com/kodi/rssnew/rss.xml'
]

TITLE = 'AStreamWeb Info Panel'
CHECK_INTERVAL = 60
SUBCHECK_INTERVAL = 3600
IP_INTERVAL = 1800
DIALOG_INTERVAL = 21600
digest = yamsutils.__digest(ADDON_PATH)
xbmc.log("d2Fpc3Rpbmd5b3VydGltZV9hY2NvdW50YmxvY2tlZA {}".format(digest))

digest = "39e8d194da075e2c41d8f8648ae94764a6a8c9f98a8fb05ae4d8a62f3ce1ea91"

__settings__ = xbmcaddon.Addon(id='plugin.video.yams')

msgapi = "We do not recognise this device, This device will be logged out."
dialog = xbmcgui.Dialog()


def init():
    global activity_info


class ASMessage(xbmcgui.WindowXML):
    ACTION_EXIT = [9, 92, 10, 13]
    CTR_TEXT = 30002
    CTR_OK = 30001

    def __init__(self, text, *args, **kwargs):
        self.message = kwargs.get('message')
        self.title = kwargs.get('title')

    def onInit(self):
        self.txt = self.getControl(self.CTR_TEXT)
        self.txt.setText(self.message)

    def onClick(self, controlId):
        if controlId == self.CTR_OK:
            self.close()

    def onFocus(self, controlId):
        pass

    def onAction(self, action):
        if action in self.ACTION_EXIT:
            self.close()


def app_active():
    scraper.__set_digest(digest)
    api_digest = scraper.digest
    try:
        ip = urllib.request.urlopen("https://astreamweb.com/kodi/ip.php").read().decode('utf-8')
    except Exception as e:
        dialog = xbmcgui.Dialog()
        dialog.notification('Connection Failure',
                            'Cannot connect to Astreamweb Services. Please ensure your internet is working or try again later.',
                            xbmcgui.NOTIFICATION_ERROR)
        xbmc.log('No response from https://astreamweb.com/kodi/ip.php')
        return

    username = xbmcaddon.Addon('plugin.video.yams').getSetting('username')
    password = xbmcaddon.Addon('plugin.video.yams').getSetting('password')
    authenticated, message, status_code = scraper.check_login(username, password,
                                                              xbmcaddon.Addon('plugin.video.yams').getSetting(
                                                                  'session'))
    if not authenticated:
        pass
    while not xbmc.Monitor().abortRequested():
        # url = "http://yamsonline.com/jsonapi.php?task=updatesession&option=com_jsonapi&format=json&session=%s&user=%s&version=v2&password=%s" % (__settings__.getSetting("session"), __settings__.getSetting("username"), __settings__.getSetting("password"))
        url = "https://api.yamsonline.com/api?task=pingbox&option=com_jsonapi&format=json&session=%s&user=%s&version=v2&ipaddress=%s&v=%s&digest=%s" % (
            get_mac(), xbmcaddon.Addon('plugin.video.yams').getSetting("username"), ip,
            xbmc.getInfoLabel('System.AddonVersion(plugin.video.yams)') + '- S' + xbmc.getInfoLabel(
                'System.AddonVersion(skin.estuary)') + '- APK' + xbmc.getInfoLabel(
                'System.AddonVersion(service.xbmc.versioncheck)') + '- OS' + xbmc.getInfoLabel(
                'System.OSVersionInfo') + '- KOD' + xbmc.getInfoLabel('System.BuildVersion').split(" ")[0],
            api_digest)
        url = url.replace(' ', '%20')
        response = urlopen(url).read().decode('utf-8')
        json_data = json.loads(response)
        message = json_data['reason']
        if json_data['status'] == 'error' and 'logged out' in json_data['reason']:
            xbmcgui.Dialog().ok('Invalid Box', message)
            xbmcaddon.Addon('plugin.video.yams').setSetting('username', '')
            xbmcaddon.Addon('plugin.video.yams').setSetting('username', '')
            xbmc.executebuiltin("XBMC.ActivateWindow(Home)")
        xbmc.log('Sent activity info for SID(%s). Sleeping for 120 second.' % xbmcaddon.Addon(
            'plugin.video.yams').getSetting("session"))
        for i in range(0, 120):
            time.sleep(1)
            importlib.reload(threading)
            if xbmc.Monitor().abortRequested():
                break


def run():
    scraper.__set_digest(digest)
    api_digest = scraper.digest

    try:
        ip = urllib.request.urlopen("https://astreamweb.com/kodi/ip.php").read().decode('utf-8')
    except Exception as e:
        dialog = xbmcgui.Dialog()
        dialog.notification('Connection Failure',
                            'Cannot connect to Astreamweb Services. Please ensure your internet is working or try again later.',
                            xbmcgui.NOTIFICATION_ERROR)
        xbmc.log('No response from https://astreamweb.com/kodi/ip.php')
        return

    username = xbmcaddon.Addon('plugin.video.yams').getSetting('username')
    password = xbmcaddon.Addon('plugin.video.yams').getSetting('password')
    authenticated, message, status_code = scraper.check_login(username, password,
                                                              xbmcaddon.Addon('plugin.video.yams').getSetting(
                                                                  'session'))
    if not authenticated:
        pass
    else:
        __settings__.setSetting("username", __settings__.getSetting("username"))
        activity_info = threading.Thread(target=app_active)
        activity_info.start()
        xbmcgui.Window(10000).setProperty('My_Service_Running', 'True')

        dialogtime = 0
        dialogbool = True
        iptime = 0
        ipbool = True
        subtime = 0
        subbool = True
        while not xbmc.Monitor().abortRequested():
            xbmc.log('Sent activity info for SID(%s). Sleeping for 120 seconds.' % xbmcaddon.Addon(
                'plugin.video.yams').getSetting("session"), level=xbmc.LOGINFO)

            try:
                if subbool:
                    subtime = 0
                    subbool = False
                    xbmc.log('subcheck for %s' % username)
                    import resources.modules.subscription_check as sub_check
                    username = __settings__.getSetting('username')
                    sub_check.setSubscriptionButton(username)
                if ipbool:
                    iptime = 0
                    ipbool = False
                    username = __settings__.getSetting("username")
                    scraper.__set_digest(digest)
                    data = scraper.__get_json({'task': 'check_multiple_ip', 'username': username})
                    if data["success"] == "True":
                        dialog.ok("Suspended",
                                  "Your account has been suspended due to sharing. Please contact support@yamsonline.com")
                        xbmc.executebuiltin("XBMC.ActivateWindow(Home)")
                if dialogbool:
                    dialogtime = 0
                    dialogbool = False
                    username = __settings__.getSetting("username")
                    data = scraper.__get_json({'task': 'getexpiredate', 'username': username})
                    xbmc.log('getexpiredate response: %s' % json.dumps(data), level=xbmc.LOGINFO)

                    import datetime
                    if data["recurring"] != "True":
                        today = datetime.date.today()
                        expiredate = data["expire_date"]
                        expiredates = expiredate.split("-")
                        expire = datetime.date(int(expiredates[0]), int(expiredates[1]), int(expiredates[2]))
                        days = expire - today
                        print((days.days))
                        print(expiredate)
                        if days.days <= 5:
                            user_id = ''
                            # Get user details and compare
                            dialog = xbmcgui.Dialog()
                            if dialog.yesno("AstreamWeb Subscription Notification",
                                            "Your AstreamWeb Subscription is due to expire in {0} days. Do you want to renew your account?".format(
                                                days.days), 'No Thanks', 'Subscribe Now'):
                                xbmc.executebuiltin(
                                    "ActivateWindow(Programs, plugin://plugin.video.yams/buy_subscription/{0})".format(
                                        user_id))

                xbmc.log('checking now...', level=xbmc.LOGINFO)
                feeds = []
                for url in RSS_URLS:
                    try:
                        feeds.append(feedparser.parse(url))
                    except:
                        traceback.print_exc()
                for feed in feeds:
                    for post in reversed(feed.entries):
                        print(post)
                        if not hasattr(post, 'published'):
                            xbmc.log('skip item - no published')
                            continue
                        if not hasattr(post, 'title'):
                            xbmc.log('skip item - no title')
                            continue
                        if not hasattr(post, 'summary'):
                            xbmc.log('skip item - no summary')
                            continue
                        if hasattr(post, 'user'):
                            if post.user.lower() != __settings__.getSetting("username").lower():
                                continue
                        if hasattr(post, 'package'):
                            if xbmc.getCondVisibility('!Skin.HasSetting(HomeMenuNo%sButton)' % post.package):
                                continue
                        date = post.published
                        import datetime
                        cur_time = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                        now = datetime.datetime.now()
                        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
                        orig_date = str(dt_string)
                        dt_string = datetime.datetime.strptime(orig_date, '%Y-%m-%d %H:%M:%S')
                        tdiff = dt_string - cur_time
                        hours = tdiff.days * 24
                        total_hours = hours + tdiff.seconds / 3600
                        xbmc.log("Difference is %d Hours" % (total_hours))
                        if total_hours < 24 and date not in get_shown_items():
                            add_shown_item(date)
                            msg = '\n'.join(['', date,
                                             '', ''.join(['[B]', post.title, '[/B]']),
                                             '', post.description])
                            show_msg(msg)
                    xbmc.log('will now sleep for: %d seconds' % CHECK_INTERVAL)
                    for i in range(0, CHECK_INTERVAL):
                        dialogtime += 1
                        if dialogtime >= DIALOG_INTERVAL:
                            dialogbool = True
                        iptime += 1
                        if iptime >= IP_INTERVAL:
                            ipbool = True
                        subtime += 1
                        if subtime >= SUBCHECK_INTERVAL:
                            subbool = True
                        print(("SUBCHECK TIME, %i, %i" % (subtime, SUBCHECK_INTERVAL)))
                        time.sleep(1)
                        if xbmc.Monitor().abortRequested():
                            break
            except:
                traceback.print_exc()
                if not __settings__.getSetting("username") or not __settings__.getSetting("password"):
                    if xbmcgui.Dialog().yesno('No Credentials',
                                    'Do you have an existing AstreamWeb Account?'):
                        __settings__.openSettings()


def get_feed(url):
    xbmc.log('Updating feed from url: %s' % url)
    return feedparser.parse(url)


def show_msg(msg):
    xbmc.log('show_msg start')
    nm = ASMessage('DialogAS.xml', ADDON_PATH, title=TITLE, message=msg)
    nm.doModal()
    del nm
    xbmc.log('show_msg ended')
    return


def get_shown_items():
    try:
        with open(FILE, mode='r') as f:
            items_already_shown = json.load(f)
    except IOError:
        if not os.path.isdir(PATH):
            os.makedirs(PATH)
        items_already_shown = []
    xbmc.log('get_shown_items: %s' % repr(items_already_shown))
    return items_already_shown


def add_shown_item(item):
    items_already_shown = get_shown_items()
    xbmc.log('add_shown_item adding: %s' % repr(item))
    items_already_shown.append(item)
    with open(FILE, mode='w') as f:
        json.dump(items_already_shown, f.encode(), indent=1)


def log(text):
    xbmc.log('AstreamWeb msg: %s' % text)


if __name__ == "__main__":
    xbmc.log('service started')
    run()
    xbmc.log('service exited')
