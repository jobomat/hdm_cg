import os
from shutil import copyfile
from time import time

import pymel.core as pc

from cg.maya.files.alembic import abc_merge
from cg.maya.minipipe.core import read_meta, write_meta
from cg.maya.minipipe import colors
reload(colors)
COLOR = colors.COLOR

def select_grp(namespace, grp):
    pc.select("{}:{}".format(namespace, grp.split(":")[-1]))


def create_caches_menu(scene, namespace):
    caches_dir = "{}/caches".format(scene.absolute_path)
    _, dirs, files = next(os.walk(caches_dir))
    for file in [f for f in files if f.endswith(".abc")]:
        pc.menuItem(file)


def merge_alembic(scene, selected_cache_optionMenu, namespace, grp):
    abc_file = "{}/caches/{}".format(
        scene.absolute_path,
        selected_cache_optionMenu.getValue()
    )
    select_grp(namespace, grp)
    abc_merge("{}:{}".format(namespace, grp.split(":")[-1]), abc_file)
  

def ui(parent_cl, scene, dept, *args, **kwargs):
    current_scene = kwargs.get("current_scene", None)
    current_scene_dept = kwargs.get("current_scene_dept", None)
    config = kwargs.get("config")
    
    if current_scene and current_scene.name == scene.name and current_scene_dept == dept:
        ratios = (2,2,1)
        with pc.columnLayout(adj=True, p=parent_cl):
            pc.separator(style="in")
            pc.text(label="Update Caches:", h=30, align="left")
            with pc.horizontalLayout(ratios=ratios, bgc=COLOR.mid_grey, h=25):
                pc.text(label="Cached Shading Asset", font="tinyBoldLabelFont", align="center")
                pc.text(label="Avalible Caches", font="tinyBoldLabelFont", align="center")
                pc.text(label="")
            
            with pc.scrollLayout(h=100, cr=True, bgc=COLOR.dark_grey):
                #shot_meta = read_meta()
            
                for ref in pc.listReferences():
                    meta = read_meta(ref.namespace)
                    if meta and meta.get("abc_grp", False):
                        with pc.horizontalLayout(ratios=ratios):
                            pc.button(
                                label=ref.namespace, 
                                c=pc.Callback(select_grp, ref.fullNamespace, meta["abc_grp"]),
                                annotation="Select the import group ({}).".format(meta["abc_grp"])
                            )
                            with pc.optionMenu(bgc=COLOR.button_grey) as selected_cache_optionMenu:
                                create_caches_menu(scene, ref.namespace)
                            pc.button(
                                label="Update", bgc=COLOR.add_green,
                                c=pc.Callback(
                                    merge_alembic, scene, selected_cache_optionMenu,
                                    ref.namespace, meta["abc_grp"]
                                )
                            )
                        pc.separator()
            pc.separator(style="in")