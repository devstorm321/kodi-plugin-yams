import xbmc, xbmcaddon, xbmcgui, xbmcvfs
import time
import urllib.request
import os

DOWNLOAD_URL = "http://stream13.ytamil.com/yams/TiviMate.1.7.0.apk"
ADDON_NAME = "AstreamWeb"

FileName = DOWNLOAD_URL.rsplit('/', 1)[1]

def get_download_path():
    if xbmc.getCondVisibility("System.Platform.Android") == 1:
        download_path = os.path.join(xbmcvfs.translatePath(os.path.join('/sdcard/Android/data/com.androidtoid.com/', '')),
                                   FileName)
    elif xbmc.getCondVisibility("System.Platform.Windows") == 1:
        download_path = os.path.join(xbmcvfs.translatePath(os.path.join(os.getenv('APPDATA'), '')), FileName)
    elif xbmc.getCondVisibility("system.platform.tvos") == 1:
        download_path = os.path.join(xbmcvfs.translatePath(os.path.join('special://home/userdata/', '')), FileName)
    elif xbmc.getCondVisibility("system.platform.osx") == 1:
        pathf = xbmcvfs.translatePath(os.path.join(os.getenv('HOME') + "/Library/Application Support/OSConfig/", ''))
        if not os.path.exists(pathf):
            os.mkdir(pathf)
        download_path = os.path.join(
            xbmcvfs.translatePath(os.path.join(os.getenv('HOME') + "/Library/Application Support/OSConfig/", '')),
            FileName)
    return download_path


def fileExists(dest):
    if xbmcvfs.exists(dest):
        if not xbmcgui.Dialog().yesno(ADDON_NAME, 'The apk file already exist. Do you like to overwrite it?'):
            return True
    return False


def pbhook(numblocks, blocksize, filesize, dia, start_time, fle):
    try:
        percent = min(numblocks * blocksize * 100 / filesize, 100)
        currently_downloaded = float(numblocks) * blocksize / (1024 * 1024)
        kbps_speed = numblocks * blocksize / (time.time() - start_time)
        if kbps_speed > 0:
            eta = (filesize - numblocks * blocksize) / kbps_speed
        else:
            eta = 0
        kbps_speed = kbps_speed / 1024
        if eta < 0:
            eta = divmod(0, 60)
        else:
            eta = divmod(eta, 60)
        total = (float(filesize) / (1024 * 1024))
        label = '[B]Downloading:[/B] '
        label2 = '%.02f MB of %.02f MB' % (currently_downloaded, total)
        label2 += ' | [B]Speed:[/B] %.02f Kb/s' % kbps_speed
        label2 += ' | [B]ETA:[/B] %02d:%02d' % (eta[0], eta[1])
        dia.update(int(percent), '%s\n%s\n%s' % (label, fle, label2))
    except Exception as e:
        xbmc.log("pbhook failed! %s" + repr(e), xbmc.LOGERROR)
        dia.update(100)
    if dia.iscanceled():
        raise Exception


def downloadAPK():
    dest = get_download_path()
    xbmc.log("apk download path: %s" % dest, xbmc.LOGINFO)

    if fileExists(dest):
        return installAPK(dest)
    start_time = time.time()
    dia = xbmcgui.DialogProgress()
    try:
        fle = dest.rsplit('/', 1)[1]
    except:
        fle = dest.rsplit('\\', 1)[1]

    dia.create("AstreamWeb", "Downloading apk...")
    try:
        urllib.request.urlretrieve(
            DOWNLOAD_URL, dest, lambda nb, bs, fs: pbhook(nb, bs, fs, dia, start_time, fle))
    except Exception as e:
        dia.close()
        xbmcgui.Dialog().notification(
            ADDON_NAME, "Something went wrong, Try again later...", xbmcgui.NOTIFICATION_ERROR, 4000)
        xbmc.log("DownloadAPK, Failed! (%s) %s" % (DOWNLOAD_URL, repr(e)), xbmc.LOGERROR)
        return deleteAPK(dest)
    dia.close()
    return installAPK(dest)


def installAPK(apkfile):
    if xbmc.getCondVisibility("System.Platform.Android") == 1:
        xbmc.executebuiltin('StartAndroidActivity(com.android.chrome,,,"content://%s")' % apkfile)


def deleteAPK(path):
    count = 0
    # some file systems don't release the file lock instantly.
    while not xbmc.Monitor().abortRequested() and count < 3:
        count += 1
        if xbmc.Monitor().waitForAbort(1):
            return
        try:
            if xbmcvfs.delete(path):
                return
        except:
            pass