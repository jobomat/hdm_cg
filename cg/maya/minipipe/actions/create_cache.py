import os
from shutil import copyfile
from time import time

import pymel.core as pc

from cg.maya.files.alembic import abc_export
from cg.maya.minipipe.core import read_meta, write_meta


def select_grp(namespace, grp):
    pc.select("{}:{}".format(namespace, grp))

def invert_checkboxes(reference_list):
    for ref in reference_list:
        ref["checkbox"].setValue(not ref["checkbox"].getValue())

def save_meta_from_control(namespace, meta, control, getFunction):
    meta[control.getAnnotation()] = getattr(control, getFunction)()
    write_meta(meta, namespace)

def set_all_start_end(se_option, reference_list, shot_meta):
    selected_option = se_option.getSelect()
    if selected_option == 1:
        return
    for ref in reference_list:
        if selected_option == 2:  # from range slider
            ref["start_ff"].setValue(pc.language.Env().getMinTime())
            ref["end_ff"].setValue(pc.language.Env().getMaxTime())
        elif selected_option == 3:  # from shot_meta
            ref["start_ff"].setValue(shot_meta["start"])
            ref["end_ff"].setValue(shot_meta["end"])
            ref["step_ff"].setValue(shot_meta["step"])
        else:  # from reference meta
            ref["start_ff"].setValue(ref["meta"]["start"])
            ref["end_ff"].setValue(ref["meta"]["end"])
            ref["step_ff"].setValue(ref["meta"]["step"])

def create_caches(scene, reference_list):
    caches_dir = "{}/caches".format(scene.absolute_path)
    if not os.path.isdir(caches_dir):
        os.mkdir(caches_dir)
    cache_archive_dir = "{}/archive".format(caches_dir)
    if not os.path.isdir(cache_archive_dir):
        os.mkdir(cache_archive_dir)

    for ref in reference_list:
        if ref["checkbox"].getValue():
            cache_name = ref["name_tf"].getText()
            file = "{}/{}.abc".format(caches_dir, cache_name)
            root = "{}:{}".format(ref["namespace"], ref["meta"]["abc_grp"])
            frame_ranges = [{
                "start": ref["start_ff"].getValue(),
                "end": ref["end_ff"].getValue()
            }]
            if os.path.isfile(file):
                copyfile(
                    file, 
                    "{}/{}_{}.abc".format(cache_archive_dir, cache_name, int(time()))
                )

            abc_export(root, file, frame_ranges)


def ui(parent_cl, scene, dept, *args, **kwargs):
    ratios = (2, 6, 3, 3, 3, 10)
    bgc = (.3, .3, .3)
    with pc.columnLayout(adj=True, p=parent_cl):
        pc.separator(style="in")
        with pc.horizontalLayout(bgc=bgc, h=25, ratios=(1,5)):
            pc.text(label="  Create Caches", font="boldLabelFont", align="left")
            pc.text(label="(Target Folder: {}/caches)  ".format(scene.name), align="right")
        with pc.horizontalLayout(ratios=ratios, bgc=bgc, h=25):
            pc.text(label="")
            pc.text(label="Namespace", font="boldLabelFont", align="left")
            pc.text(label="Start", font="tinyBoldLabelFont", align="left")
            pc.text(label="End", font="tinyBoldLabelFont", align="left")
            pc.text(label="Step", font="tinyBoldLabelFont", align="left")
            # pc.text(label="Create Cache", font="boldLabelFont")
            pc.text(label="Cache Name", font="boldLabelFont", align="left")
        
        with pc.scrollLayout(h=200, cr=True, bgc=(.2,.2,.2)):
            seen = {}
            reference_list = []

            shot_meta = read_meta()
            shot_meta["start"] = shot_meta.get("start", 1)
            shot_meta["end"] = shot_meta.get("end", 50)
            shot_meta["step"] = shot_meta.get("step", 1)

            for ref in pc.listReferences():
                meta = read_meta(ref.namespace)
                data = {}
                if meta.get("abc_grp", False):
                    data["namespace"] = ref.namespace

                    meta["start"] = meta.get("start", shot_meta["start"])
                    meta["end"] = meta.get("end", shot_meta["end"]) 
                    meta["step"] = meta.get("step", shot_meta["step"])

                    data["meta"] = meta

                    with pc.horizontalLayout(ratios=ratios):
                        data["checkbox"] = pc.checkBox(label="")
                        pc.button(
                            label=ref.namespace, 
                            c=pc.Callback(select_grp, ref.fullNamespace, meta["abc_grp"]),
                            annotation="Select the group to be cached ({}).".format(meta["abc_grp"])
                        )
                        start_ff = pc.floatField(
                            v=meta["start"], w=20, pre=1, annotation="start"
                        )
                        start_ff.changeCommand(
                            pc.Callback(
                                save_meta_from_control,
                                ref.namespace, meta, start_ff, "getValue"
                            )
                        )
                        end_ff = pc.floatField(
                            v=meta["end"], w=20, pre=1, annotation="end"
                        )
                        end_ff.changeCommand(
                            pc.Callback(
                                save_meta_from_control,
                                ref.namespace, meta, end_ff, "getValue"
                            )
                        )
                        step_ff = pc.floatField(
                            v=meta["step"], w=20, pre=2, annotation="step"
                        )
                        step_ff.changeCommand(
                            pc.Callback(
                                save_meta_from_control,
                                ref.namespace, meta, step_ff, "getValue"
                            )
                        )
                        data["start_ff"] = start_ff
                        data["end_ff"] = end_ff
                        data["step_ff"] = step_ff

                        suggested_name = meta.get("cache_name", False)

                        if not suggested_name:
                            name = ref.namespace.split("_")[0]
                            i = 1
                            if name in seen.keys():
                                i = seen[name] + 1
                            suggested_name = "{}_{}".format(name, i)
                            seen[name] = i
                        
                        data["name_tf"] = pc.textField(text=suggested_name, annotation="cache_name")
                        data["name_tf"].changeCommand(
                            pc.Callback(
                                save_meta_from_control,
                                ref.namespace, meta, data["name_tf"], "getText"
                            )
                        )

                    reference_list.append(data)
                    
                    pc.separator()

        with pc.horizontalLayout(bgc=bgc):
            pc.button(label="Flip Checkboxes", c=pc.Callback(invert_checkboxes, reference_list))
            with pc.optionMenu() as se_option:
                pc.menuItem(label="Set All Start/End to:")
                pc.menuItem(label="Range Slider Values")
                pc.menuItem(label="Shot Meta Values")
                pc.menuItem(label="Individual Meta Values")
            se_option.changeCommand(pc.Callback(set_all_start_end, se_option, reference_list, shot_meta))
            pc.button(
                label="Create Caches", bgc=(.4, .4, .4),
                c=pc.Callback(create_caches, scene, reference_list)
            )
        pc.separator(style="in")