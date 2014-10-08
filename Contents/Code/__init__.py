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
# Delete a file from the filesystem (Aka asidecar srt file....Use with care here)
#		DelFile(Secret, FileName)
#			Call like: http://PMS:32400/utils/devtools?Func=DelFile&Secret=1234&File=/share/MD0_DATA/.qpkg/PlexMediaServer/Library/Plex%20Media%20Server/test.ged
#				Note: remember to fill out spaces in the filename with %20
#
# Check if a file or directory exists Returns true if it does, and false if not
#		PathExists(Secret, Path)
#			Call like: http://PMS:32400/utils/devtools?Func=PathExists&Secret=1234&Path=/root/Library
#
# Show the contents of a txt-based file, like an srt file
#		ShowSRT(Secret, FileName)
#			Call like: http://PMS:32400/utils/devtools?Func=ShowSRT&Secret=1234&FileName=/root/Library/Plex%20Media%20Server/Media/localhost/b/4c657e372488b460b64d38d7d78ae7851343eaf.bundle/Contents/Subtitles/en/com.plexapp.agents.opensubtitles_ec8dd1a2f67607d603bcbc170e856bbfe53834e6.srt
#
# Delete an Sub file, and update all xml files involved
#		DelSub(Secret, MediaID, SubFileID)
#			Call like: http://PMS:32400/utils/devtools?Func=DelSub&Secret=1234&MediaID=2&SubFileID=109
#
####################################################################################################
#TODO
# Hash Secret pwd.....Needs to be hashed as well on the client
####################################################################################################

#**********  Imports needed *************
import xml.etree.ElementTree as et
import urllib
import os
import io

#********** Constants needed ************
VERSION = '0.0.0.8'
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
	elif Func=='DelFile':
		return DelFile(Secret, kwargs.get("File"))
	elif Func=='PathExists':
		return PathExists(Secret, kwargs.get("Path"))
	elif Func=='ShowSRT':
		return ShowSRT(Secret, kwargs.get("FileName"))
	elif Func=='DelSub':
		return DelSub(Secret, kwargs.get("MediaID"), kwargs.get("SubFileID"))

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
# Delete a file
####################################################################################################
''' Delete a file.	Returns ok if all goes well '''
@route(PREFIX + '/DelFile')
def DelFile(Secret, File):
	if PwdOK(Secret):		
		# Now we got the filename and dir name, so let's nuke the file
		try:
			fileName, fileExtension = os.path.splitext(File.upper())
			Log.Debug('Trying to delete the file %s' %(File))
			if fileExtension != '.SRT':
				os.remove(File)
				return 'ok'
			else:
				return 'error....Deleting an srt file is not supported with this function....use DelSRT function instead'
		except OSError:
			return 'error'
	else:
		return ERRORAUTH

####################################################################################################
# Check if a path exists
####################################################################################################
''' Check if a path exists.	Returns true if if it does, else false '''
@route(PREFIX + '/PathExists')
def PathExists(Secret, Path):
	if PwdOK(Secret):		
		# Now we got the filename and dir name, so let's nuke the file
		if os.path.exists(Path):
			return 'true'
		else:
			return 'false'				
	else:
		return ERRORAUTH

####################################################################################################
# Show contents of a txt file
####################################################################################################
''' Show contents of a txt file '''
@route(PREFIX + '/ShowSRT')
def ShowSRT(Secret, FileName):
	if PwdOK(Secret):
		with io.open (FileName, "rb") as myfile:		
			return myfile.read()
	else:
		return ERRORAUTH

####################################################################################################
# Delete a subtitle file
####################################################################################################
''' Delete a subtitle file.	Returns ok if all goes well '''
@route(PREFIX + '/DelSub')
def DelSub(Secret, MediaID, SubFileID):
	if PwdOK(Secret):		
		# Now we got the filename and dir name, so let's nuke the file
		try:			
			Log.Debug('***** Trying to delete the Sub file %s from the media %s *****' %(SubFileID, MediaID))
			myFiles = []
			# Let's start by grapping the media info from it's tree
			myURL = 'http://127.0.0.1:32400/library/metadata/' + MediaID + '/tree'			
			myMediaStreams = XML.ElementFromURL(myURL).xpath('//MediaPart/MediaStream')
			# We got a collection of MediaParts, so start walking them
			for myMediaStream in myMediaStreams:
				if myMediaStream.get('id') == SubFileID:
					# We got the correct sub file
					mySub = myMediaStream.get('url')
					Log.Debug('Sub file found is %s' %(mySub))
					# Okay....Got the agent, now let's find the path to the bundle/contents directory
					myHash = XML.ElementFromURL(myURL).xpath('//MediaPart/@hash')[0]
					# Create a string containing the path to the contents directory
					myPath = os.path.join(Core.app_support_path, 'Media', 'localhost', myHash[0], myHash[1:]+ '.bundle', 'Contents')
					if 'media://' in mySub:
						# Let's find the agent in spe, and start by getting LangCode/Agent
						import re
						try:
							myAgent = re.search('Contents/Subtitles/(.*)', mySub).group(1)					
						except:
							Log.Debug('Error digesting string %s' %(mySub))		
						print myAgent
						# Now seperate the lang code
						lang, myAgent = myAgent.split("/")
						# Let's get the filename
						mySubFile = myAgent							
						realAgentName, realSubFile = myAgent.split('_')
						# The result for the subtitles contribution folder						
						realSubPathForSubCont = os.path.join(myPath, 'Subtitle Contributions', realAgentName, lang, realSubFile)
						# The result for the Symbolic links
						realPathForSymbLink = os.path.join(myPath, 'Subtitles', lang, myAgent)
						# Add to array of files to delete
						myFiles.append(realSubPathForSubCont)
						myFiles.append(realPathForSymbLink)						
					else:
						realAgentName = 'com.plexapp.agents.localmedia'
						mySubFile = mySub[7:]
						myFiles.append(mySubFile)
					for myFile in myFiles:
						Log.Debug('Delete %s' %(myFile))
						os.remove(myFile)						
					# XML files that we need to manipulate
					xmlFile1 = os.path.join(myPath, 'Subtitles.xml')
					xmlFile2 = os.path.join(myPath, 'Subtitle Contributions',  realAgentName + '.xml')
					if (realAgentName!='com.plexapp.agents.localmedia'):
						DelFromXML(xmlFile2, 'media', realSubFile)
						DelFromXML(xmlFile1, 'media', realSubFile)
					else:
						DelFromXML(xmlFile2, 'file', mySubFile)
						DelFromXML(xmlFile1, 'file', mySubFile)
					break
			Log.Debug('***** DelSub ended okay *****')
			return 'ok'				
		except OSError:
			return 'error'
	else:
		return ERRORAUTH

####################################################################################################
# Delete from an XML file
####################################################################################################
''' Delete from an XML file '''
@route(PREFIX + '/DelFromXML')
def DelFromXML(fileName, attribute, value):
	Log.Debug('Need to delete element with an attribute named "%s" with a value of "%s" from file named "%s"' %(attribute, value, fileName))
	from xml.etree import ElementTree
	with io.open(fileName, 'r') as f:
		tree = ElementTree.parse(f)
		root = tree.getroot()
		mySubtitles = root.findall('.//Subtitle')
		for Subtitles in root.findall("Language[Subtitle]"):
			for node in Subtitles.findall("Subtitle"):
				myValue = node.attrib.get(attribute)
				if myValue:
					if '_' in myValue:
						drop, myValue = myValue.split("_")
					if myValue == value:
						Subtitles.remove(node)
	tree.write(fileName, encoding='utf-8', xml_declaration=True)
	return

