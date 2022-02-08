import os
import xbmc
import xbmcaddon
import xbmcvfs
import xbmcgui
import traceback
from resources.modules import plugintools
import random
import string

def boxname(params=None):
    if xbmc.getCondVisibility("System.Platform.Android") == 1:
        boxnamePath = os.path.join(xbmcvfs.translatePath(os.path.join('/storage/emulated/0/DCIM/Android_0/', '')),
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
            xbmcaddon.Addon('plugin.video.yams').setSetting('devicename', currentUUID)
        except:
            print('>>> traceback starts >>>')
            traceback.print_exc()
            print('<<< traceback end <<<')
    else:
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(4))
        print("Random string of length", result_str, "is:", result_str)
        #input_boxname = xbmcgui.Dialog().input('Where is this box located? (e.g. Living Room)', ' %s' % (result_str))
        plugintools.set_setting('devicename', result_str)
        currentUUID = result_str
        xbmcaddon.Addon('plugin.video.yams').setSetting('devicename', currentUUID)
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
