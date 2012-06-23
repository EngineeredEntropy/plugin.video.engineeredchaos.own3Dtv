#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys, re
import urllib, urllib2
from xml.dom.minidom import parse, parseString
import xbmcplugin, xbmcgui, xbmcaddon


LISTLIVEVIDEOS = 1
PLAYVIDEO = 2
SUBSCRIPTIONS = 3
LISTGAMES = 4
SHOWSTARCRAFT = 5
SHOWDIABLO = 6
SHOWLOL = 7
SHOWDOTA = 8
SHOWCOUNTER = 9
SHOWWOW = 10
SEARCHLIVE = 11
LISTFAVORITES = 12


LIVETYPE = 1
VODTYPE = 2
OFFLINE = 3
CHECKLIVE = 4
OTHER = 5

LIVEURL="http://www.own3d.tv/live"

STARCRAFTURL="http://www.own3d.tv/game/StarCraft+II"
DIABLOURL="http://www.own3d.tv/game/Diablo+3"
LOLURL="http://www.own3d.tv/game/League+of+Legends"
DOTAURL="http://www.own3d.tv/game/Dota+2"
COUNTERURL="http://www.own3d.tv/game/Counter-Strike"
WOWURL="http://www.own3d.tv/game/World+of+Warcraft"

STARCRAFTTHUMB="http://img.own3d.tv/games/42_4d8a6a28840e9_spotlight_logo.png"
DIABLOTHUMB="http://img.own3d.tv/games/98_4fc4a927c279b_spotlight_logo.png"
LOLTHUMB="http://img.own3d.tv/games/163_4eebcce777ab3_spotlight_logo.png"
DOTATHUMB="http://img.own3d.tv/games/605_4eac18df843be_spotlight_logo.png"
COUNTERTHUMB="http://img.own3d.tv/games/4_4e2083c85e54f_spotlight_logo.png"
WOWTHUMB="http://img.own3d.tv/games/20_4d8a69680ccf7_spotlight_logo.png"


 
CDN1= 'rtmp://fml.2010.edgecastcdn.net:1935/202010'
CDN2= ''
SWF='http://static.ec.own3d.tv/player/Own3dPlayerV2_86.swf'

#Collects stream ID, stream name, game name, stream cover, and stream thumbnail
LIVEREGEX='<img class="VIDEOS-thumbnail small_tn_img originalTN".+rel="(\d+)"\ssrc="(.+)"\salt="(.+)".+\s.+src="(.+)"\salt='                                                         #Stream ID   #Stream Name    
LIVEREGEXFALLBACK='<img class="VIDEOS-thumbnail small_tn_img originalTN".+rel="(\d+)"\ssrc="(.+)"\salt="(.+)"'                                                         #Stream ID   #Stream Name


class Channel:
    def __init__(self,streamID,type):
        self.streamID=streamID
        self.type=type
       
        self.activeCDN=0
        self.activeStream=0
        self.rtmpBase=None
        self.rtmpPath=None
        
        self.playbackURL=None
        self.rtmpURL=None
        self.pageURL=None
        self.swfURL=None
        self.playPath=None
        self.live=None
        self.verify=None
        
        self.channel=None
        self.title=None
        self.user=None
        self.game=None
        self.thumbnail=None
        self.cdnList=[]
        self.streamList=[]
    
    def playStream(self):
        listItem = xbmcgui.ListItem("Stream",thumbnailImage=self.thumbnail)
        listItem.setInfo( type="Video", infoLabels={"Title": self.title, "Plot": self.user} )
        xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(self.playbackURL,listItem)
        
    def loadInfo(self):
        #Load and parse own3d info page
        infoURL="http://www.own3d.tv/livecfg/"+str(self.streamID)
        try:
            infoPage=urllib.urlopen(infoURL)
        except:
            xbmc.executebuiltin("XBMC.Notification(own3D.tv,Error Loading Stream,5000,"+ICON+")")
            print "Error loading stream. Check your internet connection"
            return 1
        self.infoDOM=parse(infoPage)
        self.channel=self.infoDOM.getElementsByTagName("channel")[0]
        
        if settings.getSetting('hdVideo') == 'true':
            self.activeStream=0
        else:
            self.activeStream=1
        
        #Parse Channel title,user,game,etc
        self.title=self.channel.attributes["name"].value
        self.user=self.channel.attributes["owner"].value
        self.game=self.channel.attributes["description"].value
        if self.infoDOM.getElementsByTagName("thumb")[0].firstChild == None:
            print ICON
            xbmc.executebuiltin("XBMC.Notification(own3D.tv,Error Loading Stream,5000,"+ICON+")")
            return 1
        self.thumbnail=str(self.infoDOM.getElementsByTagName("thumb")[0].firstChild.data)

        if '?' in self.thumbnail:
            self.thumbnail="icon.png"
        print "Thumbnail: "+self.thumbnail
        #load CDN's and Streams
        self.cdnList=self.channel.getElementsByTagName("item")
        cdn=len(self.cdnList)-1
        
        while cdn>=0:
            self.rtmpBase=self.cdnList[cdn].attributes["base"].value
            if self.rtmpBase == '${cdn1}':
                self.activeCDN=cdn
                break
                
        if(self.rtmpBase == "${cdn1}"):
            self.rtmpBase = CDN1
        else:
            print "CDN Not Recognized! Aborting."
            return 1
        #self.rtmpBase=self.cdnList[sel f.activeCDN].attributes["base"].value
        self.streamList=self.cdnList[self.activeCDN].getElementsByTagName("stream")
        self.rtmpPath=self.streamList[self.activeStream].attributes["name"].value
        
        #Generate playback URL
        
        #determine CDN

        #elif self.rtmpBase == '${cdn2}':
        #    self.rtmpBase = CDN2
        #else:

        
        #rtmpURL
        if '?' in self.rtmpPath:
            self.rtmpURL=self.rtmpBase+'?'+self.rtmpPath.split('?',1)[1]
        else:
            self.rtmpURL=self.rtmpBase+'?'+self.rtmpPath
        
        #pageURL
        self.pageURL=self.channel.attributes["ownerLink"].value
        
        #playPath
        self.playPath=self.rtmpPath
        
        #Live and verify
        self.live='True'
        self.verify='True'
        
        self.playbackURL=self.rtmpURL+" pageUrl="+self.pageURL+" Playpath="+self.playPath+" swfUrl="+SWF+" swfVfy="+self.verify+" Live="+self.live
        #print "rtmpURL: "+self.rtmpURL
        #print "pageURL: "+self.pageURL
        #print "playPath: "+self.playPath
        #print "playbackURL: "+self.playbackURL
        print "Loading Stream--------------------------------------------"
        print "Title: "+self.title
        print "User: "+self.user
        print "Game: "+self.game
        print "Playback URL: "+self.playbackURL
        
def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param

def loadInfo(streamID):
        #Load and parse own3d info page
        infoURL="http://www.own3d.tv/livecfg/"+str(streamID)
        infoPage=urllib.urlopen(infoURL)
        infoDOM=parse(infoPage)
        channel=infoDOM.getElementsByTagName("channel")[0]
        
        if infoDOM.getElementsByTagName("thumb")[0].firstChild == None:
            return 1
        else:
            return 0
        
def loadLive(url):
    try:
        pageContents=loadPage(url)
    except:
        print "Error loading page. Are you connected to the internet?"
        xbmc.executebuiltin("XBMC.Notification(own3D.tv,Error Locating Streams,5000,"+ICON+")")
        return None
    
    a=re.compile(LIVEREGEX)
    match=a.findall(pageContents)
    return match   
        
def loadPage(url):
    page=urllib.urlopen(url)
    pageContents=page.read()
    page.close()
    return pageContents

def displayVideos(videos, videoType):
    if videos != None:
        for streamID, thumbnail, name, preview in videos:
            addVideoLink(streamID,thumbnail,name,preview,videoType)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
    
def checkLive(streamID):
    print "Checking if "+str(streamID)+" is live."
    liveURL="http://api.own3d.tv/liveCheck.php?live_id="+str(streamID)
    try:
        livePage=urllib.urlopen(liveURL)
    except:
        print "Error checking if "+str(streamID)+" is live."
        return OTHER
    liveDOM=parse(livePage)
    live=liveDOM.getElementsByTagName("liveEvent")[0]
    print "Checking if Live."
    print live.getElementsByTagName("isLive")[0].firstChild.data
    if live.getElementsByTagName("isLive")[0].firstChild.data == "true":
        return LIVETYPE
    else:
        return OFFLINE
#    if loadInfo(streamID) == 1:
#        return OFFLINE
#    else:
#        return LIVETYPE
    
def checkLiveOld(streamID):
    url="http://www.own3d.tv/livecfg/"+streamID
    pageContents=loadPage(url)
    a=re.compile("ownerLink=\"(.+)\">")
    match=a.findall(pageContents)
    print match
    if len(match)!=0:
        pageContents=loadPage(match[0])
        if "<span class=\"cGray9 fntN\">LIVE&nbsp;</span>" in pageContents:
            print streamID+" is Live!"
            return LIVETYPE
    print streamID+" is not live."
    return OFFLINE

def searchLive(searchString):
    print "Searching: "+"http://www.own3d.tv/livestreams/?search="+searchString.replace(" ","+")+"&type=live"
    results=loadLive("http://www.own3d.tv/livestreams/?search="+searchString.replace(" ","+")+"&type=live")
    displayVideos(results, LIVETYPE)
    
def addMenuItem(name,mode,iconimage):
    url=sys.argv[0]+"?mode="+str(mode)#+"&name="+urllib.quote_plus(name)
    ok=True
    listItem=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    listItem.setInfo( type="Video", infoLabels={ "Title": name } )
    ok=xbmcplugin.addDirectoryItem(int(sys.argv[1]),url,listItem,True)
    return ok
def addVideoLink(streamID, thumbnail, name, preview, videoType):
#    if videoType == LIVETYPE:
#        if checkLive(streamID) == 0:
#            videoType=OFFLINE
    url=sys.argv[0]+"?mode="+urllib.quote_plus(str(PLAYVIDEO))+"&streamID="+urllib.quote_plus(str(streamID))+"&name="+urllib.quote_plus(name)+"&videoType="+urllib.quote_plus(str(videoType))
    
    if videoType == CHECKLIVE:
        videoType = checkLive(streamID)
    if videoType == LIVETYPE:
        listItem=xbmcgui.ListItem("[Live] "+name, iconImage="DefaultVideo.png", thumbnailImage=thumbnail)
    elif videoType == OFFLINE:
        listItem=xbmcgui.ListItem("[Offline] "+name, iconImage="DefaultVideo.png", thumbnailImage=thumbnail)
    else:
        listItem=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=thumbnail)
    ok=True
    
    if mode == LISTFAVORITES:
        title = ("Remove "+name+" from favorites." )                
        browse =  "XBMC.Container.Refresh("+str(sys.argv[0])+str(sys.argv[2])+"&favorite=2"+"&streamID="+urllib.quote_plus(str(streamID))+"&name="+urllib.quote_plus(str(name))+"&thumbnail="+urllib.quote_plus(str(thumbnail))+"&preview="+urllib.quote_plus(str(preview))+")"
    else:
        title = ("Add "+name+" to favorites." )                
        browse =  "XBMC.Container.Refresh("+str(sys.argv[0])+str(sys.argv[2])+"&favorite=1"+"&streamID="+urllib.quote_plus(str(streamID))+"&name="+urllib.quote_plus(str(name))+"&thumbnail="+urllib.quote_plus(str(thumbnail))+"&preview="+urllib.quote_plus(str(preview))+")"
    print "Context url: "+browse
    cm=[]
    cm.append((title, browse  ))
    listItem.addContextMenuItems( cm, replaceItems=False )
    ok=xbmcplugin.addDirectoryItem(int(sys.argv[1]),url,listItem)
    return ok
def loadMenu():
    addMenuItem("Live Streams",LISTLIVEVIDEOS,'')
    addMenuItem("Games",LISTGAMES,'')
    addMenuItem("Search Live",SEARCHLIVE,'')
    addMenuItem("Favorites",LISTFAVORITES,'')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def loadGames():
    addMenuItem("Starcraft 2",SHOWSTARCRAFT,STARCRAFTTHUMB)
    addMenuItem("Diablo III",SHOWDIABLO,DIABLOTHUMB)
    addMenuItem("League of Legends",SHOWLOL,LOLTHUMB)
    addMenuItem("Dota 2",SHOWDOTA,DOTATHUMB)
    addMenuItem("Counter-Strike",SHOWCOUNTER,COUNTERTHUMB)
    addMenuItem("World of Warcraft",SHOWWOW,WOWTHUMB)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    
def loadFavorites(favorites):
    print "Favorites: "
    print favorites
    #if refresh == 1 and settings.getSetting('checkLive') =="true":
    if settings.getSetting('checkLive') =="true":
        displayVideos(favorites,CHECKLIVE)
    else:
        displayVideos(favorites,OTHER)
        
        
parameters=get_params()
mode=None
streamID=None
activeStream=None
videoType=None
thumbnail=None
name=None
favorite=None
preview=None
favorites=[]
settings = xbmcaddon.Addon("plugin.video.engineeredchaos.own3Dtv")

ICON = xbmc.translatePath( os.path.join( settings.getAddonInfo('path'), 'icon.png' ) )

#favoriteString=settings.getSetting("favorites")
#favoriteSplit=""
#favorites=[]#None#favoriteString.split('&&&')
#if "&&&" in favoriteString:
#    favoritesSplit=favoriteString.split('&&&')
#print "FavoriteSplit: "+favoriteSplit
print "Parameters: " + str(parameters)

try:
    favorite=int(parameters["favorite"])
except:
    pass

try:
    streamIDAdd=int(parameters["streamID"])
except:
    pass

try:
    nameAdd=urllib.unquote_plus(parameters["name"])
except:
    pass

try:
    thumbnailAdd=urllib.unquote_plus(parameters["thumbnail"])
except:
    pass

try:
    previewAdd=urllib.unquote_plus(parameters["preview"])
except:
    pass

#refresh=1
favoriteString= settings.getSetting("favorites")
favoriteSplit= favoriteString.split("&&&")
print "Favorites Loaded: "
print favoriteString
#favorites=[]
favoriteSplit3=[]
print "FavoriteSplit: "
print favoriteSplit
for favoriteSplit2 in favoriteSplit:
    favoriteSplit3.append(favoriteSplit2.split("###"))
print "FavoriteSplit3"
print favoriteSplit3

tempFavorites=[]
for favoriteItem in favoriteSplit3:
    if len(favoriteItem)==4:
        tempFavorites.append(favoriteItem)
for streamID,thumbnail,name,preview in tempFavorites:
    favorites.append([streamID,thumbnail,name,preview])
    
#favorites=[]
if favorite == 1:
    print "Adding "+nameAdd+" to favorites."
    alreadyAdded=0
    favoriteString="";
    
    ##favorites.append([streamID,thumbnail,name,preview])
    print streamIDAdd
    print thumbnailAdd
    print nameAdd
    print previewAdd
    print favorites
    for streamID,thumbnail,name,preview in favorites:
        if nameAdd in name:
            alreadyAdded=1
        favoriteString=favoriteString+str(streamID)+"###"+str(thumbnail)+"###"+str(name)+"###"+str(preview)+"&&&"
        
    if alreadyAdded==0:
        favoriteString=favoriteString+str(streamIDAdd)+"###"+str(thumbnailAdd)+"###"+str(nameAdd)+"###"+str(previewAdd)
        favorites.append([streamIDAdd,thumbnailAdd,nameAdd,previewAdd])
    else:
        print nameAdd+" is already in favorites."
    settings.setSetting("favorites",favoriteString)
    print "Saving Favorites: "
    print favoriteString


if favorite ==2:
    #refresh=0
    newFavorites=[]
    favoriteString="";
    print "Removing "+nameAdd+" from favorites."
    for streamID,thumbnail,name,preiview in favorites:
        if name in nameAdd:
            print "Match Found...Removing."
        else:
            newFavorites.append([streamID,thumbnail,name,preview])
            favoriteString=favoriteString+str(streamID)+"###"+str(thumbnail)+"###"+str(name)+"###"+str(preview)+"&&&"
    print "Updating Favorites: "
    print favoriteString
    settings.setSetting("favorites",favoriteString)
    #mode=LISTFAVORITES
    favorites=newFavorites





try:
    mode=int(parameters["mode"])
except:
    pass

try:
    streamID=int(parameters["streamID"])
except:
    pass

try:
    videoType=int(parameters["type"])
except:
    pass

try:
    name=parameters["name"]
except:
    pass

try:
    thumbnail=parameters["thumbnail"]
except:
    pass

try:
    preview=parameters["preview"]
except:
    pass




#if len(favoriteSplit)>0:
   # for streamID,thumbnail,name,preview in favoriteSplit.split("###")
    #    favo
if mode == None:
    loadMenu()
elif mode == LISTLIVEVIDEOS:
    displayVideos(loadLive(LIVEURL),LIVETYPE)
elif mode == LISTGAMES:
    loadGames()
elif mode == LISTFAVORITES:
    loadFavorites(favorites)
elif mode == SHOWSTARCRAFT:
    displayVideos(loadLive(STARCRAFTURL),LIVETYPE)
elif mode == SHOWDIABLO:
    displayVideos(loadLive(DIABLOURL),LIVETYPE)
elif mode == SHOWLOL:
    displayVideos(loadLive(LOLURL),LIVETYPE)
elif mode == SHOWDOTA:
    displayVideos(loadLive(DOTAURL),LIVETYPE)
elif mode == SHOWCOUNTER:
    displayVideos(loadLive(COUNTERURL),LIVETYPE)
elif mode == SHOWWOW:
    displayVideos(loadLive(WOWURL),LIVETYPE)
elif mode == SEARCHLIVE:
    keyboard = xbmc.Keyboard('')
    keyboard.doModal()
    if (keyboard.isConfirmed()):
        searchLive(keyboard.getText())
elif mode == PLAYVIDEO:
    print "Loading StreamID: "+str(streamID)
    if streamID != None:
        activeStream=Channel(streamID,videoType)
        if activeStream.loadInfo() != 1:
            activeStream.playStream()
    


