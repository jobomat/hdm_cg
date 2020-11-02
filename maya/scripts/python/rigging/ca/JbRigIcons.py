#coding: utf8 
import maya.cmds as cmds
import maya
import maya.mel as mel
from functools import partial
import caUtil 
import glob
import re
import json
import os

class JbRigIcons():
	def __init__(self, 
	winName="rigIconsWindow", 
	thumbnailSize=[40,40], 
	gridNewlineAfter=8,
	directory='', 
	excludeList=None,
	postfixes={"ctrl":"_ctrl","null":"_null","offset":"_offset"},
	colorIndizes=[1,4,5,6,7,9,10,12,13,15,16,17,18,22,23]):
		self.winTitle = "Create Rig Icons"
		self.winName = winName
		self.curveName = ""
		self.thumbnailSize = thumbnailSize
		self.gridNewlineAfter = gridNewlineAfter
		self.btnIconList = []
		self.colorBtnList = []
		self.nameTextFieldGrp = None
		self.directory = directory if directory!='' else (os.path.abspath(os.path.dirname(__file__))+'/rigIcons/')
		self.excludeList = excludeList
		self.postfixDict = postfixes
		self.colorIndizes = colorIndizes
		self.colors = []
		self.color = None
		self.createdControls = []
		self.nameList = []
		for index in self.colorIndizes:
			self.colors.append( cmds.colorIndex( index, q=True ) )

		self.readRiFiles()

	def readRiFiles(self, args=None):
		self.btnIconList = []
		#	alle .ri-filenamen aus dem directory abfragen
		iconDirList = glob.glob(self.directory+'*.ri')
		#	liest alle ri-files in die btnIconList
		for riFile in iconDirList:
			with open(riFile.replace("\\","/")) as f:
				lines = f.read().splitlines()
				self.btnIconList.append( {"label": lines[0], "filename" : riFile[len(self.directory):-3], "command" : json.loads(lines[2]), "pos": lines[3], "btn": None} )		
		self.btnIconList.sort( key=lambda x: int(x['pos']), reverse=False )
		for i,btn in enumerate(self.btnIconList):
			btn['pos'] = str(i+1)
			self.writeRiFile(btn)

	def create(self):
		if cmds.window(self.winName, exists=True):
			cmds.deleteUI(self.winName)

		cmds.window(self.winName, title=self.winTitle, menuBar=True, toolbox=True, resizeToFitChildren=True)
		cmds.menu( label="File", tearOff=True )
		cmds.menuItem(label='Reread RigIcon-directory', c=self.rereadDir)
		cmds.setParent('..')
		cmds.menu( label="Edit", tearOff=True )
		cmds.menuItem(label='Save selected curve as new icon...', c=self.addIcon)
		cmds.menuItem(label='Select last created elements', c=self.selectLastCreated)
		cmds.setParent('..')
		self.mainCol	= cmds.columnLayout( adjustableColumn=True)
		cmds.separator()
		self.iconGrid   = cmds.gridLayout(numberOfColumns=self.gridNewlineAfter, cellWidthHeight = [ (self.thumbnailSize[0]+2), (self.thumbnailSize[1]) ] )
		#	baut für alle btnIconList-einträge ein iconTextButton mit rechstklickmenü
		for iconBtn in self.btnIconList:
			iconBtn["btn"] = self.createIconButton(blItem=iconBtn)
		cmds.setParent(self.mainCol)
		cmds.separator(h=10)
		self.editRow = cmds.rowLayout(numberOfColumns=7)
		cmds.text(label=" Rotate by ")
		self.rotDegree = cmds.intField( w=25, h=20, minValue=-180, maxValue=180, value=90 )
		cmds.text(label=" in ")
		cmds.button(w=20, h=20, label="x", c=partial(self.rotateMethod,"x"))
		cmds.button(w=20, h=20, label="y", c=partial(self.rotateMethod,"y"))
		cmds.button(w=20, h=20, label="z", c=partial(self.rotateMethod,"z"))
		self.scaleSlider = cmds.floatSliderGrp( label="Scale", field=True, cw3=[35,30,90], minValue=0.1, maxValue=3.0, value=1.0, dc=self.scaleMethod, cc=self.postScaleMethod )
		cmds.setParent('..')
		cmds.separator(h=10)
		self.nameTextFieldGrp = cmds.textFieldGrp(label='Name (optional):', textChangedCommand=self.checkTextFieldInput, cw2=[83,242],annotation="If left blank, name of selected object OR default name will be used.\n To see the default name, hover above the RigIcon-button.\nRightclick for Name-History.", placeholderText="Leave blank for selected object- or defaultname")
		self.nameHistoryPopup = cmds.popupMenu()
		cmds.separator(h=10)
		cmds.rowLayout(numberOfColumns=len(self.colorIndizes))
		for i,index in enumerate(self.colorIndizes):
			self.colorBtnList.append( cmds.iconTextButton(backgroundColor=self.colors[i], h=20, w=20, c=partial(self.colorizeSelectedCurves,i)) )
			cmds.popupMenu()
			cmds.menuItem(label="Std (Toggle)", c=partial(self.setColor, i) )
			
		# cmds.button(label="Save Selected Curve",)
		cmds.showWindow( self.winName )
		self.adjustButtonPanelHeight()

	def adjustButtonPanelHeight(self):
		heightMultiplier = int(len(self.btnIconList) / self.gridNewlineAfter)
		if not (int(len(self.btnIconList) % self.gridNewlineAfter) ):
			heightMultiplier -= 1
		h = heightMultiplier * self.thumbnailSize[0] + 166
		w = (self.gridNewlineAfter*(self.thumbnailSize[0]+2)) + 2
		cmds.window(self.winName, edit=True, widthHeight=[ w , h ])

	def createIconButton(self, blItem, btn=None):
		pathAndFile = (self.directory+blItem['filename']+".bmp")
		i = int(blItem['pos'])-1
		if not caUtil.fileExists(pathAndFile):
			pathAndFile = (self.directory+"temp.bmp")
		edit = False
		if btn==None:
			cmds.setParent(self.iconGrid)
		else:
			edit = True
		button = cmds.iconTextButton( btn, edit=edit,
		style="iconOnly", ann=(blItem['label']+"\nRightclick for Options"),
		image1=pathAndFile,
		flat=1, width=self.thumbnailSize[0], height=self.thumbnailSize[1], 
		c=partial(self.createRigIcon, i, 1),
		dragCallback=self.dragCallback,
		dropCallback=self.dropCallbackSwap )
		if btn==None:
			cmds.popupMenu()
			cmds.menuItem(label="Create Solo at Object(s)", c=partial( self.createRigIcon,i, 0 ) )
			cmds.menuItem(d=True)
			cmds.menuItem(label="Take Thumbnail Screenshot", c=partial( self.iconScreenshot, i) )
			cmds.setParent('..')
			return button
		return None

	
	def changeIcon(self, buttonToChange, curveColor, viewportColor, lineWidth, args=None):
		cmds.iconTextButton( self.btnIconList[buttonToChange]["btn"], edit=True, image1=(self.directory+"temp.bmp") ) 
		cmds.iconTextButton( self.btnIconList[buttonToChange]["btn"], edit=True, image1=(self.directory+self.btnIconList[buttonToChange]["filename"]+".bmp"))
		cmds.displayColor( 'curve', curveColor, active=False, dormant=True )
		cmds.displayRGBColor( viewportColor[0], float(viewportColor[1]), float(viewportColor[2]), float(viewportColor[3]) )
		cmds.modelEditor( modelPanel='modelPanel4' , lineWidth=lineWidth)

	def addIcon(self, args=None):
		sel = cmds.ls(sl=True)
		#	Tests:
		#	Ist überhaupt was selektiert?
		if not sel or len(sel) > 1:
			cmds.confirmDialog(message="Please select something to Save!", button=["OK"], p=self.winName)
			return
		shapes = caUtil.getShapes(sel[0])
		#	Hat das Objekt mehr als eine Shape?
		# if len(shapes) > 1:
		#	cmds.confirmDialog(message=sel[0]+" seems to have more than one Shape... \nCan't handle that in this Version. Sorry!", button=["OK"], p=self.winName)
		#	return
		#	Ist das Objekt eine Nurbs Kurve?
		# if cmds.ls(shapes[0],st=1)[1].encode('ascii','ignore') != "nurbsCurve":
		#	cmds.confirmDialog(message="Object must be of type 'nurbsCurve'!", button=["OK"], p=self.winName)
		#	return

		curve = sel[0]
		result = cmds.promptDialog( title='Icon Name', message='Enter Name:', text=curve, button=['OK', 'Cancel'], defaultButton='OK', cancelButton='Cancel', dismissString='Cancel')

		if result == 'OK':
			iconName = cmds.promptDialog(q=True, text=True)
			#	hier evtl rückgabewert aus funktion, die böse zeichen 
			#	abcheckt, whitespaces durch unterstriche ersetzt usw
			saveName = self.getSaveName(iconName) 
			rigElement = self.getRigList(curve)
			self.btnIconList.append({"label": iconName, "filename": saveName, "command": rigElement, "btn": None, "pos": (len(self.btnIconList)+1)})
			self.btnIconList[len(self.btnIconList)-1]["btn"] = self.createIconButton( blItem=self.btnIconList[len(self.btnIconList)-1] )
			self.iconScreenshot(buttonToChange=(len(self.btnIconList) - 1))
			self.writeRiFile(riDict=self.btnIconList[len(self.btnIconList)-1])
			h = (int(len(self.btnIconList) / self.gridNewlineAfter) ) * self.thumbnailSize[0] + 92
			cmds.window(self.winName, edit=True, h=h )

	def iconScreenshot(self, buttonToChange, args=None):
		curveColor = cmds.displayColor( 'curve', q=True, active=False, dormant=True )
		cmds.displayColor( 'curve', 16, active=False, dormant=True )
		viewportColor = cmds.displayRGBColor( list=True )[0].split()
		cmds.displayRGBColor( 'background', .261, .261, .261 )
		lineWidth = cmds.optionVar(q="lineWidth")
		cmds.modelEditor( modelPanel='modelPanel4' , lineWidth=5.0)
		caUtil.ViewportScreenshot(path=self.directory, imagesize=self.thumbnailSize, filename=self.btnIconList[buttonToChange]['filename'], fileformat='bmp', onComplete=partial(self.changeIcon, buttonToChange, curveColor, viewportColor, lineWidth) )
	
	def getSaveName(self,name):
		# prüfung auf sonder- und leerzeichen
		name = re.sub('[^A-Za-z0-9_]+', '', name.replace(" ","_"))
		# prüfung auf existenz des namens in der liste und im verzeichnis
		while caUtil.fileExists(self.directory+name+".ri"):
			nameList = name.split("_")
			lastElement = nameList[-1]
			# schauen, ob letztes element eine zahl ist
			# wenn ja: zahl erhöhen
			if str.isdigit(lastElement.encode('ascii','ignore')):
				nameList[-1] = str(int(lastElement)+1)
			# wenn nein: eine 1 anhängen
			else:
				nameList.append("1")
			# neuen namen zusammenbauen
			name = "_".join(nameList)
		return name

	# createRigIcon
	def createRigIcon(self, i, withGroup, args=None):
		self.createdControls = []
		selectedObjects = cmds.ls(sl=True)
		nameField = cmds.textFieldGrp(self.nameTextFieldGrp,query=True, text=True)
	
		if selectedObjects:
			for obj in selectedObjects:
				cons = ""
				n = nameField if nameField else obj
				element = self.reconstructRigElement(self.btnIconList[i]['command'], n)
				curveName = element
				if withGroup:
					offsetGrp = caUtil.addGroupWithTransforms(curveName, curveName+self.postfixDict['offset'])
					nullGrp = caUtil.addGroupWithTransforms(offsetGrp, curveName+self.postfixDict['null'])
					cons = cmds.parentConstraint(obj,nullGrp)
				else:
					cons = cmds.parentConstraint(obj,curveName)
				cmds.delete(cons)
				#createdControls.append(curveName)
		else:
			n = nameField if nameField else self.getCurveName(self.btnIconList[i]['label'])
			element = self.reconstructRigElement(self.btnIconList[i]['command'], n)
			curveName = element
			# createdControls.append(curveName)
			if withGroup:
				offsetGrp =caUtil.addGroupWithTransforms(curveName, curveName+self.postfixDict['offset'])
				nullGrp = caUtil.addGroupWithTransforms(offsetGrp, curveName+self.postfixDict['null'])
		cmds.select(self.createdControls)
		if self.color:
			self.colorizeSelectedCurves(self.color)
		if nameField:
			if cmds.popupMenu(self.nameHistoryPopup, query=True, numberOfItems=True):
				cmds.menuItem(parent=self.nameHistoryPopup, label=nameField, insertAfter="", c=partial( self.chooseNameHistoryItem, nameField))
			else:
				cmds.menuItem(parent=self.nameHistoryPopup, label=nameField, c=partial( self.chooseNameHistoryItem, nameField))
			# self.nameList.append(nameField)
		cmds.textFieldGrp(self.nameTextFieldGrp, edit=True, text="")

	def reconstructRigElement(self,liste,name,parent=None):
		import maya
		g=""
		for element in liste:
			if element['type'] == "nurbsCurve":
				crv = eval(element['cmd'])
				s = caUtil.getShapes(crv)[0]
				cmds.parent(s,parent,shape=True,add=True)
				cmds.delete(crv)
			else:
				g = cmds.group(em=True)
				try:
					cmds.xform( g, rp=element['pivot'] )
					cmds.xform( g, sp=element['pivot'] )
				except:
					pass
				n = name
				if n==None:
					n = element['name']
				g = cmds.rename(g,self.getCurveName(n+self.postfixDict['ctrl']))
				self.createdControls.append(g)
				if parent:
					cmds.parent(g,parent)
				self.reconstructRigElement(element['childs'],None,g)
		return g		

	def getCurveName(self, name, args=None):
		# hier noch textfeld abfragen, sonst Name des selektierten Objekts...
		# print name
		while cmds.objExists(name):
			nameList = name.split("_")
			lastElement = nameList[-1]
			lastElement = lastElement.encode('ascii','ignore')
			# schauen, ob letztes element eine zahl ist
			# wenn ja: zahl erhöhen
			if str.isdigit(lastElement):
				nameList[-1] = str(int(lastElement)+1)
			# wenn nein: eine 1 anhängen
			else:
				nameList.append("1")
			# neuen namen zusammenbauen
			name = "_".join(nameList)
		return name

	def scaleMethod(self, args=None):
		v = cmds.floatSliderGrp(self.scaleSlider, q=True, v=True)
		cmds.scale(v,v,v)

	def postScaleMethod(self, args=None):
		cmds.makeIdentity(apply=True,t=0,r=0,s=1,n=0)
		cmds.floatSliderGrp(self.scaleSlider, edit=True, v=1.0)

	def rotateMethod(self, axes, args=None):
		assert axes in ['x','y','z'], "Parameter 'axes' of RotateMethod must be 'x', 'y', or 'z'"
		cmds.symmetricModelling(e=True, symmetry=False)
		sel = cmds.ls(sl=True)
		betrag = cmds.intField(self.rotDegree, q=True, value=True)
		if betrag == "":
			betrag = 90
		if not sel:
			cmds.warning("Select at least one object to rotate it's shape!")
			return
		for obj in sel:
			cmds.select(obj, r=True)
			pivot = cmds.xform(q=True, ws=True, rp=True)
			try:
				cmds.select(obj+".cv[0:]")
				mult = {'x': [betrag,0,0], 'y': [0,betrag,0], 'z':[0,0,betrag]}
				cmds.rotate( *mult[axes], r=True, os=True, eu=True, p=pivot )
			except:
				pass
			
		cmds.select(sel)

	def colorizeSelectedCurves(self, i, args=None):
		sel = cmds.ls(sl=True)
		for obj in sel:
			shapes = caUtil.getShapes(obj)
			if shapes:
				for s in shapes:
					cmds.setAttr( s+'.overrideEnabled', True)
					cmds.setAttr( s+'.overrideColor', self.colorIndizes[i] )

	def setColor(self, i, args=None):
		if self.color is not None:
			cmds.iconTextButton(self.colorBtnList[self.color], edit=True, style="iconOnly")
		if self.color == i:
			self.color = None
		else:
			self.color=i
			cmds.iconTextButton(self.colorBtnList[i], edit=True, style="iconAndTextHorizontal", label="*", font="smallBoldLabelFont")

	def getRigList(self,name):
		return self.buildRigCurveHirarchy( caUtil.listHirarchy(name) )

	def buildRigCurveHirarchy(self, node):
		newHir = []
		pivot = None
		for element in node:
			cmdString = ""
			if element['type'] == 'nurbsCurve':
				cmdString = self.reEngineerCurve(element['name'])
			else:
				pivot = cmds.xform(element['name'],q=True, ws=True, rp=True)
				
			newHir.append({'name':element['name'], 'type':element['type'], 'cmd':cmdString, 'pivot':pivot, 'childs': self.buildRigCurveHirarchy(element['childs'])})
		return newHir

	#	reEngineerSelectedCurve
	#	gibt das python-kommando zurück, um exakt die übergebene nurbs-kurve (shape-node!) nachzubauen.
	def reEngineerCurve(self, curveToReproduce):
		degree = cmds.getAttr(curveToReproduce + ".degree")

		infoNode = cmds.createNode("curveInfo")
		cmds.connectAttr( (curveToReproduce +".worldSpace") , (infoNode+".inputCurve") )
		knots = map(str,cmds.getAttr( infoNode+".knots")[0])

		cmds.delete(infoNode)

		cmds.select(curveToReproduce + ".cv[*]")
		curveCvs=cmds.ls(sl=True, fl=True)
		
		# für geschlossene curven werden die letzten x cvs wiederholt,
		# tauchen aber nicht in der curveCV liste auf. 
		# die info-node gibt die cv's nicht direkt preis, da es sich um 
		# mixedCompound Objects handelt. 
		# workaround im folgenden das manuelle anhängen...
		missingCVs = len(knots) - degree + 1 - len(curveCvs)
		for i in range(0,missingCVs):
			curveCvs.append(curveCvs[i])

		coords=[]
		for cv in curveCvs:
			coord = map(str,cmds.xform(cv,q=True,translation=True,ws=True))
			coords.append( "(" + ",".join(coord) + ")" )

		cmdString = "maya.cmds.curve( d=" + str(degree) + ", p=[" + ",".join(coords) + "], k=[" + ",".join(knots) + "] )"
		return cmdString
		
	def writeRiFile(self, riDict):
		riString = riDict['label']+'\n'+riDict['filename']+'\n'+json.dumps(riDict['command'])+'\n'+str(riDict['pos'])
		f = open( (self.directory+riDict['filename']+".ri"), 'w')
		f.write(riString)
		f.close()

	def dragCallback(self,*a):
		pass

	def dropCallbackSwap( self, *a ):
		fi = int( next((btn['pos'] for btn in self.btnIconList if btn['btn'] == a[0]), None) ) - 1
		ti = int( next((btn['pos'] for btn in self.btnIconList if btn['btn'] == a[1]), None) ) - 1
		
		if  fi != ti:
			#	pos und btn tauschen
			self.btnIconList[fi]['pos'] = str(ti+1)
			self.btnIconList[ti]['pos'] = str(fi+1)
			
			self.btnIconList[fi]['btn'], self.btnIconList[ti]['btn'] = self.btnIconList[ti]['btn'], self.btnIconList[fi]['btn']
			#	listenelemente tauschen
			self.btnIconList[fi], self.btnIconList[ti] = self.btnIconList[ti], self.btnIconList[fi]
			
			#	beide buttons updaten
			# print cmds.menuItem(cmds.popupMenu(cmds.iconTextButton(self.btnIconList[ti]['btn'],q=True,popupMenuArray=True)[0], query=True, itemArray=True)[0],q=True,cmd=True)
			self.createIconButton(self.btnIconList[ti], btn=self.btnIconList[ti]['btn'])
			self.createIconButton(self.btnIconList[fi], btn=self.btnIconList[fi]['btn'])
			#	jetzt noch ri-files updaten
			self.writeRiFile(self.btnIconList[ti])
			self.writeRiFile(self.btnIconList[fi])

	def rereadDir(self, args=None):
		for i,iconBtn in enumerate(self.btnIconList):
			cmds.deleteUI(iconBtn['btn'])
		del self.btnIconList[:]

		self.readRiFiles()
		for iconBtn in self.btnIconList:
			iconBtn["btn"] = self.createIconButton(blItem=iconBtn)
		self.adjustButtonPanelHeight()

	def selectLastCreated(self, args=None):
		if self.createdControls:
			cmds.select(self.createdControls)

	def checkTextFieldInput(self, args=None):
		t = cmds.textFieldGrp(self.nameTextFieldGrp, query=True, text=True)
		if not re.match( '[a-zA-Z_0-9]',t[-1:]):
			cmds.textFieldGrp(self.nameTextFieldGrp, edit=True, text=t[:-1])

	def chooseNameHistoryItem(self, n, args=None):
		cmds.textFieldGrp(self.nameTextFieldGrp, edit=True, text=n)

#	create the window
JbRigIcons().create()