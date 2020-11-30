import os
from shutil import copyfile
from time import time

import pymel.core as pc

from cg.maya.minipipe.core import read_meta, write_meta
from cg.maya.minipipe import colors
reload(colors)
COLOR = colors.COLOR


def get_cam_attributes():
    return [
        a for a in pc.SCENE.minipipe_meta.listAttr(ud=True)
        if a.name().startswith("minipipe_meta.shotcam_")
    ]
    
    
def get_shotcams():
    return [c.listConnections()[0] for c in get_cam_attributes()]


def get_highest_cam_count():
    cam_attrs = get_cam_attributes()
    return max([int(c.split("_")[-1]) for c in cam_attrs]) if cam_attrs else 0


def add_selected_cams(cam_row_cl, scene, dept):
    sel = pc.selected()
    if not sel:
        pc.warning("Please select one or more Cameras.")
        return

    cam_counter = get_highest_cam_count()
    meta_node = pc.SCENE.minipipe_meta
    meta = read_meta()

    for cam in sel:
        shape = cam.getShape()
        if not shape or shape.type() != "camera":
            pc.warning("Object '{}' skipped as it is not of type 'camera'.".format(cam))
            continue
        cam_counter += 1
        attr_name = "shotcam_{}".format(cam_counter)
        meta_node.addAttr(attr_name, at="bool")
        cam.visibility >> meta_node.attr(attr_name)
        # Add start/end to cam
        if not cam.hasAttr("mp_start"):
            cam.addAttr("mp_start", at="float")
        cam.setAttr("mp_start", meta["start"])
        if not cam.hasAttr("mp_end"):
            cam.addAttr("mp_end", at="float")
        cam.setAttr("mp_end", meta["end"])

    create_cam_rows(cam_row_cl, scene, dept)


def create_cam_folder(scene):
    cameras_dir = "{}/cameras".format(scene.absolute_path)
    if not os.path.isdir(cameras_dir):
        os.mkdir(cameras_dir)
    camera_archive_dir = "{}/archive".format(cameras_dir)
    if not os.path.isdir(camera_archive_dir):
        os.mkdir(camera_archive_dir)
    return cameras_dir, camera_archive_dir


def export_cam(cam, scene, dept):
    cam_dir, cam_archive_dir = create_cam_folder(scene)

    cam_dup = pc.duplicate(cam, rr=True, un=True)[0]
    cam_name = cam.name()
    cam.rename(cam_name + "_TEMP")
    cam_dup.rename(cam_name)

    pc.parent(cam_dup, w=True)

    con = pc.parentConstraint(cam, cam_dup)
    pc.bakeResults(
        cam_dup, simulation=True, t=(0,125), sampleBy=1, oversamplingRate=1,
        disableImplicitControl=True, preserveOutsideKeys=True, sparseAnimCurveBake=False,
        removeBakedAttributeFromLayer=False, removeBakedAnimFromLayer=False, bakeOnOverrideLayer=False,
        minimizeRotation=True, controlPoints=False, shape=True
    )
    pc.delete(con)
    pc.select(cam_dup, r=True)

    cam_export_file = "{}/{}.ma".format(cam_dir, cam_name)
    if os.path.isfile(cam_export_file):
        copyfile(
            cam_export_file, 
            "{}/{}_{}.ma".format(cam_archive_dir, cam_name, int(time()))
        )
        
    pc.exportSelected(
        cam_export_file,
        force=True, type="mayaAscii", preserveReferences=True, expressions=True
    )
    pc.select(cam, r=True)
    pc.delete(cam_dup)
    cam.rename(cam_name)



def create_cam_rows(cam_row_cl, scene, dept):
    for child in cam_row_cl.getChildren():
        pc.deleteUI(child)

    for shot_cam in get_shotcams():
        with pc.rowLayout(nc=7, p=cam_row_cl) as row:
            cam_name_text = pc.text(label=shot_cam.name(), align="left", w=95)
            pc.text(label="Start", w=50, align="right")
            start_intField = pc.intField(
                value=shot_cam.getAttr("mp_start"),
                annotation="mp_start", w=40
            )
            pc.text(label="End", w=30, align="right")
            end_intField = pc.intField(
                value=shot_cam.getAttr("mp_end"),
                annotation="mp_end", w=40
            )
            start_intField.changeCommand(pc.Callback(set_cam_start_end, start_intField, shot_cam))
            end_intField.changeCommand(pc.Callback(set_cam_start_end, end_intField, shot_cam))
            pc.button(label="Unflag", c=pc.Callback(unflag_cam, cam_row_cl, shot_cam, scene, dept))
            pc.button(label="Export", c=pc.Callback(export_cam, shot_cam, scene, dept))
        pc.separator(p=cam_row_cl)
            

def set_cam_start_end(intField, cam):
    cam.setAttr(intField.getAnnotation(), intField.getValue())


def unflag_cam(cam_row_cl, shot_cam, scene, dept):
    vis = shot_cam.attr("visibility")
    cam_plug = vis.listConnections(plugs=True)[0]
    vis // cam_plug
    cam_plug.delete()
    create_cam_rows(cam_row_cl, scene, dept)


def ui(parent_cl, scene, dept, *args, **kwargs):
    meta = read_meta()
    with pc.columnLayout(adj=True, p=parent_cl):
        pc.separator(style="in")
        with pc.horizontalLayout(bgc=COLOR.mid_grey, h=25) as hl:
            pc.text(label="Shot Cameras", font="boldLabelFont", w=120, align="left")
            add_cam_button = pc.button(label="Flag selected Camera", bgc=COLOR.button_grey)
            pc.text(label="(Target Folder: {}/cameras)  ".format(scene.name), align="right")
        hl.redistribute(1,1,2)
        with pc.columnLayout(adj=True) as cam_row_cl:
            create_cam_rows(cam_row_cl, scene, dept)

        add_cam_button.setCommand(pc.Callback(add_selected_cams, cam_row_cl, scene, dept))