#coding: utf8 
import maya.cmds as cmds
import caUtil
import re

class jbHashRename():
    def __init__(self,winName="HashRenamer", winTitle="Hash Renamer", w=300, h=24):
        self.winName = winName
        self.winTitle = winTitle

        if cmds.window(self.winName, exists=True):
            cmds.deleteUI(self.winName)

        self.winName = cmds.window(
            self.winName, 
            title=self.winTitle, 
            toolbox=True, 
            resizeToFitChildren=True)
        cmds.columnLayout( adjustableColumn=True)
        self.nameTextField = cmds.textFieldGrp(
            textChangedCommand=self.checkTextFieldInput,
            changeCommand=self.hashRenameSelection,
            adjustableColumn=1,
            annotation="'spine_##_jnt' will be renamed to\n'spine_01_jnt', 'spint_02_jnt'...", 
            placeholderText="Type and press Enter to rename.")
        cmds.showWindow( self.winName )
        cmds.window(self.winName, edit=True, widthHeight=[ w , h ])

    def hashRenameSelection(self,args=None):
        sel = cmds.ls(sl=True)
        if not sel:
            cmds.warning("Please select some objects to hash-rename.")
            return False

        name = cmds.textFieldGrp( self.nameTextField, q=True, text=True)
        if not name:
            cmds.warning("Please type a name - and don't forget the hash-character (#)!")
            return False

        caUtil.hashRename(name,sel)

    def checkTextFieldInput(self, args=None):
        t = cmds.textFieldGrp( self.nameTextField, q=True, text=True)
        if not re.match( '[a-zA-Z_0-9#]',t[-1:]):
            cmds.textFieldGrp( self.nameTextField, edit=True, text=t[:-1])