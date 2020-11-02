import maya.cmds as cmds
import maya.OpenMaya as api
import maya.OpenMayaUI as apiUI
import math
from functools import partial

def getShapes(xform ):
	shapes = []
	shapes.append(xform)
	if cmds.nodeType(xform) == "transform":
		# If given node is not a transform, assume it is a shape and pass it through
		shapes = cmds.listRelatives( xform, fullPath=True, shapes=True)	
	return shapes
	
def getTransform(shape ):
	transform = ""
	if cmds.nodeType(shape) == "transform":
		# If given node is already a transform, just pass on through
		parents = cmds.listRelatives(shape, fullPath=True, parent=True )
		transform = parents[0]
	return transform

def faceCenter():

    faceCenter = []

    selection = api.MSelectionList()
    api.MGlobal.getActiveSelectionList(selection)
    print ("Number of objects in selection: %s " % selection.length())

    iter = api.MItSelectionList (selection, api.MFn.kMeshPolygonComponent)

    while not iter.isDone():
        status = api.MStatus
        dagPath = api.MDagPath()
        component = api.MObject()

        iter.getDagPath(dagPath, component)

        polyIter = api.MItMeshPolygon(dagPath, component)

        while not polyIter.isDone():

            i = 0
            i = polyIter.index()
            faceInfo = [0]
            faceInfo[0] = ("The center point of face %s is:" %i)
            faceCenter+=faceInfo

            center = api.MPoint
            center = polyIter.center(api.MSpace.kWorld)
            point = [0.0,0.0,0.0]
            point[0] = center.x
            point[1] = center.y
            point[2] = center.z
            faceCenter += point
            
            polyIter.next()
            
        iter.next()
        
    return faceCenter

def fileExists(filepath):
    try:
        f = open(filepath, "r")
    except IOError as e:
        return False
    return True

def listHirarchy(objekt):
     info = cmds.ls(objekt,st=True)
     content = []
     content.append({'name':objekt,'type':info[1],'childs':listContentsRecursive(objekt)})
     return content

def listContentsRecursive(objekt):
    list = cmds.listRelatives(objekt, ad=False)
    content = []
    
    if list:
        for obj in list:
            info = cmds.ls(obj,st=True)
            content.append({'name':info[0],'type':info[1],'childs':listContentsRecursive(info[0])})
    return content

def addGroupWithTransforms(objekt,groupname=""):
    groupname = (objekt+"_grp") if not groupname else groupname
    grp = cmds.group(empty=True, name=groupname)
    par = cmds.listRelatives(objekt, p=True)  
    constraint = cmds.parentConstraint(objekt,grp)
    cmds.delete(constraint)
    if par:
        cmds.parent(grp, par[0])
    cmds.parent(objekt, grp)
    return grp


#   Given a namepattern 'name' and a list of objects
#   hashRename will rename every object in the list and
#   replace every #-character in the name-pattern with a number
#   including leading zeros.
def hashRename(name, objects):
    import re

    try: hashes = re.search('#+',name).group()
    except Exception as e:
        cmds.warning("In method 'hashRename': The name-pattern has to contain at least one hash-character (#).")
        return False
        
    hashLength = len(hashes)
    zerostring = hashLength * "0"

    # if renaming hirachical interdependent nodes with the same name
    # (e.g. joint > joint > joint), renaming the parent would change 
    # the unique path to it's child and we wouldn't be able to rename
    # the child-nodes. therefore we attach all nodes to be renamed to 
    # a dummy-node and we'll find them by connection...
    dummynode = cmds.createNode('unknown')
    cmds.addAttr(ln='selObjects', at='message', multi=True, im=0)

    for obj in objects:
        # connect the attributes
        cmds.connectAttr( (obj + ".message"), (dummynode + ".selObjects"), nextAvailable=True )

    # now we can ask for the connected object and will always get the
    # actual name - not the name at the beginning of the method. 
    for i in range( 0, len(cmds.listConnections(dummynode + ".selObjects")) ):
        oldName = cmds.listConnections( "%s.selObjects[%s]" % (dummynode,i) )
        # concatenate the zerostring and the loopcounter. then cut off leading zeros.
        newName = cmds.rename(oldName[0], name.replace(hashes,(zerostring + str(i+1))[-hashLength:]))
        print "Renamed: %s to %s" % (oldName[0],newName)
    
    cmds.select( cmds.listConnections( "%s.selObjects" % dummynode ) )
    cmds.delete(dummynode)

    if int(len(objects) / (hashLength*10)):
        cmds.warning("In method 'hashRename' Objects where renamed but the number of hashes is to short to give every selected object a unique and predictable name.")

#   ViewportScreenshot:
#   Opens a Viewport of size <viewportsize> with a "Screenshot-Button". 
#   On click it writes the Framebuffer to <path><file>.<fileformat>
#   It's possible to scale the image to <imagesize> before saving.
#   <onComplete> takes a funcion which is executed after saving the image.
#
#   Example Call:
#   caUtil.ViewportScreenshot(path='E:/', imagesize=[40,30], filename='test', fileformat='bmp', onComplete=partial(changeIcon, buttonToChange, curveColor, viewportColor, lineWidth) )

class ViewportScreenshot():
    def __init__(   self, 
                    viewportsize=[180,180], 
                    imagesize=[60,60], 
                    filename='test', 
                    path='D:/', 
                    fileformat='bmp', 
                    onComplete=None,
                    onStart=None,
                    arg=None
                ):
        if cmds.window('screenshotWindow', exists=True):
            cmds.deleteUI('screenshotWindow')
            
         
        self.ssWindow = cmds.window('screenshotWindow',w=viewportsize[0],h=(viewportsize[1]+20),maximizeButton=False,minimizeButton=False,sizeable=False)
        column = cmds.columnLayout()
        form = cmds.formLayout(w=viewportsize[0], h=viewportsize[1])
        
        self.ssEditor = cmds.modelEditor(grid=False, cameras=False, av=True, rendererName="vp2Renderer", headsUpDisplay=False)
        cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable", 1)
        cmds.formLayout( form, edit=True, attachForm=[ (self.ssEditor, 'top', 0), (self.ssEditor, 'left', 0), (self.ssEditor, 'bottom', 0),(self.ssEditor, 'right', 0)])
        cmds.setParent('..')
        
        #   Create a camera 
        camera = cmds.camera(position=(2,2.5,2), rotation = (-40, 45, 0), name="temporary_screenshot_cam")
        self.ssCam = camera[0]
        
        cmds.button(label='Make Screenshot', w=viewportsize[0], c=partial(self.takeScreenshot, imagesize, path, filename, fileformat,onComplete))
        
        #   Attach the camera to the model editor.
        cmds.modelEditor( self.ssEditor, edit=True, camera=self.ssCam )
        
        cmds.showWindow( self.ssWindow )
        cmds.scriptJob( uiDeleted=[self.ssWindow,self.deleteScreenshotCam])
        
        #   make modelEditor the active view and frame Selection
        cmds.modelEditor(self.ssEditor, edit=True, av=True)
        cmds.viewFit(all=True)
        
    def takeScreenshot(self, imagesize, path, filename, fileformat, onComplete, arg=None):
        cmds.refresh()
        image = api.MImage()
        #   Bug Workaraound: 
        #   "Move" Cam or otherwise the imagebuffer will be black
        #   if the cam wasn't used by the user... ???
        cmds.modelEditor( self.ssEditor, edit=True ,av=True )
        cmds.setAttr(self.ssCam+".ty", cmds.getAttr(self.ssCam+".ty"))
        
        view = apiUI.M3dView.active3dView()
        view.refresh()
        view.readColorBuffer(image, True)
        image.resize(imagesize[0],imagesize[1],True)
        #   Write image into a file:
        
        image.writeToFile(path+filename+'.'+fileformat, fileformat)
        cmds.deleteUI(self.ssWindow)
        if onComplete!=None:
            onComplete()
            
    def deleteScreenshotCam(self, arg=None):
        cmds.delete(self.ssCam)