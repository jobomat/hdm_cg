# -------------------------------------------------------------------------------------------------------
# Maya Submitter Script for the RenderPal V2 Submitter V2.14.2
# For support send email to: support@shoran.de
# -------------------------------------------------------------------------------------------------------
# Copyright (c) Shoran Software. All rights reserved.
# -------------------------------------------------------------------------------------------------------
#
# INSTRUCTIONS:
#  Note: Installation instructions can be found in the accompanying Install.txt
#
#  This script requires a copy of the RenderPal V2 Submitter. If you haven't got one yet, go to
#  http://www.renderpal.com to download the submitter for your system.
#
#  Before using this script, run the RenderPal V2 Submitter once; this will register an environment
#  variable so that the script can automatically locate the submitter.
#
# TROUBLESHOOTING:
#  If the submitter has been properly installed, this script does not require any configuration and
#  works right out-of-the-box. If you run into problems, however, try the following:
#    1. Run the submitter and make sure that it is working correctly
#    2. In the submitter, configure the RenderPal V2 Server address and login
#    3. On some systems, a reboot might be needed before the submitter can be found
#    4. If the submitter still cannot be found, you can modify the global submitter path (see below)
#       accordingly
#    5. Otherwise, contact us at support@shoran.de
#
# -------------------------------------------------------------------------------------------------------

import os, platform, tempfile, ConfigParser, subprocess
import maya.cmds, maya.mel

# The global submitter path; leave empty to let the script read the path from
# the system environment. Only enter the full path to the submitter if necessary
g_rpSubmitterLocation = "K:/pipeline/software/RenderPalSubmitter"

# -- The rest of this script should not be modified --

g_rpSubmitterExe	= "RpSubmitter"
g_rpSubmitterPath	= ""

g_rpSettingsFile	= ""

# -- Global constants

c_attr_renderGlobals	= "renderGlobals"
c_attr_resolution		= "resolution"

# -- Global script data

d_layers	= {}
d_cameras	= {}

d_attributeNames			= {}
d_attributeNames["default"]	= {"startFrame": "startFrame", "endFrame": "endFrame", "byFrame": "byFrameStep"}
d_attributeNames["vray"]	= {"startFrame": "startFrame", "endFrame": "endFrame", "byFrame": "frameStep"}

d_exportAttributes				= {}	# [Section, MayaAttributeSection, MayaAttribute]
d_exportAttributes["width"]		= ["RenderSettings", c_attr_resolution, "width"]
d_exportAttributes["height"]	= ["RenderSettings", c_attr_resolution, "height"]

d_noteAttributes				= {}	# [Section, Key]
d_noteAttributes["frames"]		= ["RenderSettings", "frames"]
d_noteAttributes["framestep"]	= ["RenderSettings", "fstep"]
d_noteAttributes["width"]		= ["RenderSettings", "width"]
d_noteAttributes["height"]		= ["RenderSettings", "height"]

if platform.system().lower() == "windows":
	g_rpSubmitterExe = "RpSubmitter.exe"

# -- Helper functions

def rpPrint(msg):
	print "rpSubmit: " + msg
	
def rpError(msg):
	rpPrint("ERROR! " + msg)
	maya.cmds.confirmDialog(title="RenderPal V2 Submitter Integration", message="An error occurred:\n\n" + msg, button="OK", defaultButton="OK")
	
	return False
	
def rpAddIniSection(cfgParser, section):
	try:
		cfgParser.add_section(section)
	except:
		pass
	
def rpFormatIniValue(val):
	val = str(val)	
	val = val.replace("\\", "/")
	val = val.replace(";", ",")
	val = val.replace("\n", "\\n")
	val = val.replace("\r", "")
	
	return val
	
# -- Renderer handling helper functions

def rpGetSettingsNames(renderer):
	global c_attr_renderGlobals, c_attr_resolution
	
	rendererSettings	= "defaultRenderGlobals"
	resolutionSettings	= "defaultResolution"
	
	if renderer == "vray":
		rendererSettings	= "vraySettings"
		resolutionSettings	= "vraySettings"	
	elif renderer == "redshift":
		rendererSettings	= "redshiftOptions"
		resolutionSettings	= "redshiftOptions"
	
	return {c_attr_renderGlobals: rendererSettings, c_attr_resolution: resolutionSettings}
	
def rpGetRendererName(renderer):
	renderer = renderer.lower()	
	
	rpRenderer	= "Scene renderer"
	
	if renderer == "mayasoftware":
		rpRenderer = "Software Renderer"
	elif renderer == "mentalray":
		rpRenderer = "mental ray for Maya"
	elif renderer == "redshift":
		rpRenderer = "Redshift for Maya"
	elif renderer == "vray":
		rpRenderer = "V-Ray for Maya"
	elif renderer == "mayahardware":
		rpRenderer = "Hardware Renderer"
	elif renderer == "mayavector":
		rpRenderer = "Vector Renderer"
	elif renderer == "turtle":
		rpRenderer = "Turtle"
	elif renderer == "arnold":
		rpRenderer = "Arnold Renderer"
	elif renderer == "renderman" or renderer == "rms":
		rpRenderer = "RenderMan for Maya"
		
	return rpRenderer
	
def rpGetAttributeName(renderer, attribute):
	global d_attributeNames
		
	attributes = d_attributeNames["default"]
	
	if renderer in d_attributeNames:
		attributes = d_attributeNames[renderer]
		
	result = None
	
	try:
		result = attributes[attribute]
	except:
		result = attribute
		
	return result

# -- Core functions

def rpReadSubmitterPath():
	global g_rpSubmitterLocation, g_rpSubmitterExe, g_rpSubmitterPath
	
	if g_rpSubmitterLocation != "":
		fullPath = os.path.join(g_rpSubmitterLocation, g_rpSubmitterExe)
		
		if not os.path.isfile(fullPath):
			g_rpSubmitterLocation = ""

	if (g_rpSubmitterLocation == "") and ("RP_SUBMITTER_DIR" in os.environ):
		g_rpSubmitterLocation = os.environ["RP_SUBMITTER_DIR"]
	
	g_rpSubmitterPath = os.path.normpath(os.path.join(g_rpSubmitterLocation, g_rpSubmitterExe))

	return (g_rpSubmitterPath != "") and os.path.isfile(g_rpSubmitterPath)	

def rpExportSettings():
	global g_rpSettingsFile
	global c_attr_renderGlobals, c_attr_resolution
	global d_layers, d_cameras
	
	g_rpSettingsFile	= os.path.join(tempfile.gettempdir(), "RpSubmitterData.ini")
	
	cfgParser	= ConfigParser.SafeConfigParser()		
	sceneFile	= maya.cmds.file(q=True, sn=True)	

	# -- The scene
	
	rpAddIniSection(cfgParser, "Scene")
	cfgParser.set("Scene", "scene", rpFormatIniValue(sceneFile))
		
	# -- Render settings
	
	rpAddIniSection(cfgParser, "RenderSettings")
	
	try:
		outDir	= maya.cmds.workspace(expandName=maya.cmds.workspace("images", q=True, fre=True))
		
		if outDir != None and outDir != "":
			cfgParser.set("RenderSettings", "outdir", rpFormatIniValue(outDir))		
	except:
		pass

	try:	
		projDir	= maya.cmds.workspace(q=True, fn=True)
		
		if projDir != None and projDir != "":
			cfgParser.set("RenderSettings", "projdir", rpFormatIniValue(projDir))
	except:
		pass
		
	# -- Job data
	
	allLayers	= maya.cmds.listConnections("renderLayerManager.renderLayerId", p=0, d=1, s=0)	
	layers		= []
	cameras		= maya.cmds.ls(ca=True)
	
	for curLayer in allLayers:
		if maya.cmds.getAttr(curLayer + ".renderable"):
			layers.append(str(curLayer))
			
	if len(layers) == 0:
		return rpError("There are no renderable layers in your scene.")
	
	rpAddIniSection(cfgParser, "GenerateJobs")
	
	for idx, curLayer in enumerate(layers):
		layerID				= "Layer" + ("%02d" % idx)
		d_layers[curLayer]	= layerID
		
		cfgParser.set("GenerateJobs", layerID, rpFormatIniValue(curLayer))
		
	for idx, curCam in enumerate(cameras):
		cameraID			= "Cam" + ("%02d" % idx)
		d_cameras[curCam]	= cameraID
		
		cfgParser.set("GenerateJobs", cameraID, rpFormatIniValue(curCam))
		
	# -- Job generation
		
	jobIdx = 0
		
	for curCamera in cameras:
		camLayers = rpGetCameraLayers(curCamera)
		
		if camLayers == None or len(camLayers) == 0:
			camLayers = layers
		
		for curLayer in camLayers:
			if not curLayer in layers:
				continue
				
			camRenderable, dummy = rpGetMayaAttributeEx(curCamera, "renderable", curLayer)
			
			if not camRenderable:
				continue
			
			jobName = os.path.basename(sceneFile) + " - Camera: " + curCamera + " Layer: " + curLayer
			
			section = "GeneralSettings." + str(jobIdx)
			rpAddIniSection(cfgParser, section)
			cfgParser.set(section, "nj_name", rpFormatIniValue(jobName))
			rpExportSettings_Notes(cfgParser, section, curCamera, curLayer)
			
			section = "RenderSettings." + str(jobIdx)
			rpAddIniSection(cfgParser, section)
			cfgParser.set(section, "layer", rpFormatIniValue(curLayer))
			cfgParser.set(section, "camera", rpFormatIniValue(curCamera))
			
			jobIdx += 1
			
	if jobIdx == 0:
		return rpError("There are no renderable cameras in your scene.")
			
	# -- Job count
	
	jobCount = jobIdx		
	
	rpAddIniSection(cfgParser, "Main")
	cfgParser.set("Main", "JobCount", rpFormatIniValue(jobCount))
		
	# -- Layer-specific settings
	
	for layer in layers:
		if layer == "masterLayer":
			layer = "defaultRenderLayer"
		
		layerRenderer		= rpGetLayerRenderer(layer)
		settingNames		= rpGetSettingsNames(layerRenderer)
		rendererSettings	= settingNames[c_attr_renderGlobals]
		resolutionSettings	= settingNames[c_attr_resolution]
			
		section = "JobSettings." + d_layers[layer]		
		rpExportSettings_Renderer(cfgParser, section, layerRenderer)
			
		section = "RenderSettings." + d_layers[layer]
		
		layerAnimRange = rpGetLayerAnimationValues(layerRenderer, rendererSettings, layer)
		
		if layerAnimRange != None:			
			rpExportSettings_Frames(cfgParser, section, layerAnimRange)
			
		rpExportSettings_LayerSettings(cfgParser, layerRenderer, layer)
			
	# -- Camera-specific settings
			
	for camera in cameras:
		try:
			camNotes = maya.cmds.getAttr(camera + ".notes")
			
			if camNotes != None and camNotes != "":
				rpExportSettings_ObjectNotes(cfgParser, d_cameras[camera], camNotes)
		except:
			pass		
	
	# -- Data
	
	rpAddIniSection(cfgParser, "Data")
	
	cfgParser.set("Data", "layer", rpFormatIniValue(",".join(layers)))	
	cfgParser.set("Data", "camera", rpFormatIniValue(",".join(cameras)))
	
	# -- All exported, write the .ini
	
	with open(g_rpSettingsFile, "wb") as cfgFile:
		cfgParser.write(cfgFile)
	
	return True
	
def rpExportSettings_Frames(cfgParser, section, animRange):
	startFrame	= int(animRange[0])
	endFrame	= int(animRange[1])
	byFrame		= int(animRange[2])
		
	rpAddIniSection(cfgParser, section)
	
	if startFrame != endFrame:
		cfgParser.set(section, "frames", str(startFrame) + "-" + str(endFrame))
	else:
		cfgParser.set(section, "frames", str(startFrame))

	cfgParser.set(section, "fstep", str(byFrame))
	
def rpExportSettings_Renderer(cfgParser, section, renderer):
	rpAddIniSection(cfgParser, section)		
	cfgParser.set(section, "nj_renderer", rpFormatIniValue(renderer))
	
def rpExportSettings_LayerSettings(cfgParser, renderer, layer):
	global d_layers
	global d_exportAttributes
	
	settings = rpGetSettingsNames(renderer)
	
	try:
		for curAttr in d_exportAttributes:
			section, settingsIdx, attrName	= d_exportAttributes[curAttr]
			value, dummy					= rpGetMayaAttributeEx(settings[settingsIdx], rpGetAttributeName(renderer, attrName), layer)
			
			if value != None:
				section = section + "." + d_layers[layer]
				rpAddIniSection(cfgParser, section)
				cfgParser.set(section, curAttr, rpFormatIniValue(str(value)))	
	except:
		pass
		
def rpExportSettings_Notes(cfgParser, section, camera, layer):
	try:
		camNotes = maya.cmds.getAttr(camera + ".notes")
				
		if camNotes != None and camNotes != "":
			cfgParser.set(section, "nj_notes", rpFormatIniValue(camNotes))
	except:
		pass
	
def rpExportSettings_ObjectNotes(cfgParser, obj, notes):
	global d_noteAttributes
	
	noteData = rpParseNotes(notes)
	
	for key in noteData:
		value = noteData[key]
		
		if key in d_noteAttributes:
			section, valName	= d_noteAttributes[key]
			section				= section + "." + obj
				
			rpAddIniSection(cfgParser, section)
			cfgParser.set(section, valName, rpFormatIniValue(str(value)))
	
def rpPrepareSubmission():
	global g_rpSettingsFile
	
	sceneFile = maya.cmds.file(q=True, sn=True)
	
	if sceneFile == "":
		return rpError("Please save your scene before submitting it.")
		
	if rpExportSettings():
		rpPrint("  Settings exported to: " + g_rpSettingsFile)
	else:
		return False
	
	return True
	
def rpLaunchSubmitter():
	global g_rpSubmitterPath, g_rpSettingsFile
	
	rpPrint("Launching RenderPal V2 Submitter...")
	subprocess.Popen([g_rpSubmitterPath, "--group", "Maya", "--import", g_rpSettingsFile, "--delete-ini"])	
	rpPrint("  Done")
	
# -- Maya helper functions

def rpGetMayaAttributeConnection(section, attribute, layer):
	result = None
	
	try:
		layerOverrides	= maya.cmds.listConnections(layer + ".adjustments", p=True, c=True)
		
		if layerOverrides != None and len(layerOverrides) > 1:
			for i in range(0, len(layerOverrides) / 2):
				override 				= layerOverrides[(i * 2) + 1]
				layerOverrides[i * 2]	= layerOverrides[i * 2].replace(".plug", ".value")
				
				if override == (section + "." + attribute):
					result = maya.cmds.getAttr(layerOverrides[i * 2])
					break
	except:
		pass
			
	return result

def rpGetMayaAttributeEx(section, attribute, layer, defSection="defaultRenderGlobals"):
	result		= (None, False)
	layerCon	= rpGetMayaAttributeConnection(section, attribute, layer)
	
	if layerCon != None:
		result = (layerCon, True)
	else:
		defaultCon = rpGetMayaAttributeConnection(section, attribute, "defaultRenderLayer")
		
		if defaultCon != None:
			result = (defaultCon, True)
		else:
			try:
				result = (maya.cmds.getAttr(section + "." + attribute), False)
			except:
				try:
					result = (maya.cmds.getAttr(defSection + "." + attribute), False)
				except:
					pass
		
	return result

# -- Renderer specific helper functions

def rpGetLayerRenderer(layer):
	renderer, dummy = rpGetMayaAttributeEx("defaultRenderGlobals", "currentRenderer", layer)
	return rpGetRendererName(renderer)
	
def rpGetLayerAnimationValues(renderer, rendererSettings, layer):	
	startFrame	= endFrame = maya.cmds.currentTime(q=True)
	byFrame		= 1
	
	animation	= maya.cmds.getAttr("defaultRenderGlobals.animation")

	if animation:
		fps = float(maya.mel.eval("currentTimeUnitToFPS"))
	
		startFrame, sfOverride	= rpGetMayaAttributeEx(rendererSettings, rpGetAttributeName(renderer, "startFrame"), layer)
		endFrame, efOverride	= rpGetMayaAttributeEx(rendererSettings, rpGetAttributeName(renderer, "endFrame"), layer)
		byFrame, bfOverride		= rpGetMayaAttributeEx(rendererSettings, rpGetAttributeName(renderer, "byFrame"), layer)
	
		if sfOverride:
			startFrame = float(startFrame) * fps
		
		if efOverride:
			endFrame = float(endFrame) * fps
	
	return [round(startFrame, 3), round(endFrame, 3), round(byFrame, 3)]
	
def rpParseNotes(notes):
	noteData = {}
	
	try:
		lines = notes.split("\n")
		
		for line in lines:
			line = line.strip()
			
			if line == "":
				continue
			
			key, value	= line.split(":")
			key			= key.strip().lower()
			value		= value.strip()
			
			noteData[key] = value
	except:
		noteData = {}
		
	return noteData
	
def rpGetCameraLayers(camera):
	result = None
	
	try:
		camNotes = maya.cmds.getAttr(camera + ".notes")
			
		if camNotes != None and camNotes != "":
			noteData = rpParseNotes(camNotes)
			
			if "layer" in noteData:
				noteData["layers"] = noteData["layer"]
				
			if "layers" in noteData:
				result		= []
				layerList	= noteData["layers"].replace(";", ",").split(",")
				
				for layer in layerList:
					result.append(layer.strip())
	except:
		pass			
		
	return result
	
# -- Main function

def rpSubmit():
	rpPrint("Initializing...")
	
	if rpReadSubmitterPath():
		rpPrint("  Submitter location: " + g_rpSubmitterPath)
	else:
		return rpError("RenderPal V2 Submitter not found. Make sure that there is a copy installed on this system and that you have run it at least once.")
	
	if rpPrepareSubmission():
		rpLaunchSubmitter()			
		
	return True
	