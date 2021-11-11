import sys, json, urllib.request, urllib.error, urllib.parse, urllib.request, urllib.parse, urllib.error, xbmcgui, xbmcplugin
addonHandle   = int(sys.argv[1])
baseUrl       = sys.argv[0]

def addDirectory(name, image, build_url, is_folder=True):
    li = xbmcgui.ListItem(name)
    li.setArt({'thumb':str(image)})
    li.setProperty('IsPlayable', 'True')
    xbmcplugin.addDirectoryItem(handle=addonHandle, url=build_url, listitem=li, isFolder = is_folder)

def buildUrl(query):
    return baseUrl + '?' + urllib.parse.urlencode(query)


def vijayVOD(url, mode, isDirectory):
    print('log: vijayVOD special started')
    try:
        response = urllib.request.urlopen(url)
        html = response.read()
    except urllib.error.HTTPError as e:
        html = e.fp.read()
        pass

    if isDirectory == 'False':
        item = xbmcgui.ListItem(path=html)
        item.setProperty('IsPlayable', 'True')
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), succeeded=True, listitem=item)
    else:
        items = json.loads(html)
        for item in items:
            dirBuildUrl = buildUrl({"mode" : "vijayVOD", "url" : item['url'], "isDirectory" : item['isDirectory']})
            addDirectory(item['title'], item['imageUrl'], dirBuildUrl, item['isDirectory'])

        xbmcplugin.endOfDirectory(addonHandle)
