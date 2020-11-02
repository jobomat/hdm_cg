#coding: utf8 
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
from functools import partial
from random import randrange

class JbMirrorShape():

    def __init__(self, winName="mirrorShapeWindow"):
        self.mirroraxis = 0
        self.axis2 = 1
        self.axis3 = 2
        self.axismult = [-1,1,1]
        self.threshold = 0.01
        self.vertex_list = []
        self.zero_list = []
        self.vertex_pair_list = []
        self.vertex_pair_list_flat = []
        self.instance = self
        self.winName = winName
        self.winTitle = "Mirror Symmetric Shapes"
        self.basemesh = ''

        self.showWindow()
 
    def buildVertexpairList(self,args):
        obj = cmds.ls(sl=True)
        if obj:
            self.fillVertexAndZeroList()
            self.basemesh = obj[0]
        else:
            cmds.warning("Nothing selected!")
            return False   
        # sort vtxlist by axis defined in "mirroraxis"
        self.vertex_list = sorted(self.vertex_list, key = lambda v: ( v["coords"][self.mirroraxis],v["coords"][self.axis2],v["coords"][self.axis3] ))
        # cut in half
        vertex_count = len(self.vertex_list)
        neg_list = self.vertex_list[:vertex_count/2]
        pos_list = self.vertex_list[vertex_count/2:]
        # sort the two lists first by the "not" mirroraxis then by the mirroraxis
        # this ensures a high number of first hits in the following for-loop
        pos_list = sorted(pos_list, key = lambda v: ( v["coords"][self.axis2],v["coords"][self.axis3] ) )
        pos_list.sort(key = lambda v: v["coords"][self.mirroraxis]  ,reverse=True )

        # run through the pos_list and check the first elements of the two lists on symmetry
        self.vertex_pair_list = []
        for i in range(0,vertex_count/2):
            v1 = neg_list.pop(0)
            v2 = pos_list.pop(0)
            match = self.distance_under_threshold(v1["coords"],v2["coords"])
            # if every coordinate matches up append the vertices to the list
            if match:
                self.vertex_pair_list.append([v1,v2])
                self.vertex_pair_list_flat.extend([v1,v2])
            # if not check members of the pos_list against the neg_list[0] member until a match was found
            # the match will usually be one of the first elements in the list 
            else:
                pos_list.insert(0,v2)
                i = 1
                match = False
                while not match and i < len(pos_list):
                    match = self.distance_under_threshold(v1["coords"],pos_list[i]["coords"])
                    if match:
                        v2 = pos_list.pop(i)
                        self.vertex_pair_list.append([v1,v2])
                        self.vertex_pair_list_flat.extend([v1,v2])
                    i += 1
                # if after the check of each po_list-vertex still no match was found attach the vertex back
                if not match:
                    neg_list.append(v1)
        cmds.frameLayout(self.check_framelayout, edit=True, enable=True)
        cmds.frameLayout(self.actions_framelayout, edit=True, enable=True)
        cmds.text(self.currentBase_text, edit=True, label=("Basemesh: %s" % self.basemesh))

    def distance_under_threshold(self,p1,p2):
        d1 = max(p1[self.axis2],p2[self.axis2]) - min(p1[self.axis2],p2[self.axis2])
        d2 = max(p1[self.axis3],p2[self.axis3]) - min(p1[self.axis3],p2[self.axis3])
        return ( d1 < self.threshold and d2 < self.threshold )
 
    def fillVertexAndZeroList(self):
        self.threshold = cmds.floatFieldGrp(self.threshold_floatfield, q=True, value1=True)
        # get the active selection
        selection = OpenMaya.MSelectionList()
        OpenMaya.MGlobal.getActiveSelectionList( selection )
        iterSel = OpenMaya.MItSelectionList(selection, OpenMaya.MFn.kMesh)
     
        # go througt selection
        while not iterSel.isDone():
            # get dagPath
            dagPath = OpenMaya.MDagPath()
            iterSel.getDagPath( dagPath )
            # create empty point array
            inMeshMPointArray = OpenMaya.MPointArray()
            # create function set and get points in world space
            currentInMeshMFnMesh = OpenMaya.MFnMesh(dagPath)
            currentInMeshMFnMesh.getPoints(inMeshMPointArray, OpenMaya.MSpace.kObject)
            # put each point to the correct list
            self.vertex_list = []
            self.zero_list = []
     
            for i in range( inMeshMPointArray.length() ) :
                if abs(inMeshMPointArray[i][self.mirroraxis]) > self.threshold:
                    self.vertex_list.append( { "vtx": i, "coords": [ inMeshMPointArray[i][0], inMeshMPointArray[i][1], inMeshMPointArray[i][2] ] } )
                else:
                    self.zero_list.append( { "vtx": i, "coords": [ inMeshMPointArray[i][0], inMeshMPointArray[i][1], inMeshMPointArray[i][2] ] } )
            return True

    def getAllVertexPositions(self):
        # get the active selection
        selection = OpenMaya.MSelectionList()
        OpenMaya.MGlobal.getActiveSelectionList( selection )
        iterSel = OpenMaya.MItSelectionList(selection, OpenMaya.MFn.kMesh)
     
        # go througt selection
        while not iterSel.isDone():
            # get dagPath
            dagPath = OpenMaya.MDagPath()
            iterSel.getDagPath( dagPath )
            # create empty point array
            inMeshMPointArray = OpenMaya.MPointArray()
            # create function set and get points in world space
            currentInMeshMFnMesh = OpenMaya.MFnMesh(dagPath)
            currentInMeshMFnMesh.getPoints(inMeshMPointArray, OpenMaya.MSpace.kObject)
            # put each point to the correct list
            point_list = []
     
            for i in range( inMeshMPointArray.length() ) :
                point_list.append([ inMeshMPointArray[i][0], inMeshMPointArray[i][1], inMeshMPointArray[i][2] ]  )
            return point_list
    
    def mirror_vertex_positions(self, dir='flip', args=None):
        # get the active selection
        sel = cmds.ls(sl=True)
        
        if sel:
            selection = OpenMaya.MSelectionList()
            OpenMaya.MGlobal.getActiveSelectionList( selection )
            iterSel = OpenMaya.MItSelectionList(selection, OpenMaya.MFn.kMesh)
         
            # go througt selection
            while not iterSel.isDone():
                # get dagPath
                dagPath = OpenMaya.MDagPath()
                iterSel.getDagPath( dagPath )
                # create empty point array
                inMeshMPointArray = OpenMaya.MPointArray()
            
                # create function set and get points in world space
                currentInMeshMFnMesh = OpenMaya.MFnMesh(dagPath)
                currentInMeshMFnMesh.getPoints(inMeshMPointArray, OpenMaya.MSpace.kObject)
                outMeshMPointArray = OpenMaya.MPointArray(inMeshMPointArray)

                for pair in self.vertex_pair_list:
                    point0=outMeshMPointArray[pair[0]["vtx"]]
                    point1=outMeshMPointArray[pair[1]["vtx"]]
                    if dir!='neg_to_pos':
                        point0.x=self.axismult[0]*inMeshMPointArray[pair[1]["vtx"]].x
                        point0.y=self.axismult[1]*inMeshMPointArray[pair[1]["vtx"]].y
                        point0.z=self.axismult[2]*inMeshMPointArray[pair[1]["vtx"]].z
                    if dir != 'pos_to_neg':
                        point1.x=self.axismult[0]*inMeshMPointArray[pair[0]["vtx"]].x
                        point1.y=self.axismult[1]*inMeshMPointArray[pair[0]["vtx"]].y
                        point1.z=self.axismult[2]*inMeshMPointArray[pair[0]["vtx"]].z

                    #currentInMeshMFnMesh.setPoint(pair[0]["vtx"],OpenMaya.MPoint(*p1),OpenMaya.MSpace.kWorld)
                currentInMeshMFnMesh.setPoints(outMeshMPointArray,OpenMaya.MSpace.kObject)
                iterSel.next()

        else:
            cmds.warning("Nothing selected!")
            return False

    def cmdTest(self):
        # get the active selection
        global test
        sel = cmds.ls(sl=True)
        obj = sel[0]
        if obj:
            test = self.vertex_pair_list
            cmds.jb_mirrorshape()

        else:
            cmds.warning("Nothing selected!")
            return False

    def setMirrorAxis(self,a1,args):
        cmds.frameLayout(self.check_framelayout, edit=True, enable=False)
        cmds.frameLayout(self.actions_framelayout, edit=True, enable=False)
        cmds.text(self.currentBase_text, edit=True, label=("Axis changed: Reread Basemesh!"))
        if a1==1:
            self.mirroraxis = 0
            self.axis2 = 1
            self.axis3 = 2
            self.axismult = [-1,1,1]
        elif a1==2:
            self.mirroraxis = 1
            self.axis2 = 0
            self.axis3 = 2
            self.axismult = [1,-1,1]
        else:
            self.mirroraxis = 2
            self.axis2 = 1
            self.axis3 = 0
            self.axismult = [1,1,-1]

    def testVertexAssociation(self,testScheme,args):
        if testScheme=='zero':
            cmds.select(map(lambda x: ("%s.vtx[%s]") % (self.basemesh,x['vtx']), self.zero_list))
        if testScheme=='pos':
            cmds.select(map(lambda x: ("%s.vtx[%s]") % (self.basemesh,x[1]['vtx']), self.vertex_pair_list))
        if testScheme=='neg':
            cmds.select(map(lambda x: ("%s.vtx[%s]") % (self.basemesh,x[0]['vtx']), self.vertex_pair_list))
        if testScheme=='probe':
            cmds.select(map(lambda x: ("%s.vtx[%s]") % (self.basemesh,x['vtx']), self.vertex_pair_list[randrange(len(self.vertex_pair_list))]))

    def showWindow(self):
        if cmds.window(self.winName, exists=True):
            cmds.deleteUI(self.winName)

        cmds.window(self.winName, title=self.winTitle)
        cmds.columnLayout( adjustableColumn=True )
        cmds.frameLayout( label='Setup', borderStyle='in', collapsable=True, mh=2, mw=2)
        cmds.columnLayout(rowSpacing=2)
        self.mirroraxis_checkbox = cmds.radioButtonGrp( 
            label='Mirror Axis: ',labelArray3=['x', 'y', 'z'], 
            select=1, numberOfRadioButtons=3, columnWidth4= [70,28,28,28],
            onCommand1=partial(self.setMirrorAxis,1),
            onCommand2=partial(self.setMirrorAxis,2),
            onCommand3=partial(self.setMirrorAxis,3)
            )
        self.threshold_floatfield = cmds.floatFieldGrp( numberOfFields=1, label='Threshold: ', value1=0.001, precision=4, columnWidth2= [70,90])
        cmds.button(label='Read Basemesh Symmetry', c=self.buildVertexpairList, w=165)
        cmds.setParent( '..' ) #endCol
        cmds.setParent( '..' ) #endFrame
        self.check_framelayout = cmds.frameLayout( label='Test Vertex Association', borderStyle='in', enable=(True if self.basemesh else False), collapsable=True, mh=2, mw=2 )
        cmds.rowColumnLayout( numberOfColumns=4, columnSpacing=([2,2],[3,2],[4,2]) )
        cmds.button(label='Zero', c=partial(self.testVertexAssociation,'zero'), h=20, w=39)
        cmds.button(label='Neg', c=partial(self.testVertexAssociation,'neg'), h=20, w=39)
        cmds.button(label='Pos', c=partial(self.testVertexAssociation,'pos'), h=20, w=39)
        cmds.button(label='Probe', c=partial(self.testVertexAssociation,'probe'), h=20, w=39)
        cmds.setParent( '..' ) #endCol
        cmds.setParent( '..' ) #endFrame
        self.actions_framelayout = cmds.frameLayout( label='Actions', enable=(True if self.basemesh else False), borderStyle='in', mh=2, mw=2 )
        cmds.columnLayout(rowSpacing=2)
        self.currentBase_text = cmds.text( label=(' Basemesh: %s' % self.basemesh), align='left' )
        cmds.button(label='Flip Vertices', w=165, c=self.mirror_vertex_positions)
        cmds.rowColumnLayout( numberOfColumns=3, columnSpacing=[3,2])
        cmds.text( label='Copy:', align='left', w = 32 )
        cmds.button(label='Pos to Neg', c=partial(self.mirror_vertex_positions,'pos_to_neg'), w = 65 )
        cmds.button(label='Neg to Pos', c=partial(self.mirror_vertex_positions,'neg_to_pos'), w = 65 )
        cmds.setParent( '..' ) #endCol
        cmds.setParent( '..' ) #endFrame
        #cmds.setParent( '..' ) #mainCol
        #self.progressControl = cmds.progressBar(maxValue=10, w=165) 
        #cmds.button( label='Make Progress!', command='cmds.progressBar(progressControl, edit=True, step=1)' )

        cmds.showWindow(self.winName)

# todo:
# - undo lösung
# - copy pos or neg basemesh verts to selected shape
# - icons?
# - additional checks while reading sym (true/false check after first sort)