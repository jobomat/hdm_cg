import os
import json

import pymel.core as pc

from cg.maya.files.paths import normpath
import cg.maya.viewport.capture as capture
from cg.maya.ui.widgets import file_chooser_button
import cg.maya.minipipe.utils as mp_utils
from cg.maya.env.io import load_env_json, save_env_json
import cg.maya.minipipe.core as mp_core

reload(capture)
reload(mp_utils)
reload(mp_core)


class MainWindow():
    def __init__(self, rebuild_win=False):
        self.window_name = "minipipe_win"
        self.main_fl = None     # main formLayout
        self.toolbar_cl = None  # the main toolbar columnLayout
        self.content_sl = None  # the main content scrollLayout
        self.resolution_intFieldGrp = None
        self.framerate_intFieldGrp = None
        self.scene_lister = None
        self.info_panel = None
        self.in_button = None
        self.out_button = None
        self.settings_button = None
        self.tool_buttons = []

        self.last_selected_scene = None

        self.main_padding = 5
        self.status_color = {
            "info": (0.2, 0.2, 0.2),
            "warning": (1.0, 0.8, 0.23),
            "error": (0.9, 0.0, 0.0),
            "success": (0.0, 0.65, 0.0)
        }
        
        self.minipipe_templates_dir = normpath(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "minipipe", "setup_templates"
            )
        )

        self.user = load_env_json("GLOBAL_CONFIG_FILE").get(
            "MINIPIPE_USER",
            mp_utils.get_system_user()
        )

        self.reload_config()

        self.main_window(rebuild_win)

    def main_window(self, rebuild_win):
        if pc.window(self.window_name, exists=True):
            if rebuild_win:
                pc.deleteUI(self.window_name)
            else:
                pc.showWindow(self.window_name)
                return

        with pc.window(self.window_name, title="Minipipe") as self.win:
            with pc.formLayout(numberOfDivisions=100) as self.main_fl:
                with pc.columnLayout(adj=True) as self.toolbar_cl:
                    pass
                with pc.formLayout() as self.content_sl:
                    pass
                with pc.columnLayout(bgc=self.status_color["info"], adj=True) as self.info_cl:
                    pass
          
        self.main_fl.attachForm(self.toolbar_cl, "top", self.main_padding)
        self.main_fl.attachForm(self.toolbar_cl, "left", self.main_padding)
        self.main_fl.attachForm(self.toolbar_cl, "right", self.main_padding)

        self.main_fl.attachForm(self.content_sl, "left", self.main_padding)
        self.main_fl.attachForm(self.content_sl, "right", self.main_padding)

        self.main_fl.attachForm(self.info_cl, "left", self.main_padding)
        self.main_fl.attachForm(self.info_cl, "right", self.main_padding)
        self.main_fl.attachForm(self.info_cl, "bottom", self.main_padding)

        self.main_fl.attachControl(
            self.content_sl, "top", self.main_padding, self.toolbar_cl
        )
        self.main_fl.attachControl(
            self.content_sl, "bottom", self.main_padding, self.info_cl
        )
        self.main_fl.attachNone(self.toolbar_cl, "bottom")
        self.main_fl.attachNone(self.info_cl, "top")

        self.info_cl.setHeight(20)

        self.update_toolbar()
        if self.config.get("env_var_name", False):
            self.in_layout()
        else:
            self.settings_layout()

    def update_toolbar(self):
        self.tool_buttons = []
        self.toolbar_cl.setHeight(54)
        flags = {
            "flat": True,
            "height": 48, "width": 48,
            "style": "iconAndTextVertical", 
        }

        for child in self.toolbar_cl.getChildren():
            pc.deleteUI(child)

        pc.flowLayout(columnSpacing=5, p=self.toolbar_cl)
        if self.config.get("env_var_name", False):
            self.in_button = pc.iconTextButton(
                label="In", image="in.png", ann="Browse, add, open, reference Assets & Shots.",
                c=pc.Callback(self.in_layout), **flags
            )
            self.tool_buttons.append(self.in_button)
            self.out_button = pc.iconTextButton(
                label="Out", image="out.png", ann="Save Version, Release or Cache from current scene which is already part of pipeline",
                c=pc.Callback(self.out_layout), **flags
            )
            self.tool_buttons.append(self.out_button)
        self.settings_button = pc.iconTextButton(
            label="Settings", image="settings.png", ann="Edit Minipipe-Settings, Create Minipipe-Project",
            c=pc.Callback(self.settings_layout), **flags
            )
        self.tool_buttons.append(self.settings_button)
        pc.setParent("..")

    def highlight_button(self, button):
        for btn in self.tool_buttons:
            btn.setBackgroundColor([.27,.27,.27])
        button.setBackgroundColor([.5,.5,.5])

    def in_layout(self, *args, **kwargs):
        self.clear_main_content()
        self.highlight_button(self.in_button)

        mp_utils.set_maya_project_env(self.config)
        mp_utils.set_maya_project(self.config)
        # mp_core.Scene.reload_scene_types()

        with pc.formLayout(parent=self.content_sl) as fl:
            with pc.columnLayout(adj=True, rs=5) as tools:
                pc.separator()
                with pc.rowLayout(nc=len(mp_core.Scene.types) + 1):
                    pc.text(label="CREATE NEW: ", font="boldLabelFont")
                    for scene_type in mp_core.Scene.types:
                        pc.button(
                            label=scene_type["nice_name"], w=60,
                            c=pc.Callback(self.add_asset, scene_type)
                        )
                pc.separator()
            with pc.paneLayout(configuration='vertical2', paneSize=[1, 45, 100]) as pl:
                self.scene_lister = pc.treeLister()
                with pc.formLayout(bgc=[0.23, 0.23, 0.23]) as self.info_panel:
                    nothing_text = pc.text(label="Nothing selected.", h=200)
                self.info_panel.attachForm(nothing_text, "left", 0)
                self.info_panel.attachForm(nothing_text, "right", 0)


        pc.treeLister(
            self.scene_lister, e=True, 
            add=[
                (sl.relative_path, sl.icon, self.update_info_factory(sl)) 
                for sl in mp_core.get_scene_list()
            ]
        )

        self.content_sl.attachForm(fl, "top", 0)
        self.content_sl.attachForm(fl, "left", 0)
        self.content_sl.attachForm(fl, "right", 0)
        self.content_sl.attachForm(fl, "bottom", 0)
        fl.attachForm(tools, "left", 0)
        fl.attachForm(tools, "right", 0)
        fl.attachForm(pl, "left", 0)
        fl.attachForm(pl, "right", 0)
        fl.attachForm(pl, "bottom", 0)
        fl.attachControl(pl, "top", 0, tools)

        if self.last_selected_scene:
            self.update_info_panel(self.last_selected_scene, *args, **kwargs)

    def update_info_panel(self, scene, *args, **kwargs):
        #dept_dropdown_sel = kwargs.get("dept_dropdown_sel", "")
        current_scene, cs_dept, cs_user, cs_time, cs_version, cs_variant = mp_core.scene_from_open_file()
        for child in self.info_panel.getChildren():
            pc.deleteUI(child)

        self.last_selected_scene = scene
        scene.get_status()

        self.info_panel.setEnableBackground(False)

        with pc.frameLayout(label=scene.name, p=self.info_panel, mh=2, mw=2) as ml:
            with pc.scrollLayout(childResizable=True) as sl:
                with pc.columnLayout(adj=True, rs=5):
                    with pc.optionMenu(bgc=(0.09, 0.25, 0.37), h=30,
                                       cc=pc.Callback(self.update_in, scene)) as self.dept_optionMenu:
                        sel = 1
                        for i, dept in enumerate(scene.get_depts()):
                            if cs_dept == dept:
                                sel = i + 1
                            pc.menuItem(
                                label=mp_utils.get_nested_dict(self.config["depts"], dept, "nice_name", dept)
                            )
                    self.dept_optionMenu.setSelect(sel)
                    with pc.frameLayout(label="Suggested In Actions", collapsable=True) as self.dynamic_action_fl:
                        self.update_in(scene)

                    with pc.frameLayout(label="Other Actions", collapsable=True, cl=True):
                        pass

        self.info_panel.attachForm(ml, "top", 0)
        self.info_panel.attachForm(ml, "bottom", 0)
        self.info_panel.attachForm(ml, "left", 0)
        self.info_panel.attachForm(ml, "right", 0)
    
    def update_in(self, scene, *args):
        current_scene, cs_dept, cs_user, cs_time, cs_version, cs_variant = mp_core.scene_from_open_file()
        # if current_scene:
        #     current_scene.get_status()
        dept = scene.get_depts()[self.dept_optionMenu.getSelect() - 1]
        self.dept_optionMenu.setBackgroundColor(
            mp_utils.get_nested_dict(self.config, "depts", dept, "color", (0.3, 0.3, 0.3))
        )
        self.update_dynamic_actions_fl(
            scene, dept, "in", *args, in_layout=self.in_layout,
            current_scene=current_scene, current_scene_dept=cs_dept, variant=cs_variant
        )


    def update_dynamic_actions_fl(self, scene, dept, direction, *args, **kwargs):
        actions = mp_utils.get_nested_dict(
            self.config, "actions", direction, scene.type["name"], dept, []
        )
        for child in self.dynamic_action_fl.getChildren():
            pc.deleteUI(child)

        with pc.columnLayout(adj=True, p=self.dynamic_action_fl, rs=4) as cl:
            mp_core.create_dynamic_actions_ui(
                cl, actions, scene, dept, *args,
                user=self.user, update_status_message=self.update_status_message,
                config=self.config, **kwargs
            )

    def out_layout(self):
        self.clear_main_content()
        self.highlight_button(self.out_button)

        mp_utils.set_maya_project_env(self.config)
        mp_utils.set_maya_project(self.config)
        mp_core.Scene.reload_scene_types()
                
        scene, dept, user, time, version, variant = mp_core.scene_from_open_file()
        if scene:
            scene.get_status()

        with pc.formLayout(parent=self.content_sl) as fl:
            sep = pc.separator(h=8)
            pane_width = 30000 / self.win.getWidth()
            with pc.paneLayout(configuration='vertical2', paneSize=[1, pane_width, 100],
                               separatorMovedCommand=self.scale_thumb) as self.out_pl:
                with pc.columnLayout(adj=True):
                    if scene:
                        pc.text(
                            label=scene.name, font="boldLabelFont", h=30, 
                            bgc=mp_utils.get_nested_dict(self.config, "depts", dept, "color", [0.05, 0.5, 0.89])
                        )
                        v = "{}".format("V {}".format(version) if version else "Release")
                        pc.textFieldGrp(
                            label="Version:", text=v, editable=False, cw2=[100,1], adj=2
                        )
                        pc.textFieldGrp(
                            label="Type:", text=scene.type["nice_name"], editable=False,
                             cw2=[100,1], adj=2
                        )
                        pc.textFieldGrp(
                            label="Department:", editable=False, cw2=[100,1], adj=2,
                            text=mp_utils.get_nested_dict(self.config, "depts", dept, "nice_name", dept)
                        )
                        pc.textFieldGrp(
                            label="Created by:", text=user or " ", editable=False,
                             cw2=[100,1], adj=2
                        )
                        pc.textFieldGrp(
                            label="Creation Date:", text=scene.get_nice_time(time), editable=False,
                             cw2=[100,1], adj=2
                        )
                        with pc.columnLayout():
                            self.thumb_btn = pc.iconTextButton(
                                image1=scene.icon,  w=160, scaleIcon=False,
                                c=pc.Callback(self.create_thumb, scene)
                            )
                    else:
                        pc.text(label="No Project Scene loaded", font="boldLabelFont")
                        pc.separator(h=25)
                        with pc.rowLayout(nc=2):
                            pc.text(label="'{}'".format(pc.sceneName() or "untitled"), font="boldLabelFont")
                            pc.text(label="is not part of the Minipipe project or")
                        pc.text(label="is not named according to the Minipipe", align="left")
                        pc.text(label="naming conventions.", align="left")

                with pc.scrollLayout(childResizable=True) as sl:
                    with pc.columnLayout(adj=True, rs=5):
                        if scene:
                            with pc.frameLayout(lv=False, collapsable=False) as self.dynamic_action_fl:
                                self.update_dynamic_actions_fl(
                                    scene, dept, "out", 
                                    out_layout=self.out_layout, variant=variant
                                )
                        else:
                            pc.text(label="No Actions availible.")

        self.content_sl.attachForm(fl, "top", 0)
        self.content_sl.attachForm(fl, "left", 0)
        self.content_sl.attachForm(fl, "right", 0)
        self.content_sl.attachForm(fl, "bottom", 0)
        fl.attachForm(sep, "top", 0)
        fl.attachForm(sep, "left", 0)
        fl.attachForm(sep, "right", 0)
        fl.attachForm(self.out_pl, "left", 0)
        fl.attachForm(self.out_pl, "right", 0)
        fl.attachForm(self.out_pl, "bottom", 0)
        fl.attachControl(self.out_pl, "top", 0, sep)

        if scene:
            self.scale_thumb()

    def create_thumb(self, scene):
        capture.screenshot(
            viewportsize=[320, 180], enable_ui=False, formats=["jpg"],
            save_path=scene.absolute_path, filename="thumb", callback=self.reload_thumb
        )

    def reload_thumb(self, f, w, h):
        self.thumb_btn.setImage1(f)
        self.scale_thumb()

    def scale_thumb(self):
        w = int(self.win.getWidth() * self.out_pl.getPaneSize()[0] / 107)
        h = w * self.config["image_resolution"][1] / self.config["image_resolution"][0]
        self.thumb_btn.setHeight(h)
        self.thumb_btn.setWidth(w)


    def settings_layout(self):
        self.clear_main_content()
        self.highlight_button(self.settings_button)

        frameLayoutFlags = {
            "cll": True, "bgs": True, "mh": 5, "mw": 5
        }
        with pc.columnLayout(parent=self.content_sl, adj=True, rs=5) as cl:
            with pc.frameLayout(label="Config File", **frameLayoutFlags):
                with pc.columnLayout(adj=True, rs=5):
                    self.current_config_button = file_chooser_button(
                        label="Current Config File", fileMode=1, bl="Choose Config",
                        callback=self.change_config, text=mp_utils.get_config_file(),
                        fileFilter="JSON (*.json)",  okCaption="Load Settings",
                        caption="Load Settings from JSON-File"
                    )
                    self.resolution_intFieldGrp = pc.intFieldGrp(
                        numberOfFields=2, label='Image Resolution',
                        extraLabel='px',  cal=[1, "left"],
                        value1=self.config["image_resolution"][0],
                        value2=self.config["image_resolution"][1]
                    )
                    self.framerate_intFieldGrp = pc.intFieldGrp(
                        numberOfFields=1, label='Framerate',
                        extraLabel='fps',  cal=[1, "left"],
                        value1=self.config["framerate"]
                    )
                    self.render_base_path_textFieldGrp = pc.textFieldGrp(
                        label='Path at Render Location',
                        cal=[1, "left"],
                        text="M:/paradise/PARADISE/3d"
                    )
                    self.env_var_info_textFieldGrp = pc.textFieldGrp(
                        label='Name of Env Var',
                        cal=[1, "left"], editable=False,
                        text=self.config.get("env_var_name", "")
                    )
                    pc.button(label="Save to Minipipe Config File", c=self.save_config)

            with pc.frameLayout(label="Current User", **frameLayoutFlags):
                with pc.columnLayout(adj=True, rs=5):
                    self.user_name_textFieldBtn = pc.textFieldButtonGrp(
                        label="Username (Supershort)", adj=2, cal=[1, "left"],
                        text=self.user,
                        buttonCommand=self.save_user_to_config, 
                        buttonLabel="Save to Global Config File"
                    )

            with pc.frameLayout(label="Minipipe Starter", **frameLayoutFlags):
                with pc.columnLayout(adj=True, rs=5):
                    # pc.separator(h=1)
                    self.base_path_button = file_chooser_button(
                        label="Base Path", fileMode=3, okCaption="Set Folder",
                        callback=self.extract_env_var_name
                    )
                    self.mp_template_dir_button = file_chooser_button(
                        label="Minipipe Template Dir", fileMode=3, okCaption="Choose Template",
                        startingDirectory=self.minipipe_templates_dir
                    )
                    self.env_var_name_textField = pc.textFieldGrp(
                        label="Env. Variable Name", adj=2, cal=[1, "left"]
                    )
                    with pc.horizontalLayout():
                        pc.button(
                            label="Simulate Folder Creation",
                            c=pc.Callback(self.create_minipipe_project, simulate=True)
                        )
                        pc.button(
                            label="Create Project",
                            c=pc.Callback(self.create_minipipe_project)
                        )

            with pc.frameLayout(label="Update", **frameLayoutFlags):
                with pc.columnLayout(adj=True, rs=5):
                    # self.mp_template_dir_update_button = file_chooser_button(
                    #     label="Minipipe Template Dir", fileMode=3, okCaption="Choose Template",
                    #     startingDirectory=self.minipipe_templates_dir
                    # )
                    pc.text(label="This is recommended if you downloaded a new version of the Minipipe scripts.")
                    pc.button(
                        label="Update IN and OUT actions.",
                        c=pc.Callback(self.update_actions)
                    )
                        
        self.content_sl.attachForm(cl, "top", 0)
        self.content_sl.attachForm(cl, "left", 0)
        self.content_sl.attachForm(cl, "right", 0)
        self.content_sl.attachForm(cl, "bottom", 0)

    def update_actions(self, *args):
        # mp_template_dir = self.mp_template_dir_update_button.getText()
        # if not mp_template_dir:
        #     pc.warning("Please select a template to update the actions from.")
        #     return
        mp_utils.update_actions(self.config)
        self.reload_config()

    def add_asset(self, scene_type):
        result = pc.promptDialog(
            title='New {}'.format(scene_type["nice_name"]),
            message='Enter {}s Name \n(Or comma separted names):'.format(scene_type["nice_name"]),
            button=['OK', 'Cancel'],
            defaultButton='OK',
            cancelButton='Cancel',
            dismissString='Cancel'
        )
        if result != 'OK':
            return False
        
        names = [
            mp_utils.to_valid_file_name(n)
            for n in pc.promptDialog(query=True, text=True).split(",")
        ]
        msg = ("success", "'{}' created.".format(", ".join(names)))
        for name in names:
            new_scene = mp_core.Scene(name, scene_type)
            if new_scene.create_asset_dirs(self.user):
                self.update_scene_lister(new_scene)
                #self.update_info_panel
                print("'{}' created.".format(name))
            else:
                msg = ("error", "There have been errors. Check Script Editor!")
                print("Error creating '{}'.".format(name))
                
            self.update_status_message(msg)

    def create_minipipe_project(self, simulate=False):
        destination = self.base_path_button.getText()
        mp_template_dir = self.mp_template_dir_button.getText()
        env_var_name = self.env_var_name_textField.getText()

        if destination and mp_template_dir and env_var_name:
            msg = mp_utils.create_minipipe_project(
                destination, mp_template_dir, env_var_name, simulate
            )
            self.update_status_message(msg)
            if msg[0] == "success":
                self.reload_config()
                mp_utils.setup_maya()
                self.update_settings_layout()
                mp_utils.set_maya_project(self.config)
                self.update_toolbar()
        else:
            pc.warning("Please specify Base Path, Template and Env Var Name.")

    def reload_config(self):
        self.config = mp_utils.load_config()

    def change_config(self, mp_config_json):
        if not mp_config_json:
            self.update_status_message(("info", "Aborted."))
            return False

        mp_utils.change_config_file(mp_config_json)
        self.reload_config()
        self.update_settings_layout()
        self.update_toolbar()
        self.update_status_message(("success", "Config '{}' loaded.".format(mp_config_json)))
        return True

    def save_config(self, *args):
        self.config["image_resolution"] = (
            self.resolution_intFieldGrp.getValue1(),
            self.resolution_intFieldGrp.getValue2()
        )
        self.config["framerate"] = self.framerate_intFieldGrp.getValue1()
        self.config["render_base_path"] = self.render_base_path_textFieldGrp.getText()
        if mp_utils.save_config(self.config):
            self.update_status_message(("success", "Minipipe Config saved."))

    def save_user_to_config(self, *args):
        name = self.user_name_textFieldBtn.getText()
        name = mp_utils.to_valid_file_name(name)
        global_config = load_env_json("GLOBAL_CONFIG_FILE")
        global_config["MINIPIPE_USER"] = name
        save_env_json(global_config, "GLOBAL_CONFIG_FILE")
        self.user = name

    def extract_env_var_name(self, base_dir):
        """
        Create a possible ENV-VAR name from the chosen base directory name.
        """
        if self.env_var_name_textField.getText():
            return True
        if not base_dir:
            return True
        base_dir = normpath(base_dir).split("/")[-1].strip().replace(" ","_").upper()
        self.env_var_name_textField.setText(base_dir)
        return True

    def clear_main_content(self, *args):
        """
        Helper method to delete children of main gui area.
        """
        for child in self.content_sl.getChildren():
            pc.deleteUI(child)

    def update_status_message(self, msg):
        self.info_cl.setBackgroundColor(self.status_color[msg[0]])
        for child in self.info_cl.getChildren():#
            pc.deleteUI(child)
        pc.text(label=msg[1], parent=self.info_cl, align="left")

    def update_settings_layout(self):
        self.current_config_button.setText(mp_utils.get_config_file())
        pc.intFieldGrp(
            self.resolution_intFieldGrp, edit=True,
            value1=self.config["image_resolution"][0],
            value2=self.config["image_resolution"][1]
        )
        pc.intFieldGrp(
            self.framerate_intFieldGrp, edit=True,
            value1=self.config["framerate"]
        )
        self.env_var_info_textFieldGrp.setText(self.config["env_var_name"])

    def update_info_factory(self, scene):
        def h():
            self.update_info_panel(scene)
        return h

    def update_scene_lister(self, scene):
        pc.treeLister(
            self.scene_lister, e=True, 
            add=[(
                scene.relative_path,
                scene.icon,
                self.update_info_factory(scene)
            )]
        )
