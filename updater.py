from distutils.version import LooseVersion
import time,os
import urllib2, urllib
import xbmc, xbmcgui,xbmcaddon, xbmcvfs
AddonID = 'plugin.video.yams'
addonPath=xbmcaddon.Addon(id=AddonID).getAddonInfo('path'); addonPath=xbmc.translatePath(addonPath);
xbmcPath=os.path.join(addonPath,"..",".."); xbmcPath=os.path.abspath(xbmcPath)




APK_URL = "http://plugin.astreamweb.com/AstreamWeb-Play.apk"
VERSION_URL = "https://astreamweb.com/kodi/astream_version.txt"

def availableUpdate():
	osVersion = xbmc.getInfoLabel('System.OSVersionInfo')
	print("[updater] OS Version {0}".format(osVersion))
	try:
		buildVersion = xbmcaddon.Addon('service.xbmc.versioncheck').getAddonInfo('version')
	except:
		return True
	print("[updater] Current build version: {0}".format(buildVersion))
	buildVersion = LooseVersion(buildVersion)
	try:
		availVersion = urllib2.urlopen(VERSION_URL).read()
		availVersion = LooseVersion(availVersion)
		return buildVersion < availVersion
	except:
		return False

	return False

def upgrade_astreamweb(path):
	if not xbmcgui.Dialog().yesno("Updater", "This Updater works only with Fire TV and Android devices, proceed?", nolabel="No", yeslabel="Yes"): return False
#	if xbmcvfs.exists(path): xbmcvfs.delete(path)
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
		urllib.urlretrieve(url.rstrip('/'), dest, lambda nb, bs, fs: pbhook(nb, bs, fs, dia, start_time))
	except Exception as e:
		dia.close()
		xbmcgui.Dialog().notification(ADDON_NAME, LANGUAGE(30001), ICON, 4000)
		log("downloadAPK, Failed! (%s) %s"%(url,str(e)), xbmc.LOGERROR)
		xbmcvfs.delete(path); return False
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

def fresh_starty():
    try:
        for root, dirs, files in os.walk(xbmcPath,topdown=False):
            for name in files:
                try:
                    if name not in ["tmp.apk","updater.py"]: os.remove(os.path.join(root,name))
                except:
                    if name not in ["Addons15.db","MyVideos75.db","Textures13.db","xbmc.log","tmp.apk","updater.py"]: failed=True
            for name in dirs:
                try: os.rmdir(os.path.join(root,name))
                except:
                    if name not in ["Database","userdata","addons","plugin.video.yams"]: failed=True
        if failed:
            dialog = xbmcgui.Dialog()
            dialog.ok("Astreamweb", "User data successfully deleted")
        else:
            dialog = xbmcgui.Dialog()
            dialog.ok("Astreamweb", "User data successfully deleted")
    except:
        dialog = xbmcgui.Dialog()
        dialog.ok("Astreamweb", "Deleting user data failed")
    xbmc.executebuiltin('Skin.ResetSettings')

def fresh_start():
    xbmc.log("freshstart.main_list xbmcPath="+xbmcPath)
    failed=False
    try:
        for root, dirs, files in os.walk(xbmcPath,topdown=False):
            for name in files:
                try:
                    if name not in ["tmp.apk","updater.py"]: os.remove(os.path.join(root,name))
                except:
                    if name not in ["Addons15.db","MyVideos75.db","Textures13.db","xbmc.log"]: failed=True
            for name in dirs:
                try: os.rmdir(os.path.join(root,name))
                except:
                    if name not in ["Database","userdata"]: failed=True
        if failed:
            dialog = xbmcgui.Dialog()
            dialog.ok("Astreamweb", "Deleting user data failed")
        else:
            dialog = xbmcgui.Dialog()
            dialog.ok("Astreamweb", "User data successfully deleted")
    except:
        dialog = xbmcgui.Dialog()
        dialog.ok("Astreamweb", "Deleting user data failed")
    xbmc.executebuiltin('Skin.ResetSettings')

def installAPK(apkfile):
	#import resources.modules.fresh_start as fresh_start
#	fresh_start()#fresh_start.fresh_start()
	xbmc.executebuiltin('StartAndroidActivity("","android.intent.action.VIEW","application/vnd.android.package-archive","file:'+apkfile+'")')
