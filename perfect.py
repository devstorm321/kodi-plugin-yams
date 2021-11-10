from distutils.version import LooseVersion
import urllib.request, urllib.error, urllib.parse, urllib.request, urllib.parse, urllib.error
import time
import xbmc, xbmcgui,xbmcaddon, xbmcvfs

import os, re

APK_URL = "http://www.indiangilma.com/rss/PerfectPlayer.apk"
VERSION_URL = "https://astreamweb.com/kodi/astream_version.txt"
ADDON_NAME = "AStreamweb"
PATH = xbmcaddon.Addon().getAddonInfo('path')
ICON = xbmcvfs.translatePath(os.path.join(PATH, 'icon.png'))
ADDON = xbmcvfs.translatePath(os.path.join(PATH, 'addon.xml'))


def availableUpdate():
    osVersion = xbmc.getInfoLabel('System.OSVersionInfo')
    print(("[updater] OS Version {0}".format(osVersion)))
    try:
        buildVersion = xbmcaddon.Addon('service.xbmc.versioncheck').getAddonInfo('version')
    except:
        return True
    print(("[updater] Current build version: {0}".format(buildVersion)))
    buildVersion = LooseVersion(buildVersion)
    try:
        availVersion = urllib.request.urlopen(VERSION_URL).read()
        availVersion = LooseVersion(availVersion)
        return buildVersion < availVersion
    except:
        return False

    return False

def upgrade_astreamweb(path):
    if not xbmcgui.Dialog().yesno("Updater", "This Updater works only with Fire TV and Android devices, proceed?", nolabel="No", yeslabel="Yes"): return False
    if xbmcvfs.exists(path): xbmcvfs.delete(path)
    if downloadAPK(APK_URL, path):
        installAPK(path)
    else:
        xbmcgui.Dialog().ok("Updater", "Installation failed, check log files.")



def downloadAPK(url, dest):
    start_time = time.time()
    dia = xbmcgui.DialogProgress()
    dia.create("Updater", "Downloading update..")
    dia.update(0)
    try:
        urllib.request.urlretrieve(url.rstrip('/'), dest, lambda nb, bs, fs: pbhook(nb, bs, fs, dia, start_time))
    except Exception as e:
        dia.close()
        xbmcgui.Dialog().notification(ADDON_NAME, __language__(30001), ICON, 4000)
        xbmc.log("downloadAPK, Failed! (%s) %s"%(url,str(e)), xbmc.LOGERROR)
        xbmcvfs.delete(PATH)
        return False
    return True


def pbhook(numblocks, blocksize, filesize, dia, start_time):
    try:
        percent = min(numblocks * blocksize * 100 / filesize, 100)
        currently_downloaded = float(numblocks) * blocksize / (1024 * 1024)
        kbps_speed = numblocks * blocksize / (time.time() - start_time)
        if kbps_speed > 0: eta = (filesize - numblocks * blocksize) / kbps_speed
        else: eta = 0
        kbps_speed = kbps_speed / 1024
        total = float(filesize) / (1024 * 1024)
        mbs = '%.02f MB of %.02f MB' % (currently_downloaded, total)
        e = 'Speed: %.02f Kb/s ' % kbps_speed
        e += 'ETA: %02d:%02d' % divmod(eta, 60)
        dia.update(percent, mbs, e)
    except Exception('Download Failed'):
        percent = 100
        dia.update(percent)
    if dia.iscanceled(): raise Exception('Download Canceled')


def installAPK(apkfile):
    xbmc.executebuiltin('StartAndroidActivity("","android.intent.action.VIEW","application/vnd.android.package-archive","file:'+apkfile+'")')


AddonID = 'plugin.video.yams'

__settings__=xbmcaddon.Addon(id=AddonID)
__language__=__settings__.getLocalizedString
