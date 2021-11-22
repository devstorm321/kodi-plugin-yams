#!/usr/bin/env python

# source: https://github.com/sanderjo/fast.com

import fast
import xbmcgui
import sys

result = fast.fast_com()
xbmcgui.Dialog().ok("[COLOR white]FAST.com[/COLOR]", "[COLOR white]Result: %s Mbps" % result + '[/COLOR]')
sys.modules.clear()
