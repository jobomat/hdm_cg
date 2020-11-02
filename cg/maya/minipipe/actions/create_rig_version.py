import os
import pymel.core as pc

from cg.maya.minipipe.utils import setup_maya


def create_first_rig_version(scene, dept, *args, **kwargs):
    user = kwargs.get("user", "unknown")
    out_layout = kwargs.get("out_layout", None)
    update_status_message = kwargs.get("update_status_message", None)

    try:
        pc.newFile(type="mayaAscii")
    except RuntimeError:
        answer = pc.confirmDialog(
            title='Unsaved Changes',
            message='Current scene has unsaved changes.\nContinue and lose changes?',
            button=['Continue', 'No! Stop!'], defaultButton='Continue',
            cancelButton='No! Stop!', dismissString='No! Stop!'
        )
        if answer == 'No! Stop!':
            return None
        pc.newFile(type="mayaAscii", force=True)
    setup_maya()  # set fps and stuff if user has wrong prefs

    scene.reference(dept, namespace=scene.name)

    dept_v, dept_rh = scene.create_dept_folders("rig")
    pc.saveAs("/".join([dept_v, scene.create_version_file_name("rig", user)]))

    msg = ("success", "First rig version for {} created.".format(scene.name))

    if out_layout:
        out_layout()
    if update_status_message:
        update_status_message(msg)



def ui(parent_cl, scene, dept, *args, **kwargs):
    if "rig" not in scene.get_depts() and scene.has_release("mod"):
        pc.button(
            p=parent_cl, label="Create first Rig Version",
            c=pc.Callback(create_first_rig_version, scene, dept, *args, **kwargs)
        )
