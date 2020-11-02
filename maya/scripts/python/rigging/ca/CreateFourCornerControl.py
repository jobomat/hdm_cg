"""
FourCornerControl comes in handy for facial-rigging.
FourCornerControl creates a square-control-panel with a circle slider.
For each corner one can assign a blendshape-channel 
eg	top right: 	"right smile" blendshape
	top left:	"left smile"
	bottom r:	"right frown"
	bottom l:	"left frown"
FourCornerControl will set it up correctly for you.

To call it type:
fcc = FourCornerControl()
fcc.showWindow()
"""
import maya.cmds as cmds
from functools import partial

class FourCornerControl:
	def __init__(self):
		self.shapeA = ""
		self.shapeB = ""
		self.shapeC = ""
		self.shapeD = ""
		
		self.blendNode = ""
		
		self.buttonA = None
		self.buttonB = None
		self.buttonC = None
		self.buttonD = None
		
		self.doit = None
		
	def assignAttribute(self,field = None,arg = None):
		message = ""
		sel = cmds.ls(sl=True)
		self.blendNode = sel[0]
		
		#read selected channel from channelbox
		if field == "A":
			self.shapeA = cmds.channelBox("mainChannelBox", query=True, selectedMainAttributes=True )
			if self.shapeA != None:
				cmds.button( self.buttonA, edit=True, label=self.shapeA[0])
			else:
				message = "empty"
		if field == "B":
			self.shapeB = cmds.channelBox("mainChannelBox", query=True, selectedMainAttributes=True )
			if self.shapeB != None:
				cmds.button( self.buttonB, edit=True, label=self.shapeB[0])
			else:
				message = "empty"
		if field == "C":
			self.shapeC = cmds.channelBox("mainChannelBox", query=True, selectedMainAttributes=True )
			if self.shapeC != None:
				cmds.button( self.buttonC, edit=True, label=self.shapeC[0])
			else:
				message = "empty"
		if field == "D":
			self.shapeD = cmds.channelBox("mainChannelBox", query=True, selectedMainAttributes=True )
			if self.shapeD != None:
				cmds.button( self.buttonD, edit=True, label=self.shapeD[0])
			else:
				message = "empty"
		
		if message == "empty":
			cmds.confirmDialog( title='Info', message='Please select an attribute from the Channelbox, then click the Button.',button=['Sir, Yes, Sir!'])
		
		#if all 4 corners are assigned unlock the button
		if (self.shapeA != "") and (self.shapeB != "") and (self.shapeC != "") and (self.shapeD != ""):
			cmds.button(self.doit, edit=True, enable=True)
			
	def createControl(self,*args):
		# create geometry for the control:
		# the square-curve:
		shapesname = self.shapeA[0]+"_"+self.shapeB[0]+"_"+self.shapeC[0]+"_"+self.shapeD[0]
		c = cmds.curve(d=1,p=[(-1, 1, 0), (1, 1, 0), (1, -1, 0), (-1, -1, 0), (-1, 1, 0)], k=[0,1,2,3,4])
		square = cmds.rename(c,(shapesname+"_frame"))
		# the circle:
		c = cmds.curve(d=3,p=[(0,0.3,0),(-0.212132,0.212132,0),(-0.3,0,0),(-0.212132,-0.212132,0),(0,-0.3,0),(0.212132,-0.212132,0),(0.3,0,0),(0.212132,0.212132,0)], k=[0,0,0,1,2,3,4,5,5,5])
		cmds.closeCurve( c, ch=1, ps=0, rpo=1, bb=0.5, bki=0, p=0.1)
		circle = cmds.rename(c,(shapesname+"_ctrl"))
		# parent and prepare limits
		cmds.parent(circle,square)
		cmds.transformLimits( tx=(-1,1), ty=(-1,1), tz=(0,0) )
		cmds.transformLimits( etx=(True,True), ety=(True,True), etz=(True,True ) )
		
		# CORE:
		# quad 1 (top right)
		setRangeNode1 = cmds.createNode( 'setRange', n=(self.shapeA[0]+"_decrease_"+self.shapeD[0]+"_range") )
		cmds.connectAttr(circle+".tx",setRangeNode1+".valueX")
		cmds.connectAttr(circle+".ty",setRangeNode1+".valueY")
		cmds.setAttr(setRangeNode1+".oldMinX", -1)
		cmds.setAttr(setRangeNode1+".minX", 0)
		cmds.setAttr(setRangeNode1+".oldMaxX", 0)
		cmds.setAttr(setRangeNode1+".maxX", 1)
		cmds.setAttr(setRangeNode1+".oldMinY", 0)
		cmds.setAttr(setRangeNode1+".minY", 0)
		cmds.setAttr(setRangeNode1+".oldMaxY", 1)
		cmds.setAttr(setRangeNode1+".maxY", 1)
		
		# quad 2 (bottom right)
		setRangeNode2 = cmds.createNode( 'setRange', n=(self.shapeB[0]+"_decrease_"+self.shapeC[0]+"_range") )
		cmds.connectAttr(circle+".tx",setRangeNode2+".valueX")
		cmds.connectAttr(circle+".ty",setRangeNode2+".valueY")
		cmds.setAttr(setRangeNode2+".oldMinX", -1)
		cmds.setAttr(setRangeNode2+".minX", 0)
		cmds.setAttr(setRangeNode2+".oldMaxX", 0)
		cmds.setAttr(setRangeNode2+".maxX", 1)
		cmds.setAttr(setRangeNode2+".oldMinY", -1)
		cmds.setAttr(setRangeNode2+".minY", 1)
		cmds.setAttr(setRangeNode2+".oldMaxY", 0)
		cmds.setAttr(setRangeNode2+".maxY", 0)
		
		# quad 3 (bottom left)
		setRangeNode3 = cmds.createNode( 'setRange', n=(self.shapeC[0]+"_decrease_"+self.shapeB[0]+"_range") )
		cmds.connectAttr(circle+".tx",setRangeNode3+".valueX")
		cmds.connectAttr(circle+".ty",setRangeNode3+".valueY")
		cmds.setAttr(setRangeNode3+".oldMinX", 0)
		cmds.setAttr(setRangeNode3+".minX", 1)
		cmds.setAttr(setRangeNode3+".oldMaxX", 1)
		cmds.setAttr(setRangeNode3+".maxX", 0)
		cmds.setAttr(setRangeNode3+".oldMinY", -1)
		cmds.setAttr(setRangeNode3+".minY", 1)
		cmds.setAttr(setRangeNode3+".oldMaxY", 0)
		cmds.setAttr(setRangeNode3+".maxY", 0)
		
		# quad 4 (top left)
		setRangeNode4 = cmds.createNode( 'setRange', n=(self.shapeD[0]+"_decrease_"+self.shapeA[0]+"_range") )
		cmds.connectAttr(circle+".tx",setRangeNode4+".valueX")
		cmds.connectAttr(circle+".ty",setRangeNode4+".valueY")
		cmds.setAttr(setRangeNode4+".oldMinX", 0)
		cmds.setAttr(setRangeNode4+".minX", 1)
		cmds.setAttr(setRangeNode4+".oldMaxX", 1)
		cmds.setAttr(setRangeNode4+".maxX", 0)
		cmds.setAttr(setRangeNode4+".oldMinY", 0)
		cmds.setAttr(setRangeNode4+".minY", 0)
		cmds.setAttr(setRangeNode4+".oldMaxY", 1)
		cmds.setAttr(setRangeNode4+".maxY", 1)
		
		# multipliy-Nodes and hook to blendshape:
		md = cmds.createNode('multiplyDivide')
		mdNode1 = cmds.rename(md,(self.blendNode+"_blender_"+md))
		
		cmds.connectAttr(setRangeNode1+".outValueX",mdNode1+".input1X")
		cmds.connectAttr(setRangeNode1+".outValueY",mdNode1+".input2X")
		cmds.connectAttr(mdNode1+".outputX",self.blendNode+"."+self.shapeA[0])
		
		cmds.connectAttr(setRangeNode2+".outValueX",mdNode1+".input1Y")
		cmds.connectAttr(setRangeNode2+".outValueY",mdNode1+".input2Y")
		cmds.connectAttr(mdNode1+".outputY",self.blendNode+"."+self.shapeB[0])
		
		md = cmds.createNode('multiplyDivide')
		mdNode2 = cmds.rename(md,(self.blendNode+"_blender_"+md))
		
		cmds.connectAttr(setRangeNode3+".outValueX",mdNode2+".input1X")
		cmds.connectAttr(setRangeNode3+".outValueY",mdNode2+".input2X")
		cmds.connectAttr(mdNode2+".outputX",self.blendNode+"."+self.shapeC[0])
		
		cmds.connectAttr(setRangeNode4+".outValueX",mdNode2+".input1Y")
		cmds.connectAttr(setRangeNode4+".outValueY",mdNode2+".input2Y")
		cmds.connectAttr(mdNode2+".outputY",self.blendNode+"."+self.shapeD[0])

		
	def showWindow(self):
		# build the gui
		magwin = cmds.window( title='Create Four Corner Control')
		
		cmds.frameLayout(labelVisible=False,borderVisible=True)
		cmds.separator(style="none")
		col = cmds.columnLayout(rs=5, columnAttach=["left",5])
		cmds.text(wordWrap=True, align='left', label='Select a blendshape-channel in the channelbox, then assign this channel to one of the 4 corners of the control by pressing the apropriate button below.')
		gridLayout = cmds.gridLayout(numberOfColumns=2, cellWidthHeight = [110,50])
		self.buttonD = cmds.button( label="Left Top Shape", command=partial(self.assignAttribute,"D") )
		self.buttonA = cmds.button( label="Right Top Shape", command=partial(self.assignAttribute,"A") )
		self.buttonC = cmds.button( label="Left Bottom Shape", command=partial(self.assignAttribute,"C") )
		self.buttonB = cmds.button( label="Right Bottom Shape", command=partial(self.assignAttribute,"B") )
		cmds.setParent( '..' )
		self.doit = cmds.button(enable=False,label="Create 4-Corner-Control!",command=self.createControl, width=220)
		cmds.separator(style="none")
		cmds.showWindow( magwin )
		cmds.window( magwin, edit=True, w=235, h=205)