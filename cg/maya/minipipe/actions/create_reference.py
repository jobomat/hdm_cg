import os

import pymel.core as pc

from cg.maya.files.paths import normpath
from cg.maya.minipipe.core import get_scene_list


def create_reference(scene_list, *args, **kwargs):
    for s in scene_list.getSelectItem():
        name, _, path = s.split("\t")
        ref_file = normpath(os.path.join(
            "${}".format(pc.mel.eval('getenv "env_var_name"')),
            pc.workspace.fileRules["mayaAscii"],
            path
        ))
        dept = path.split(".")[0].split("_")[-1]
        pc.createReference(ref_file, namespace="{}_{}".format(name, dept))



def get_scenes(types=[], depts=[], config={}):
    scenes = [s for s in get_scene_list()]

    if types:
        scenes = [s for s in scenes if s.type["name"] in types]

    filtered_scenes = []
    for s in scenes:
        s.get_status()
        for r in s.releases:
            if depts and r[0] not in depts:
                continue
            else:
                # list_text = "{n}\t{d}\t{t}/{n}/{n}_{r}.ma" if first else "\t{d}\t{t}/{n}/{n}_{r}.ma"
                filtered_scenes.append(
                    "{n}\t{d}\t{t}/{n}/{n}_{r}.ma".format(
                        n=s.name,
                        d=config.get("depts", {}).get(r[0], {}).get("nice_name", r[0]),
                        t=s.type["name"],
                        r=r[0]
                    )
                )

    return filtered_scenes


def update_scene_list(scene_list, typefilter_checkbox, deptfilter_checkbox, config):
    scene_list.removeAll()
    types = []
    if typefilter_checkbox.getValue():
        types = typefilter_checkbox.getAnnotation().split(",")
    depts = []
    if deptfilter_checkbox.getValue():
        depts = deptfilter_checkbox.getAnnotation().split(",")
    scene_list.append(get_scenes(types, depts, config))


def ui(parent_cl, scene, dept, *args, **kwargs):
    current_scene = kwargs.get("current_scene", None)
    current_scene_dept = kwargs.get("current_scene_dept", None)
    config = kwargs.get("config")
    
    if current_scene and current_scene.name == scene.name and current_scene_dept == dept:
        if current_scene.type["name"] == "sets":
            type_filters = ["props"]
            dept_filters = ["shd"]

        elif current_scene.type["name"] == "shots":
            type_filters = ["sets", "chars"]
            if current_scene_dept == "ani":
                dept_filters = ["rig", "shd"]
            elif current_scene_dept == "ren":
                dept_filters = ["shd"]

        pc.separator(h=10, style='in')
        pc.text(label="Create References:", align="left")
        scene_list = pc.textScrollList(
            numberOfRows=5 if dept == "ren" else 10, allowMultiSelection=True
        )

        with pc.horizontalLayout():
            typefilter_checkbox = pc.checkBox(
                label="{} only".format(
                    " + ".join(
                        [config.get("scene_types",{}).get(t, {}).get("nice_name", t) for t in type_filters]
                    )
                ),
                value=True, annotation=",".join(type_filters)
            )
            deptfilter_checkbox = pc.checkBox(
                label="{} only".format(
                    " + ".join(
                        [config.get("depts",{}).get(d, {}).get("nice_name", d) for d in dept_filters]
                    )
                ),
                value=True, annotation=",".join(dept_filters)
            )
            pc.button(
                label="Reference selected",
                c=pc.Callback(create_reference, scene_list, *args, **kwargs)
            )

        typefilter_checkbox.setChangeCommand(pc.Callback(
            update_scene_list, scene_list, typefilter_checkbox, deptfilter_checkbox, config
        ))
        deptfilter_checkbox.setChangeCommand(pc.Callback(
            update_scene_list, scene_list, typefilter_checkbox, deptfilter_checkbox, config
        ))
        
        update_scene_list(scene_list, typefilter_checkbox, deptfilter_checkbox, config)
