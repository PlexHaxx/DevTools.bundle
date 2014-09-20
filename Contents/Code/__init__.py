####################################################################################################
#	This plugin will assist for 3.Party developers in location the library
#
# Install it as a regular channel, and afterwards, browse to
#
# http://qnap2:32400/:/plugins/com.plexapp.plugins.DevTools/prefs
#
#	Made by 
#	dane22....A Plex Community member
#
####################################################################################################

import urllib

VERSION = ' V0.0.0.1'
NAME = 'DevTools'
PREFIX = '/hidden/DevTools'


####################################################################################################
# Start function
####################################################################################################
def Start():
#	print("********  Started %s on %s  **********" %(NAME  + VERSION, Platform.OS))
	Log.Debug("*******  Started %s on %s  ***********" %(NAME  + VERSION, Platform.OS))
	HTTP.CacheTime = 0
	myURL = 'http://127.0.0.1:32400/:/plugins/com.plexapp.plugins.DevTools/prefs/set?Home='
	Log.Debug('Found location as : %s' %(urllib.quote(Core.app_support_path)))
	HTTP.Request(myURL + urllib.quote(Core.app_support_path), immediate=True)	

class PlexDevToolsAgent():
  name = 'DevTools'
