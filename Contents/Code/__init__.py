####################################################################################################
#	This plugin will assist for 3.Party developers running apps not on the PMS
# to access it's filesystem if needed
#
# Currently limited functions are avail, but do request, and I'll see what I can do
#
# Install it as a regular channel, and afterwards, from PMS, open the channel
# settings, and enter a secret password, that can be shared between a 3.Party
# utillity and this plug-in
#
#	Made by 
#	dane22....A Plex Community member
#
#	Provided functions are:
#
# Returns the path to ~Library/Plex Media Server
#		GetLibPath(Secret)
#			Call like http://PMS:32400/utils/devtools?Func=GetLibPath&Secret=1234
#
# Returns the contents of an xml file
# 	GetXMLFile(Secret, Path)
#			Call like http://PMS:32400/utils/devtools?Func=GetXMLFile&Secret=1234&Path=<Path to file>
#
# Return the version of this plugin
# 	GetVersion(Secret)
#			Call like http://PMS:32400/utils/devtools?Func=GetVersion&Secret=1234
#
# Return the contents of an OpenSubTitle XML file for a bundle
#		GetOSXml(Secret, Bundle)
#			Call like http://PMS:32400/utils/devtools?Func=GetOSXml&Secret=1234&Bundle=1e0f180c5eb1a91a2e8d10e341a3050ceb429449
#
# Delete a subtitle file downloaded by the OpenSubtitle PlugIn
#		#	DelOSSrt(Secret, Bundle, SrtFile)
#			Call like: http://qnap2:32400/utils/devtools?Func=DelOSSrt&Secret=1234&Bundle=1e0f180c5eb1a91a2e8d10e341a3050ceb429449&SrtFile=94e38a0053dadb3c8ae0078c1571054f4fe65f96.srt
#
####################################################################################################
#TODO
# Hash Secret pwd.....Needs to be hashed as well on the client
####################################################################################################

#**********  Imports needed *************
import xml.etree.ElementTree as et
import urllib
import os

#********** Constants needed ************
VERSION = '0.0.0.3'
NAME = 'DevTools'
PREFIX = '/utils/devtools'
ART = 'art-default.jpg'
ICON = 'DevTools.png'
ERRORAUTH = 'Error authenticating'


####################################################################################################
# Start function
####################################################################################################
def Start():
	print("********  Started %s V%s on %s  **********" %(NAME, VERSION, Platform.OS))
	Log.Debug("*******  Started %s V%s on %s  ***********" %(NAME, VERSION, Platform.OS))
	HTTP.CacheTime = 0
	Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
	ObjectContainer.art = R(ART)
	ObjectContainer.title1 = NAME  + ' V' + VERSION
	ObjectContainer.view_group = 'List'
	DirectoryObject.thumb = R(ICON)

####################################################################################################
# Main function
####################################################################################################
''' Main menu '''
@handler(PREFIX, NAME, thumb=ICON, art=ART)
def MainMenu(Func='', Secret='', **kwargs):
	Log.Debug("***** Got a call for function %s with a secret of %s  ******" %(Func, Secret))
	if Func=='':
		# We most likely called this from the WebAdmin interface
		oc = ObjectContainer()
		oc.add(DirectoryObject(key=Callback(MainMenu), title="Select Preferences to set the shared secret"))
		oc.add(PrefsObject(title='Preferences', thumb=R('icon-prefs.png')))
		return oc
	elif Func=='GetLibPath':
		return GetLibPath(Secret)
	elif Func=='GetXMLFile':
		return GetXMLFile(Secret, kwargs.get("Path"))
	elif Func=='GetVersion':
		if PwdOK(Secret):
			return VERSION
		else:
			return ERRORAUTH
	elif Func=='GetOSXml':
		return GetOSXml(Secret, kwargs.get("Bundle"))
	elif Func=='DelOSSrt':
		return DelOSSrt(Secret, kwargs.get("Bundle"), kwargs.get("SrtFile"))

####################################################################################################
# Check Secret
####################################################################################################
''' Check if the Secret provided is valid
Returns true is okay, and else false '''
@route(PREFIX + '/PwdOK')
def PwdOK(Secret):
	if (Prefs['Secret'] == Secret):
		return True
	else:
		return False

####################################################################################################
# Return path to PMS/Library
####################################################################################################
''' Return path to PMS/Library '''
@route(PREFIX + '/GetLibPath')
def GetLibPath(Secret):
	if PwdOK(Secret):
		Log.Debug('Returning Library path as %s' %(Core.app_support_path))
		return Core.app_support_path
	else:
		return ERRORAUTH

####################################################################################################
# Returns the contents of an XML file
####################################################################################################
''' Returns the contents of an XML file '''
@route(PREFIX + '/GetXMLFile')
def GetXMLFile(Secret, Path):
	if PwdOK(Secret):
		Log.Debug('Getting contents of an XML file named %s' %(Path))
		document = et.parse( Path )
		root = document.getroot()
		return et.tostring(root, encoding='utf8', method='xml')
	else:
		return ERRORAUTH

####################################################################################################
# Returns the contents of an OpenSubtitle XML file
####################################################################################################
''' Returns the contents of an OpenSubtitle XML file '''
@route(PREFIX + '/GetOSXml')
def GetOSXml(Secret, Bundle):
	if PwdOK(Secret):
		myFile = os.path.join(Core.app_support_path, 'Media', 'localhost', Bundle[:1], Bundle[1:] + '.bundle', 'Contents', 'Subtitle Contributions', 'com.plexapp.agents.opensubtitles.xml')
		Log.Debug('Getting contents of an OS XML file named %s' %(myFile))
		document = et.parse( myFile )
		root = document.getroot()
		return et.tostring(root, encoding='utf8', method='xml')
	else:
		return ERRORAUTH

####################################################################################################
# Delete an OpenSubtitle downloaded srt file
####################################################################################################
''' Delete a subtitle file downloaded by OpenSubtitles
		Returns ok if all goes well '''
@route(PREFIX + '/DelOSSrt')
def DelOSSrt(Secret, Bundle, SrtFile):
	if PwdOK(Secret):
		# Start by getting the OS XML file
		myFile = os.path.join(Core.app_support_path, 'Media', 'localhost', Bundle[:1], Bundle[1:] + '.bundle', 'Contents', 'Subtitle Contributions', 'com.plexapp.agents.opensubtitles.xml')
		Log.Debug('Getting contents of an OS XML file named %s' %(myFile))
		document = et.parse( myFile )
		root = document.getroot()
		myResult = 'Not found'
		myLanguages = root.findall('Language')		
		for language in myLanguages:
			if myResult=='Not Found':
				myLang = language.get('code')
				for myLangNode in language.findall('Subtitle'):
					myMedia = myLangNode.get('media')
					if myMedia == SrtFile:
						myResult = os.path.join(myLang, myMedia)
						break
			else:
				break	
		# Now we got the filename and dir name, so let's nuke the file
		nukeFile = os.path.join(Core.app_support_path, 'Media', 'localhost', Bundle[:1], Bundle[1:] + '.bundle', 'Contents', 'Subtitle Contributions', 'com.plexapp.agents.opensubtitles', myResult )
		try:
			os.remove(nukeFile)
			return 'ok'
		except OSError:
			return 'error'
	else:
		return ERRORAUTH


