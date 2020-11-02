__author__ = 'Aksel Fleuriau-Moscoe'
import pymel.core as pmc
import maya.cmds as cmds
from qtshim import wrapinstance, QtGui
import maya.OpenMayaUI as OpenMayaUI


def get_maya_window():
    """Return the QMainWindow for the main Maya window"""

    winptr = OpenMayaUI.MQtUtil.mainWindow()
    if winptr is None:
        raise RuntimeError('No Maya window found.')
    window = wrapinstance(winptr)
    assert isinstance(window, QtGui.QMainWindow)
    return window


class undo_chunk(object):
    def __enter__(self):
        pmc.undoInfo(openChunk=True)

    def __exit__(self, *_):
        pmc.undoInfo(closeChunk=True)


class undo_on_error(object):
    def __enter__(self):
        pmc.undoInfo(openChunk=True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pmc.undoInfo(closeChunk=True)
        if exc_val is not None:
            pmc.undo()


class set_file_prompt(object):
    def __init__(self, state):
        self.state = state
        self.oldstate = None

    def __enter__(self):
        self.oldstate = cmds.file(q=True, prompt=True)
        cmds.file(prompt=self.state)

    def __exit__(self, *_):
        if self.oldstate is not None:
            cmds.file(prompt=self.oldstate)


class at_time(object):
    def __init__(self, t):
        self.t = t
        self.oldt = None

    def __enter__(self):
        self.oldt = pmc.getCurrentTime()
        pmc.setCurrentTime(self.t)

    def __exit__(self, *_):
        if self.oldt is not None:
            pmc.setCurrentTime(self.oldt)


class with_unit(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.oldlin, self.oldang, self.oldtim = None, None, None

    def __enter__(self):
        self.oldlin = pmc.currentUnit(q=True, linear=True)
        self.oldang = pmc.currentUnit(q=True, angle=True)
        self.oldtim = pmc.currentUnit(q=True, time=True)
        pmc.currentUnit(*self.args, **self.kwargs)

    def __exit__(self, *_):
        if self.oldlin is not None:
            pmc.currentUnit(linear=self.oldlin)
        if self.oldang is not None:
            pmc.currentUnit(angle=self.oldang)
        if self.oldtim is not None:
            pmc.currentUnit(time=self.oldtim)


class render_layer_active(object):
    def __init__(self, renderlayer):
        self.renderlayer = renderlayer
        self.orig_layer = None

    def __enter__(self):
        self.orig_layer = pmc.nodetypes.RenderLayer.currentLayer()
        self.renderlayer.setCurrent()

    def __exit__(self, *_):
        if self.orig_layer is not None:
            self.orig_layer.setCurrent()


class set_namespace_active(object):
    def __init__(self, ns):
        if ns == '':
            raise ValueError('argument cannot be an empty string')
        self.ns = ns
        self.oldns = None

    def __enter__(self):
        self.oldns = pmc.namespaceInfo(curreentNamespace=True)
        pmc.namespace(setNamespace=self.ns)

    def __exit__(self, *_):
        if self.oldns is not None:
            oldns = ':' + self.oldns.lstrip(':')
            pmc.namespace(setNamespace=oldns)