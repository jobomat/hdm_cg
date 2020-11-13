import pymel.core as pc

from cg.maya.minipipe import colors
reload(colors)
COLOR = colors.COLOR


def bump_version(scene, dept, **kwargs):
    user = kwargs.get("user", "unknown")
    msg = scene.bump_version(dept, user)
    
    out_layout = kwargs.get("out_layout", None)
    update_status_message = kwargs.get("update_status_message", None)
    if out_layout:
        out_layout()
    if update_status_message:
        update_status_message(msg)


def ui(parent_cl, scene, dept, *args, **kwargs):
    pc.button(
        p=parent_cl, label="Save New Version", bgc=COLOR.add_green,
        c=pc.Callback(bump_version, scene, dept, **kwargs)
    )