import pymel.core as pc

from cg.maya.minipipe import colors
reload(colors)
COLOR = colors.COLOR

def load(cl, variant_menu, variant_versions, scene, dept, *args, **kwargs):
    variant_sel = variant_menu.getSelect() - 1
    versions_menu = cl.getChildren()[0]
    version_sel = pc.optionMenu(versions_menu, q=True, select=True) - 1
    
    scene_file = "{}/versions/ren/{}".format(
        scene.absolute_path,
        variant_versions.items()[variant_sel][1][version_sel]
    )

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


def create_version_menu(cl, variant_menu, variant_versions, callback):
    for child in cl.getChildren():
        pc.deleteUI(child)

    sm = pc.optionMenu(bgc=(0.33, 0.33, 0.33), h=30, p=cl)
    
    sm.addMenuItems(
        reversed(variant_versions.items()[variant_menu.getSelect() - 1][1])
    )


def ui(parentColumnLayout, scene, dept, *args, **kwargs):
    variant_versions = scene.get_variant_versions("ren")
    versions = []
    i = 0
    
    pc.text(label="{} Variant:".format(scene.name), align="left")
    with pc.rowLayout(p=parentColumnLayout, nc=3, adj=1):
        with pc.optionMenu(bgc=(0.33, 0.33, 0.33), h=30) as variant_menu:
            for variant, v in variant_versions.items():
                pc.menuItem(
                    variant
                )
        with pc.columnLayout() as cl:
            pass
        pc.button(
            c=pc.Callback(load, cl, variant_menu, variant_versions, scene, dept, *args, **kwargs),
            label="Open", bgc=COLOR.add_green, h=30, w=50
        )
        create_version_menu(cl, variant_menu, variant_versions, None)
        variant_menu.changeCommand(
            pc.Callback(
                create_version_menu,
                cl, variant_menu, variant_versions, None
            )
        )