import pymel.core as pc
from cg.mocap.parsers import csmParser, c3dParser
import cg.maya.mocap.utils as mcutil


class OpticalSegmentImporter:
    def __init__(self):
        self.importTypeOptions = [
            {'label': 'Locators', 'f': pc.spaceLocator, 'kwargs': {}},
            {'label': 'Cubes', 'f': pc.polyCube, 'kwargs': {'ch': False}},
            {'label': 'Spheres', 'f': pc.polySphere, 'kwargs': {'sa': 8, 'sh': 6, 'ch': False}},
            {'label': 'Nulls (Empty Transforms)', 'f': pc.group, 'kwargs': {'empty': True}},
        ]
        self.fpsMap = {'game': 15, 'film': 24, 'pal': 25, 'ntsc': 30,
                       'show': 48, 'palf': 50, 'ntscf': 60}
        self.take = None
        self.gui()

    def gui(self):
        if pc.window("opticalsImportWindow", exists=True):
            pc.deleteUI("opticalsImportWindow")

        with pc.window("opticalsImportWindow", title="Import MoCap Markers", widthHeight=[300, 300]):
            with pc.columnLayout(adjustableColumn=True, rs=6):
                with pc.frameLayout(label='File (CSM or C3D)'):
                    self.filenameTextFieldButtonGrp = pc.textFieldButtonGrp(
                        text='', buttonLabel='Select',
                        bc=pc.Callback(self.getFilename), cw2=[250, 60]
                    )
                with pc.frameLayout(label='Options', marginHeight=5, marginWidth=5):
                    with pc.columnLayout():
                        self.frameLoadOptionsRadioCollection = pc.radioCollection()
                        self.oneSamplePerFrameRBtn = pc.radioButton(
                            label='Load 1 sample per frame'
                        )
                        self.loadRealtimeRBtn = pc.radioButton(
                            label='Load as "Realtime"', select=True
                        )
                        pc.separator(h=10)
                        helptext = "If you select objects (or a group containing objects) which match\nthe names of the markers in the mocap file, the keyframes will be\nput on these objects.\n\nOtherwise new Objects of this type  will be created."
                        self.importTypeOptionMenu = pc.optionMenu(label='Create new as', ann=helptext)
                        for option in self.importTypeOptions:
                            pc.menuItem(label=option['label'])
                        # pc.separator(h=10)
                        # self.groupMarkersCheckbox = pc.checkBox(
                        #     label='Group created objects', value=True
                        # )
                with pc.frameLayout(label='File and import info', marginHeight=5, height=50):
                    self.metadataText = pc.text(
                        label='No file selected', align='center', height=20, ww=True
                    )

                self.readObjectsButton = pc.button(label='Import', c=pc.Callback(self.importData))

    def getFilename(self):
        self.filepath = pc.fileDialog2(fileFilter="*.csm *.c3d", fm=1, dialogStyle=2)
        if self.filepath:
            pc.textFieldButtonGrp(self.filenameTextFieldButtonGrp, edit=True, text=self.filepath[0])
            fileExtension = self.filepath[0][-3:].lower()
            if fileExtension not in ["csm", "c3d"]:
                infoString = "Fileformat not supported."
            else:
                if fileExtension == "csm":
                    self.take = csmParser(self.filepath[0])
                elif fileExtension == "c3d":
                    self.take = c3dParser(self.filepath[0])
                infoString = "{0} Markers, {1} Frames, {2} fps, Actor: {3}".format(
                    len(self.take.segments), self.take.length,
                    self.take.rate, self.take.actor
                )
            pc.text(self.metadataText, edit=True, label=infoString)

    def importData(self):
        if not self.take:
            pc.warning("Please choose a CSM or C3D file.")
            return

        fps = self.take.rate
        if pc.radioButton(self.loadRealtimeRBtn, q=True, select=True):
            fps = self.fpsMap[pc.currentUnit(q=True, t=True)]
        pyNodes = mcutil.createAnimCurvesFromOptical(self.take, fps)

        importTo = pc.optionMenu(self.importTypeOptionMenu, q=True, select=True)
        createOption = self.importTypeOptions[importTo - 1]

        objectDict = {}
        sel = pc.ls(sl=True)
        if sel:  # something selected
            children = sel[0].getChildren()
            if children:
                if children[0].type() == "transform":  # group selected
                    objectDict = {
                        obj.name(long=None): obj for obj in children if obj.name(long=None) in pyNodes.keys()
                    }
                elif children[0].type() in ["mesh", "locator"]:  # single objects
                    objectDict = {
                        obj.name(long=None): obj for obj in sel if obj.name(long=None) in pyNodes.keys()
                    }
            else:
                pc.warning("An empty node is selected. Nothing imported.")
                return
        else:  # nothing selected -> create new objects
            for markername in pyNodes.keys():
                obj = createOption["f"](n=markername, **createOption["kwargs"])
                if type(obj) is list:
                    obj = obj[0]
                objectDict[markername] = obj
            pc.group(objectDict.values(), n=self.take.takename or "opticals_grp")

        axes = ["x", "z", "y"]

        for markername, obj in objectDict.items():
            for i, animnode in enumerate(pyNodes[markername]):
                pc.delete(pc.listConnections("{}.t{}".format(obj, axes[i]), s=True, d=False))
                animnode.output >> "{}.t{}".format(obj, axes[i])
        