"""
Autor: David Zuber
Datum: 12.04.2013

Kleines Script zum Spass fuers BlendShape-modeln
Ansonsten ziemlich nutzlos
"""
import maya.cmds as cmds

def bsUI():
	
	width =250
	height=20
	#check to see if window exists
	if cmds.window("dz_createBSUI", exists=1):
		cmds.deleteUI("dz_createBSUI")
	
	#create window
	window = cmds.window("dz_createBSUI", title="create new BlendShape Mesh", w= width, h= height, mnb=0,mxb=0,sizeable=1)
	
	#create a main layout
	mainLayout =cmds.rowLayout(w=width, h=height,nc=2)
	
	cmds.text(label="Name:")
	tf = cmds.textField(w=200,aie=1,ec=createBS)
	
	cmds.showWindow(window)
	
def createBS(name):
	#create duplicate of baseShape_geo
	duplicate = cmds.duplicate("baseShape_geo",n=name)[0]
	print ("Created Duplicate of baseShape_geo: %s"%name)
	
	#hide other geo
	geo = cmds.listRelatives(cmds.ls(g=1),parent=1)
	
	for geometry in geo:
		cmds.setAttr("%s.visibility"%geometry, 0)
	cmds.setAttr("%s.visibility"%duplicate , 1)
	#delete UI (evalDeffered is needed! fatalError if a field of a window issues a deleteUI callback
	cmds.evalDeferred("cmds.deleteUI(\"dz_createBSUI\")")

def offsetUI():
	width =250
	height=20
	#check to see if window exists
	if cmds.window("dz_offsetUI", exists=1):
		cmds.deleteUI("dz_offsetUI")
	
	#create window
	window = cmds.window("dz_offsetUI", title="create new BlendShape Mesh", w= width, h= height, mnb=0,mxb=0,sizeable=1)
	
	#create a main layout
	mainLayout =cmds.rowLayout(w=width, h=height,nc=2)
	
	cmds.text(label="Offset:")
	tf = cmds.textField(w=200,aie=1,ec=offsetObjects)
	
	cmds.showWindow(window)

def toggleVisBase():
	if(cmds.getAttr("baseShape_geo.visibility")):
		cmds.setAttr("baseShape_geo.visibility", 0)
	else:
		cmds.setAttr("baseShape_geo.visibility",1)
		
def offsetObjects(offset):
	objs=cmds.ls(sl=1)
	count = 1
	for obj in objs:
		cmds.select(obj)
		cmds.move(float(offset)*count, x=1)
		count +=1
	
	#delete UI (evalDeffered is needed! fatalError if a field of a window issues a deleteUI callback
	cmds.evalDeferred("cmds.deleteUI(\"dz_offsetUI\")")
