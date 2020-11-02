import os
import pymel.core as pc

from cg.maya.files import alembic
reload(alembic)
from cg.maya.files.paths import normpath
from cg.maya.minipipe.utils import setup_maya
from cg.maya.minipipe.core import read_meta, write_meta


def create_first_shading_version(scene, dept, *args, **kwargs):
    user = kwargs.get("user", "unknown")
    out_layout = kwargs.get("out_layout", None)
    update_status_message = kwargs.get("update_status_message", None)

    sel = pc.selected()
    if not sel or len(sel) > 1:
        pc.confirmDialog(
            title='Select a Group',
            message='Please select exactly one group.\nThe cache and shading-version will\ncontain all children of that group.',
            button=['Got it!'], defaultButton='Got it!',
            cancelButton='Got it!', dismissString='Got it!'
        )
        return

    meta = read_meta()
    meta["abc_grp"] = sel[0].name()
    write_meta(meta)
    pc.saveFile()
    abc_file = normpath("{}/{}.abc".format(scene.absolute_path, scene.name))
    alembic.abc_export(meta["abc_grp"], abc_file)
    
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

    alembic.abc_import(abc_file)
    write_meta({"abc_grp": meta["abc_grp"]})

    dept_v, dept_rh = scene.create_dept_folders("shd")
    pc.saveAs("/".join([dept_v, scene.create_version_file_name("shd", user)]))

    msg = ("success", "First Shading version for {} created.".format(scene.name))

    if out_layout:
        out_layout()
    if update_status_message:
        update_status_message(msg)


def ui(parent_cl, scene, dept, *args, **kwargs):
    if  scene.has_release("mod"):
        if "shd" not in scene.get_depts():
            # pc.text(p=parent_cl, label="New UVs? Then you can:")
            pc.button(
                p=parent_cl, label="Create first Shading Version + Cache from Selection",
                c=pc.Callback(create_first_shading_version, scene, dept, *args, **kwargs)
            )
        else:
            meta = read_meta()
            pc.text(p=parent_cl, label="New UVs? Then:")
            pc.button(p=parent_cl, label="Write new Alembic Base ({}).".format(meta["abc_grp"]))
