import os
from shutil import copyfile
from time import time

import pymel.core as pc

from cg.maya.minipipe.core import (
    read_meta, write_meta,
    get_cam_attributes, get_shotcams, get_highest_cam_count,
    export_cam
)
from cg.maya.minipipe import colors
reload(colors)
COLOR = colors.COLOR


def create_renderpal_renderset(renderer, parameters):
    rset = [
        "<RenderSet>",
        "\t<Renderer>{}</Renderer>".format(renderer),
        "\t\t<Values>"
    ]

    for parameter, values in parameters.items():
        if not values:
            continue
        rset.append("\t\t<{}>".format(parameter))
        for value in values:
            rset.append("\t\t\t<Value>{}</Value>".format(
                str(value).replace("/", "\\\\")
            ))
        rset.append("\t\t</{}>".format(parameter))

    rset.extend(["\t</Values>", "</RenderSet>"])
    return "\n".join(rset)


def create(scene, name_tf, cam_tf, range_tf, imagedir_tf, renderfile_tf, maya_dir):
    renderset_filename = name_tf.getText()
    cameras = [c for c in cam_tf.getText().split(",") if c]
    ranges = range_tf.getText()
    imagedir = imagedir_tf.getText()
    renderfile = renderfile_tf.getText()

    if not renderset_filename or not renderfile or not ranges:
        pc.confirmDialog(
            title='Confirm', button=['OK'], defaultButton='OK',
            message='You have to specify at least\n - a filename for the renderset\n - a frame range\n - a file to render'
        )
        return

    renderset_filename = "{}_{}.rset".format(pc.mel.eval('getenv "env_var_name"'), renderset_filename)

    parameters = {
        "camera": cameras,
        "frames": ranges.split(","),
        "outdir": [imagedir],
        # "padding": [3],
        # "percentres": [50.0],
        "projdir": [maya_dir],
        "scene": [renderfile]
    }

    renderer = "Arnold Renderer/2020_ca"
    renderset_content = create_renderpal_renderset(renderer, parameters)

    local_maya_project_dir = pc.mel.eval('getenv "{}"'.format(pc.mel.eval('getenv "env_var_name"')))

    shot_renderset_path = "{}/rendersets".format(scene.absolute_path)
    global_renderset_path = "{}/rendersets".format(local_maya_project_dir)
    shot_renderset_archive_path = "{}/rendersets/archive".format(scene.absolute_path)
    global_renderset_archive_path = "{}/rendersets/archive".format(local_maya_project_dir)

    if not os.path.isdir(shot_renderset_path):
        os.mkdir(os.path.normpath(shot_renderset_path))
        os.mkdir(os.path.normpath(shot_renderset_archive_path))
    if not os.path.isdir(global_renderset_path):
        os.mkdir(os.path.normpath(global_renderset_path))
        os.mkdir(os.path.normpath(global_renderset_archive_path))

    shot_renderset_filename = "{}/{}".format(shot_renderset_path, renderset_filename)
    global_renderset_filename = "{}/{}".format(global_renderset_path, renderset_filename)

    if os.path.isfile(shot_renderset_filename):
        copyfile(
            shot_renderset_filename,
            "{}/{}_{}".format(shot_renderset_archive_path, int(time()), renderset_filename)
        )
    with open(shot_renderset_filename, "w") as f:
        f.write(renderset_content)

    if os.path.isfile(global_renderset_filename):
        copyfile(
            global_renderset_filename,
            "{}/{}_{}".format(global_renderset_archive_path, int(time()), renderset_filename)
        )
    copyfile(shot_renderset_filename, global_renderset_filename)


def create_cam_menu_items():
    cams = [c.getTransform() for c in pc.ls(type="camera") if c.getTransform().hasAttr("mp_start")]
    for cam in cams:
        pc.menuItem(cam)


def set_cam(cam_menu, cam_textField):
    cam = cam_menu.getValue()
    if cam == "Clear":
        cam_textField.setText("")
        cam_menu.setSelect(1)
        return
    if cam == "Use selected Camera":
        sel = pc.selected()
        if not sel:
            pc.warning("Please select a camera.")
            cam_menu.setSelect(1)
            return
        if sel[0].getShape() and sel[0].getShape().type() == "camera":
            cam = sel[0].name()
        else:
            pc.warning("Please select something of type camera.")
            cam_menu.setSelect(1)
            return
    cam_textField.setText(cam)
    cam_menu.setSelect(1)


def create_range_menu_items():
    cams = [c.getTransform() for c in pc.ls(type="camera") if c.getTransform().hasAttr("mp_start")]
    for cam in cams:
        start = pc.PyNode(cam).getAttr("mp_start")
        end = pc.PyNode(cam).getAttr("mp_end")
        cam_range = "{:.0f}{}{:.0f}".format(start, "-" if start != end else "", end if start != end else "")
        pc.menuItem("{} ({})".format(cam_range, cam.nodeName().split(":")[-1]))


def set_range(range_menu, range_textField, cam_textField, meta_start, meta_end):
    range_selection = range_menu.getValue()

    if range_selection == "Add/Clear Range...":
        return
    current_ranges = []
    if range_textField.getText():
        current_ranges.append(range_textField.getText())
    if range_selection == "Clear":
        range_textField.setText("")
        range_menu.setSelect(1)
        return
    new_range = ""
    if range_selection == "From shot meta":
        new_range = "{:.0f}{}{:.0f}".format(
            meta_start,
            "-" if meta_start != meta_end else "",
            meta_end if meta_start != meta_end else ""
        )
    elif range_selection == "From Range Slider":
        start = pc.language.Env().getMinTime()
        end = pc.language.Env().getMaxTime()
        new_range = "{:.0f}{}{:.0f}".format(
            start,
            "-" if start != end else "",
            end if start != end else ""
        )
    else:
        new_range = range_selection.split()[0]

    current_ranges.append(new_range)
    range_textField.setText(",".join(current_ranges))
    range_menu.setSelect(1)


def ui(parent_cl, scene, dept, *args, **kwargs):
    variant = kwargs.get("variant", "")
    config = kwargs.get("config", {})
    render_base_path = config.get("render_base_path", "UNKNOWN")
    
    meta = read_meta()
    start = meta.get("start", pc.language.Env().getMinTime())
    end = meta.get("end", pc.language.Env().getMaxTime())
    with pc.columnLayout(adj=True, p=parent_cl):
        pc.separator(style="in")
        with pc.horizontalLayout(bgc=COLOR.mid_grey, h=25):
            pc.text(label="Create RenderPal Render Set", font="boldLabelFont", w=120, align="left")
            pc.text(label="(Target Folder: {}/rendersets)  ".format(scene.name), align="right")
        with pc.columnLayout(adj=True):
            with pc.rowLayout(nc=2, adj=2, cw=(1, 120)):
                pc.text(label="Render Set Name", align="right")
                name_textField = pc.textField(text=variant, h=30)
            with pc.rowLayout(nc=2, adj=2, cw=(1, 120)):
                pc.text(label="Camera", align="right")
                with pc.horizontalLayout():
                    cam_textField = pc.textField(
                        editable=False, placeholderText="Not set = Use scene info", h=30
                    )
                    with pc.optionMenu() as cam_menu:
                        pc.menuItem("Select a Camera / Clear")
                        create_cam_menu_items()
                        pc.menuItem("Use selected Camera")
                        pc.menuItem("Clear")
                    cam_menu.changeCommand(pc.Callback(set_cam, cam_menu, cam_textField))
            with pc.rowLayout(nc=2, adj=2, cw=(1, 120)):
                pc.text(label="Frame List", align="right")
                with pc.horizontalLayout():
                    range_textField = pc.textField(
                        text="1-100", h=30,
                        annotation="Comma separated list of start-end frames to render. (1-10,15,20-25)"
                    )
                    with pc.optionMenu() as range_menu:
                        pc.menuItem("Add/Clear Range...")
                        pc.menuItem("Clear")
                        create_range_menu_items()
                        pc.menuItem("From shot meta")
                        pc.menuItem("From Range Slider")
                    range_menu.changeCommand(
                        pc.Callback(set_range, range_menu, range_textField, cam_textField, start, end)
                    )
            with pc.rowLayout(nc=2, adj=2, cw=(1, 120)):
                pc.text(label="Image Dir", align="right", h=30)
                imagedir_textField = pc.textField(
                    h=30, text="{}/renders/{}/{}".format(
                        render_base_path, scene.name, variant
                    )
                )
            variant_release = [r[1] for r in scene.releases if r[1].endswith(variant + "_ren.ma")]
            text = "Please Release this Version before Rendering!"
            if variant_release:
                text = "{}/scenes/{}/{}".format(
                    render_base_path, scene.name, variant_release[0].split("/")[-1]
                )
            with pc.rowLayout(nc=2, adj=2, cw=(1, 120)):
                pc.text(label="Renderfile", align="right", h=30)
                renderfile_textField = pc.textField(
                    h=30, text=text
                )
        pc.button(
            label="Create Render Set", c=pc.Callback(
                create,
                scene,
                name_textField,
                cam_textField,
                range_textField,
                imagedir_textField,
                renderfile_textField,
                render_base_path
            )
        )
