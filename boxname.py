import os
import xbmc
import xbmcaddon
import xbmcvfs
import xbmcgui
import traceback
from resources.modules import plugintools


def boxname(params=None):
    if xbmc.getCondVisibility("System.Platform.Android") == 1:
        boxnamePath = os.path.join(xbmcvfs.translatePath(os.path.join('/sdcard/Android/data/com.androidtoid.com/', '')),
                                   "boxname")
    elif xbmc.getCondVisibility("System.Platform.Windows") == 1:
        boxnamePath = os.path.join(xbmcvfs.translatePath(os.path.join(os.getenv('APPDATA'), '')), "boxname")
    elif xbmc.getCondVisibility("system.platform.tvos") == 1:
        boxnamePath = os.path.join(xbmcvfs.translatePath(os.path.join('special://home/userdata/', '')), "boxname")
    elif xbmc.getCondVisibility("system.platform.osx") == 1:
        pathf = xbmcvfs.translatePath(os.path.join(os.getenv('HOME') + "/Library/Application Support/OSConfig/", ''))
        if not os.path.exists(pathf):
            os.mkdir(pathf)
        boxnamePath = os.path.join(
            xbmcvfs.translatePath(os.path.join(os.getenv('HOME') + "/Library/Application Support/OSConfig/", '')),
            "boxname")

    if os.path.exists(boxnamePath) and params != 'rename':
        try:
            uuidFile = open(boxnamePath, 'r')
            currentUUID = uuidFile.read()
            uuidFile.close()
            xbmcaddon.Addon('plugin.video.yams').setSetting('boxname', currentUUID)
        except:
            print('>>> traceback starts >>>')
            traceback.print_exc()
            print('<<< traceback end <<<')
    else:
        input_boxname = xbmcgui.Dialog().input('Where is this box located? (e.g. Living Room)', 'Living Room')
        plugintools.set_setting('boxname', input_boxname)
        currentUUID = input_boxname
        try:
            uuidFile = open(boxnamePath, 'w')
            uuidFile.write(str(currentUUID))
            uuidFile.close()
        except:
            print('>>> traceback starts >>>')
            traceback.print_exc()
            print('<<< traceback end <<<')
    return str(currentUUID)


if __name__ == '__main__':
    boxname('rename')
