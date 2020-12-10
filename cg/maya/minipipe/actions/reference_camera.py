import os

import pymel.core as pc

from cg.maya.files.paths import normpath

from cg.maya.minipipe import colors
reload(colors)
COLOR = colors.COLOR

def create_reference(scene, cam_optionMenu, *args, **kwargs):
    cam_file_name = cam_optionMenu.getValue()
    ref_file = normpath(
        os.path.join(
            "${}".format(pc.mel.eval('getenv "env_var_name"')),
            pc.workspace.fileRules["mayaAscii"],
            scene.relative_path,
            "cameras",
            cam_file_name
        )
    )
    pc.createReference(ref_file, namespace=cam_file_name.split(".")[0])


def create_camera_items(scene):
    _, dirs, files = next(os.walk("{}/cameras".format(scene.absolute_path)))
    for f in [f for f in files if f.endswith(".ma")]:
        pc.menuItem(f)


def ui(parent_cl, scene, dept, *args, **kwargs):
    current_scene = kwargs.get("current_scene", None)
    current_scene_dept = kwargs.get("current_scene_dept", None)
    config = kwargs.get("config")
    
    if current_scene and current_scene.name == scene.name and current_scene_dept == dept:
        with pc.rowLayout(nc=3, adj=2):
            pc.text(label="Import Cam Reference:", align="left", font="boldLabelFont")
            with pc.optionMenu(bgc=COLOR.button_grey) as cam_optionMenu:
                create_camera_items(scene)
            pc.button(
                "Import", bgc=COLOR.add_green,
                c=pc.Callback(create_reference, scene, cam_optionMenu)
            )