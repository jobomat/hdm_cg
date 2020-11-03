import pymel.core as pc
from os import getenv
from cg.maya.files.paths import normpath


class Checker():
    def __init__(self, env_var_name, fps, unit):
        self.env_var_name = env_var_name
        self.project_dir = normpath(pc.workspace.path)
        self.project_fps = fps
        self.project_unit = unit
        self.fps_map = {
            "game": 15,
            "film": 24,
            "pal": 25,
            "ntsc": 30,
            "show": 48,
            "palf": 50,
            "ntscf": 60,
        }

    def gui(self):
        win_id = "env_checker_window"
        icon_width = 30
        message_width = 300
        action_width = 150
        cw3 = [icon_width, message_width, action_width]
        margin = 7
        window_width = icon_width + message_width + action_width + 2 * margin
        window_height = 210

        if pc.window(win_id, q=1, exists=1):
            pc.deleteUI(win_id)

        with pc.window(win_id, title="Status", wh=[window_width, window_height]) as self.win:
            with pc.frameLayout(borderVisible=True, labelVisible=False,
                                marginWidth=margin, marginHeight=margin):
                with pc.columnLayout(adj=True, rs=6):
                    with pc.rowLayout(nc=3, cw3=cw3):
                        self.env_icon = pc.image(i="waitBusy.png")
                        self.env_status = pc.text(label="")
                        self.env_textfield = pc.textField(
                            text=self.env_var_name, w=action_width - 2 * margin,
                            tcc=self.update_gui
                        )
                    pc.separator(h=2)
                    with pc.rowLayout(nc=3, cw3=cw3):
                        self.proj_icon = pc.image(i="waitBusy.png")
                        self.proj_status = pc.text(label="")
                        self.proj_button = pc.button(
                            label="Set to Env-Path", w=action_width - 2 * margin,
                            c=self.set_project_to_env_path
                        )
                    pc.separator(h=2)
                    self.envpath_text = pc.text(label="", align="left", font="smallFixedWidthFont")
                    self.project_text = pc.text(label="", align="left", font="smallFixedWidthFont")
                    pc.separator(h=2)
                    with pc.rowLayout(nc=3, cw3=cw3):
                        self.fps_icon = pc.image(i="waitBusy.png")
                        self.fps_status = pc.text(label="")
                        self.fps_button = pc.button(
                            label="Set to project fps", w=action_width - 2 * margin,
                            c=pc.Callback(
                                pc.currentUnit,
                                time=[k for k in self.fps_map if self.fps_map[k] == self.project_fps][0]
                            )
                        )
                    pc.separator(h=2)
                    with pc.rowLayout(nc=3, cw3=cw3):
                        self.unit_icon = pc.image(i="waitBusy.png")
                        self.unit_status = pc.text(label="")
                        self.unit_button = pc.button(
                            label="Set to project unit", w=action_width - 2 * margin,
                            c=pc.Callback(pc.currentUnit, linear=self.project_unit)
                        )

        self.win.setWidthHeight([window_width, window_height])

        self.update_gui()
        self.script_jobs = [
            pc.scriptJob(e=("workspaceChanged", self.update_gui)),
            pc.scriptJob(e=("linearUnitChanged", self.update_gui)),
            pc.scriptJob(e=("timeUnitChanged", self.update_gui))
        ]
        pc.window(self.win, edit=True, closeCommand=self.kill_script_jobs)

    def kill_script_jobs(self):
        for job in self.script_jobs:
            pc.scriptJob(kill=job, force=True)

    def update_gui(self, *args):
        checks_passed = []
        self.project_dir = normpath(pc.workspace.path)
        self.env_var_name = self.env_textfield.getText()
        env_var_path = getenv(self.env_var_name) or ""
        env_var_path = env_var_path.split(";")[0]
        project_dir = normpath(pc.workspace.path)
        self.udapte_project_text(project_dir)

        if env_var_path:
            checks_passed.append(True)
            self.env_icon.setImage("confirm.png")
            self.env_status.setLabel("Environment variable named '{}' found.".format(self.env_var_name))
            self.env_var_path = normpath(getenv(self.env_var_name))
            self.udapte_envpath_text(self.env_var_path)
            if self.env_var_path == project_dir:
                self.proj_icon.setImage("confirm.png")
                checks_passed.append(True)
                self.proj_status.setLabel("Project path and Env-Var-Path are matching.")
            else:
                checks_passed.append(False)
                self.proj_icon.setImage("error.png")
                self.proj_status.setLabel("Project path differs from Env-Var-Path!")
        else:
            checks_passed.append(False)
            self.env_icon.setImage("error.png")
            self.proj_icon.setImage("error.png")
            self.udapte_envpath_text("Fix environment variable name.")
            if self.env_var_name:
                self.env_status.setLabel(
                    "Environment variable named '{}' not found!".format(self.env_var_name)
                )
                self.proj_status.setLabel("No valid environment variable name specified.")
            else:
                self.env_status.setLabel("No environment variable specified!")
                self.proj_status.setLabel("No environment variable specified!")

        scene_fps = self.fps_map[pc.currentUnit(q=True, time=True)]
        if scene_fps == self.project_fps:
            checks_passed.append(True)
            self.fps_icon.setImage("confirm.png")
            self.fps_status.setLabel(
                "Scene framerate matches project framerate. ({} fps)".format(self.project_fps)
            )
        else:
            checks_passed.append(False)
            self.fps_icon.setImage("error.png")
            self.fps_status.setLabel(
                "Unmatching scene and project framerate! ({} vs. {} fps)".format(
                    scene_fps, self.project_fps
                )
            )
        scene_unit = pc.currentUnit(q=True, linear=True)
        if scene_unit == self.project_unit:
            checks_passed.append(True)
            self.unit_icon.setImage("confirm.png")
            self.unit_status.setLabel(
                "Scene unit matches project unit. ({})".format(self.project_unit)
            )
        else:
            checks_passed.append(False)
            self.unit_icon.setImage("error.png")
            self.unit_status.setLabel(
                "Unmatching scene and project unit! ({} vs. {})".format(
                    scene_unit, self.project_unit
                )
            )

        self.win.setTitle(
            "Status: All good to go!" if all(checks_passed) else "Status: There are Warnings."
        )

    def set_project_to_env_path(self, *args):
        path = self.env_var_path.split(";")[0]
        path = path if path[-1] != ":" else "{}/".format(path)
        pc.mel.setProject(path)
        self.update_gui()

    def udapte_project_text(self, text):
        self.project_text.setLabel("PROJECT:  {}".format(text))

    def udapte_envpath_text(self, text):
        self.envpath_text.setLabel("ENV-PATH: {}".format(text))
