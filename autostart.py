# -*- coding: utf-8 -*-
"""
Spyder Editor

This temporary script file is located here:
D:\00-Costin\Python\WinPython-64bit-2.7.6.4\settings\.spyder2\.temp.py
"""
import xbmc, xbmcaddon, xbmcgui

xbmc.executebuiltin("UpdateAddonRepos")

xbmc.executebuiltin("UpdateLocalAddons")

autostart = xbmcaddon.Addon(id='plugin.video.yams').getSetting("autostart")

if autostart == 'true':
    autostart = True
    xbmc.executebuiltin("ActivateWindow(Videos,plugin://plugin.video.yams)")
else:
    autostart = False
