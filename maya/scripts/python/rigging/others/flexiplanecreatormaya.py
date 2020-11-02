__author__ = 'Aksel'
import maya.OpenMaya as OpenMaya
import pymel.core as pmc
import flexiplanecreatorgui as flexgui
import mayautils
import flexiplanecreator as flexcr

_window = None


def show():
    """
    show flexiplane creator window
    """
    global _window
    if _window is None:
        cont = flexgui.FlexiCreatorController()

        def emit_sel_changed(_):
            """
            emits a signal from GUI controller every time
            the selection changes
            """
            # emits a signal with all 'transform' nodes currently selected
            cont.selectionChanged.emit(
                pmc.selected(type='transform')
            )
        OpenMaya.MEventMessage.addEventCallback(
            'SelectionChanged', emit_sel_changed
        )
        # grabs Maya main window
        parent = mayautils.get_maya_window()
        # calls GUI, sets the controller and parents it to Maya main window
        _window = flexgui.FlexiCreatorGui().create(cont, parent)

        def on_create(name):
            """
            calls create_flexiplane() when create button is clicked
            :param name: name to be added to flexiplane
            """

            # overrides name definition from settings to name in text box
            settings = dict(
                flexcr.SETTINGS_DEFAULT,
                prefix=unicode(name)
            )
            flexcr.build_flexiplane(settings)
        _window.createClicked.connect(on_create)
    _window.show()