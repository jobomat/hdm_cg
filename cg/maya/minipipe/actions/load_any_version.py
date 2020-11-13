import pymel.core as pc

from cg.maya.minipipe import colors
reload(colors)
COLOR = colors.COLOR

def load(version_menu, scene, dept, *args, **kwargs):
    scene_file = scene.versions[dept][version_menu.getSelect() - 1]["absolute_path"]

    try:
        pc.openFile(scene_file)
    except RuntimeError:
        answer = pc.confirmDialog(
            title='Unsaved Changes',
            message='Current scene has unsaved changes.\nContinue and lose changes?',
            button=['Continue', 'No! Stop!'], defaultButton='Continue',
            cancelButton='No! Stop!', dismissString='No! Stop!'
        )
        if answer == 'No! Stop!':
            return None
        pc.openFile(scene_file, force=True)

    in_layout = kwargs.get("in_layout", None)
    if in_layout:
        in_layout()


def ui(parentColumnLayout, scene, dept, *args, **kwargs):
    with pc.rowLayout(p=parentColumnLayout, nc=2, adj=1):
        with pc.optionMenu(bgc=(0.33, 0.33, 0.33), h=30) as version_menu:
            for version in scene.versions[dept]:
                pc.menuItem(
                    "Version {}, {}, by {}".format(
                        version["version"], version["nice_time"], version["user"]
                    ) 
                )
        pc.button(
            c=pc.Callback(load, version_menu, scene, dept, *args, **kwargs),
            label="Open", bgc=COLOR.add_green, h=30, w=50
        )