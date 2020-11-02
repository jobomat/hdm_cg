import maya.cmds as cmds
from functools import partial

class SplitSelectedJoint():
	def __init__(self, winName="jb_splitSelectedJoint_win"):
		self.winTitle = "Split Selected Joints"
		self.winName = winName

		if cmds.window(self.winName, exists=True):
			cmds.deleteUI(self.winName)

		cmds.window(self.winName, title=self.winTitle, toolbox=True)
		self.mainCol = cmds.columnLayout( adjustableColumn=True )
		self.numSegIntfield	= cmds.intSliderGrp( columnWidth3=[110,25,165], field=True, label='Number of Segments', minValue=2, maxValue=9, fieldMinValue=2, fieldMaxValue=30, value=4 )
		cmds.rowLayout(nc=2)
		self.okButton = cmds.button( label='Split', w=145, c=partial(self.splitJoint) )
		self.cancelButton = cmds.button( label='Cancel', w=145, c="cmds.deleteUI('%s')"%self.winName )
		
		cmds.showWindow( self.winName )
		cmds.window(self.winName, edit=True, widthHeight=[300,50])

	def splitJoint(self, arg=None):
		numSegments = cmds.intSliderGrp(self.numSegIntfield, q=True, v=True)
		
		sel = cmds.ls(sl=True)
		if not len(sel):
			cmds.warning("Please select joint(s) to split!")
			return
		
		for s in sel:
			childJoints = cmds.listRelatives(s, f=True, c=True, type="joint")
			
			if not childJoints:
				cmds.warning("Joint has no child-joint. Split cannot be performed.")
				return
				
			radius = cmds.getAttr(s+".radius")
			
			distX = cmds.getAttr(childJoints[0]+".tx") and cmds.getAttr(childJoints[0]+".tx") or 0
			distY = cmds.getAttr(childJoints[0]+".ty") and cmds.getAttr(childJoints[0]+".ty") or 0
			distZ = cmds.getAttr(childJoints[0]+".tz") and cmds.getAttr(childJoints[0]+".tz") or 0
			
			deltaX = distX / numSegments
			deltaY = distY / numSegments
			deltaZ = distZ / numSegments

			jnt = s

			for i in range(0,numSegments-1):
				newJoint = cmds.insertJoint(jnt)
				newJoint = cmds.joint(newJoint, edit=True, co=True, r=True, p=[deltaX,deltaY,deltaZ], rad=radius, name=(s+"_seg_"+str(i+1)) )
				jnt=newJoint