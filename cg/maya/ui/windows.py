from collections import defaultdict
import pymel.core as pc


# window_map is a collection of maya window-names / ids 
window_map = {
    'Hypershade': 'hyperShadePanel1Window',
    'UV View': 'polyTexturePlacementPanel1Window',
    'Option Box Window': 'OptionBoxWindow',
    'Arnold Render View': 'ArnoldRenderView',
    'Connection Editor': 'connectWindow',
    'Node Editor': 'nodeEditorPanel1Window',
    'Tool Settings': 'ToolSettings',
    'Script Editor': 'scriptEditorPanel1Window',
    'Outliner': 'outlinerPanel1Window',
    'Hypergraph': 'hyperGraphPanel1Window',
    'Graph Editor': 'graphEditor1Window',
    'Time Editor': 'timeEditorPanel1Window',
    'Dope Sheet': 'dopeSheetPanel1Window',
    'Shape Editor': 'shapePanel1Window',
    'Pose Editor': 'posePanel1Window',
    'Clip Editor': 'clipEditorPanel1Window',
    'Blind Data Editor': 'blindDataEditor1Window',
    'Content Browser': 'contentBrowserPanel1Window',
    'Project Window': 'projectWindow',
    'Namespace Editor': 'namespaceEditor',
    'Preferences': 'PreferencesWindow',
    'Shelf Editor': 'shelfEditor',
    'Hotkey Editor': 'HotkeyEditor',
    'Boss Editor': 'BossEditorMainWindow',
    'About Arnold Window': 'AboutArnold',
    'Arnold Licence Window': 'ArnoldLicense',
    'Create Render Node Window': 'createRenderNodeWindow',
    'Expression Editor': 'expressionEditorWin',
    'Show Inputs Window': 'showHistoryWindow',
    'Set Driven Key Editor': 'setDrivenWnd',
    'Quick Rig Window': 'quickRigWindowId',
    'Plugin Manager': 'pluginManagerWindow',
}


def reposition(win_id, position=[0, 0]):
    try:
        pc.window(win_id, edit=True, iconify=False)
        pc.window(win_id, edit=True, topLeftCorner=position)
        return True
    except RuntimeError:
        return False


def gather(position=[0, 0], *args):
    repositioned = []
    skipped = []
    for nice_name, ui_name in window_map.items():
        if reposition(ui_name, position):
            repositioned.append(nice_name)
        else:
            skipped.append(nice_name)
    return reposition, skipped


def collect_info(*args):
    infos = defaultdict(dict)
    attributes = ['leftEdge', 'topEdge', 'width', 'height', 'iconify']
    for nice_name, ui_name in window_map.items():
        try:
            for attr in attributes:
                arg = {attr: True}
                infos[nice_name][attr] = pc.window(ui_name, q=True, **arg)
        except RuntimeError:
            pass
    return infos


def manager():
    with pc.window(title="Maya WinManager"):
        with pc.columnLayout():
            pc.button(label="Gather at [0,0]", c=pc.Callback(gather))


"""
import cg.maya.ui.windows as win
reload(win)

print win.collect_info()
win.reposition("Graph Editor")
"""