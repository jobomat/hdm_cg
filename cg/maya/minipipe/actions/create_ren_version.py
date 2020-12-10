import os
from shutil import copyfile
import pymel.core as pc

from cg.maya.files.paths import normpath
from cg.maya.minipipe.utils import setup_maya
from cg.maya.minipipe.core import (
    read_meta, write_meta,
    get_cam_attributes, get_shotcams, get_highest_cam_count,
    export_cam, scene_from_file
)
from cg.maya.minipipe import colors
reload(colors)
COLOR = colors.COLOR


class CreateRenderVersion():
    def __init__(self, scene, dept, *args, **kwargs):
        self.window_name = "create_render_version_win"
        self.scene = scene
        self.dept = dept
        self.user = kwargs.get("user", "unknown")
        self.out_layout = kwargs.get("out_layout", None)
        self.update_status_message = kwargs.get("update_status_message", None)

        self.reference_dicts = []
        self.camera_dicts = []

        self.main_window()

    def main_window(self):
        if pc.window(self.window_name, exists=True):
            pc.deleteUI(self.window_name)

        with pc.window(self.window_name, title="Create Render Versions") as self.win:
            with pc.columnLayout(adj=True, rs=3):
                pc.text(label="To create multiple versions enter the version names comma seperated:", h=30)
                self.names_textField = pc.textField(
                    placeholderText="Enter Render Version Names (Comma Seperated)",
                )
                with pc.frameLayout(label="Characters", collapsable=True):
                    with pc.columnLayout(adj=True, rs=3):
                        for i, ref in enumerate(pc.listReferences()):
                            meta = read_meta(ref.namespace)
                            if meta.get("abc_grp", False):
                                scene, dept, user, ts, version, variant = scene_from_file(ref.path)
                                scene.get_status()
                                select = 3
                                labelArray = ['No Shading Version availible', 'Remove', 'Do Nothing']
                                radio_kwargs = {"enable1": False}
                                if scene.has_release("shd"):
                                    select = 1
                                    labelArray = ['Replace w. Shading Version', 'Remove', 'Do Nothing']
                                    radio_kwargs = {}
                                if i > 0:
                                    pc.separator()
                                rbg = pc.radioButtonGrp(
                                    label=ref.namespace, numberOfRadioButtons=3, cw4=[120,180,70,50],
                                    labelArray3=labelArray,
                                    select=select, columnAlign=[1, "left"], **radio_kwargs
                                )
                                self.reference_dicts.append(
                                    {"reference": ref, "radioButtonGrp": rbg, "scene": scene}
                                )
                with pc.frameLayout(label="Cameras", collapsable=True):
                    with pc.columnLayout(adj=True, rs=3):
                        for i, shot_cam in enumerate(get_shotcams()):
                            if i > 0:
                                pc.separator()
                            rbg = pc.radioButtonGrp(
                                label=shot_cam.name(), numberOfRadioButtons=3, cw4=[120,180,70,50],
                                labelArray3=['Export and Reference', 'Remove', 'Do Nothing'],
                                select=1, columnAlign=[1, "left"]
                            )
                            self.camera_dicts.append({"camera": shot_cam, "radioButtonGrp": rbg})
                pc.button(label="Create Versions", bgc=COLOR.add_green, c=self.create_versions)

    def create_versions(self, *args):
        scene_names = self.names_textField.getText().split(",")
        scene_names = [s.replace(" ", "-").strip() for s in scene_names]
        scene_names = [s for s in scene_names if s]
        
        if not scene_names:
            pc.confirmDialog(
                title='Scene names missing',
                message='Please enter one or more render version names!',
                button=['OK'], defaultButton='OK',
            )
            return
        
        render_versions_folder, render_release_history_folder = self.scene.create_dept_folders("ren")
        
        for cam_dict in self.camera_dicts:
            cam = cam_dict["camera"]
            cam_choice = cam_dict["radioButtonGrp"].getSelect()
            # 1: export/ref, 2: Remove 3: Nothing
            if cam_choice == 1:
                env_var_name = pc.mel.eval('getenv "env_var_name"')
                env_var_path = pc.mel.eval('getenv "{}"'.format(env_var_name))
                exported_file = export_cam(cam, self.scene)
                cam_ref_file = "${}".format(
                    exported_file.replace(env_var_path, env_var_name)
                )
                pc.createReference(cam_ref_file, namespace=cam_dict["camera"].name())

            if cam_choice in [1, 2]:
                pc.delete(cam)

        for ref in self.reference_dicts:
            choice = ref["radioButtonGrp"].getSelect()
            if choice == 1:
                ref["scene"].reference("shd", "{}_shd".format(ref["scene"].name))
            if choice in [1, 2]:
                ref["reference"].remove()

        saved_file_name = normpath(
            pc.saveAs("/".join([
                render_versions_folder,
                self.scene.create_version_file_name("ren", self.user, variant=scene_names.pop(0))
            ]))
        )

        for scene_name in scene_names:
            copyfile(
                saved_file_name, 
                "/".join([
                    render_versions_folder,
                    self.scene.create_version_file_name("ren", self.user, variant=scene_name)
                ])
            )
        
        if self.out_layout:
            self.out_layout()


def create_render_version(scene, dept, *args, **kwargs):
    crv = CreateRenderVersion(scene, dept, *args, **kwargs)


def ui(parent_cl, scene, dept, *args, **kwargs):
    pc.button(
        p=parent_cl, label="Create Render Versions ...", bgc= COLOR.add_green,
        c=pc.Callback(create_render_version, scene, dept, *args, **kwargs)
    )
