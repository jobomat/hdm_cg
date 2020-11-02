__author__ = 'Aksel Fleuriau-Moscoe'

try:
    from PySide import QtCore, QtGui
    import shiboken
    Signal = QtCore.Signal
    Slot = QtCore.Slot

    def _getcls(name):
        result = getattr(QtGui, name, None)
        if result is None:
            result = getattr(QtCore, name, None)
        return result

    def wrapinstance(ptr):
        """Convert a pointer (int or long) into the concrete
        PyQt/PySide object it represents."""
        ptr = long(ptr)
        qobj = shiboken.wrapInstance(ptr, QtCore.QObject)
        metaobj = qobj.metaObject()
        realcls = None
        while realcls is None:
            realcls = _getcls(metaobj.className())
            metaobj = metaobj.superClass()
        return shiboken.wrapInstance(ptr, realcls)

except ImportError:
    from PyQt4 import QtCore, QtGui
    Signal = QtCore.pyqtSignal
    slot = QtCore.pyqtSlot
    import sip

    def wrapinstance(ptr):
        return sip.wrapinstance(long(ptr), QtCore.QObject)