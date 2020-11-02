from PySide2 import QtWidgets


def qt_wrap(qt_widget_class, **kwargs):
    try:
        import maya.OpenMayaUI as omui
        import shiboken2
        import maya.app.general.mayaMixin as maya_mixin
        
        class WrappedQtItem(maya_mixin.MayaQWidgetDockableMixin, qt_widget_class):
            def __init__(self, parent=None):
                main_window_ptr = omui.MQtUtil.mainWindow()
                maya_win = shiboken2.wrapInstance(long(main_window_ptr), QtWidgets.QWidget)
                super(WrappedQtItem, self).__init__(maya_win)
        
        wrapped_item = WrappedQtItem()
        wrapped_item.show(**kwargs)
    
    except ImportError:
        app = QtWidgets.QApplication([])
        w = qt_widget_class()
        w.show()
        app.exec_()