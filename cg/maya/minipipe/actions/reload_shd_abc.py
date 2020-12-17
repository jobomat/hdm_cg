import os
from shutil import copyfile
from time import time

import pymel.core as pc

from cg.maya.files.alembic import abc_merge
from cg.maya.minipipe.core import read_meta, write_meta
from cg.maya.minipipe import colors
reload(colors)
COLOR = colors.COLOR


def merge_alembic(scene, dept, abc_grp, *args, **kwargs):
    abc_file = "{}/{}.abc".format(scene.absolute_path, scene.name)
    pc.select(abc_grp)
    print abc_file
    abc_merge(abc_grp, abc_file)
  

def ui(parent_cl, scene, dept, *args, **kwargs):
    current_scene = kwargs.get("current_scene", None)
    current_scene_dept = kwargs.get("current_scene_dept", None)
    config = kwargs.get("config")
    
    if current_scene and current_scene.name == scene.name and current_scene_dept == dept:
        meta = read_meta()
        pc.button(
            p=parent_cl, label="Update Model (Merge '{}' into '{}')".format(
                "{}.abc".format(scene.name),
                meta["abc_grp"]
            ),
            c=pc.Callback(merge_alembic, scene, dept, meta["abc_grp"], *args, **kwargs),
            bgc=COLOR.add_green
        )