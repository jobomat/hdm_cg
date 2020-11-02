from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import pymel.core as pc
import maya.cmds as cmds
import threading
import os
import time
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
import platform
import subprocess
import json


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class BackgroundPlayblast(MayaQWidgetDockableMixin, QtWidgets.QDialog):

    # JSON_PATH = os.path.join(os.getenv("PIPE_PIPELINEPATH"), "pipeline", "PIPELINE_CONSTANTS.json")

    IMAGE_FORMAT_LIB = {
        "png": 32,
        "jpg": 8,
        "exr": 40,
    }

    FRAME_RATE_LIB = {
        "film": 24,
        "game": 15,
        "pal": 25,
        "ntsc": 30,
        "show": 48,
        "palf": 50,
        "ntscf": 60
    }

    MAYA_VERSION = pc.versions.shortName()

    if platform.system() == "Darwin":
        RENDERER_PATH = "/Applications/Autodesk/maya{}/Maya.app/Contents/bin/Render".format(MAYA_VERSION)
        MAYAPY_PATH = "/Applications/Autodesk/maya{}/Maya.app/Contents/bin/mayapy".format(MAYA_VERSION)
        DJV_PATH = "/Applications/DJV.app/Contents/MacOS/DJV"
        FFMPEG_PATH = str(
            os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "ffmpeg_mac",
                "ffmpeg"
            )
        )
    elif platform.system() == "Windows":
        RENDERER_PATH = "C:/Program Files/Autodesk/Maya{}/bin/Render.exe".format(MAYA_VERSION)
        MAYAPY_PATH = "C:/Program Files/Autodesk/Maya{}/bin/mayapy.exe".format(MAYA_VERSION)
        RV_PATH = "C:/Program Files/Shotgun/RV-7.3.1/bin/rv.exe"
        FFMPEG_PATH = str(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "ffmpeg",
                "ffmpeg.exe")
        )

    def __init__(self, parent=maya_main_window()):
        super(BackgroundPlayblast, self).__init__(parent)

        self.setWindowTitle("BackgroundPlayblast")
        self.setMinimumWidth(280)

        # Remove the ? from the dialog on Windows
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.create_widgets()
        self.create_layouts()
        self.connect_widgets()
        self.set_initial_state()

    def create_widgets(self):
        # self.setStyleSheet(r"QGroupBox {font: bold 14px}")
        self.setStyleSheet(r"QPushButton:hover{background: #278cbc; color: black} QGroupBox {font: bold 14px}")

        self.from_frame_lineedit = QtWidgets.QLineEdit()
        self.from_frame_lineedit.setMaximumWidth(60)
        self.to_frame_lineedit = QtWidgets.QLineEdit()
        self.to_frame_lineedit.setMaximumWidth(60)
        self.frame_range_label_02 = QtWidgets.QLabel("start: ")
        self.frame_range_label_03 = QtWidgets.QLabel("end: ")

        self.image_size_combobox = QtWidgets.QComboBox()
        self.image_size_combobox.addItem("HD 1080", [1920, 1080])
        self.image_size_combobox.addItem("HD 720", [1280, 720])
        self.image_size_combobox.addItem("HD 540", [960, 540])
        self.image_size_combobox_label = QtWidgets.QLabel("Size: ")

        self.image_format_combobox = QtWidgets.QComboBox()
        self.image_format_combobox.addItem("JPEG", "jpg")
        self.image_format_combobox.addItem("PNG", "png")
        self.image_format_combobox.addItem("EXR", "exr")
        self.image_format_combobox_label = QtWidgets.QLabel("Format: ")

        self.output_directory_lineedit = QtWidgets.QLineEdit()
        self.output_directory_lineedit.setMinimumWidth(130)
        self.output_directory_label = QtWidgets.QLabel("Output: ")
        self.output_directory_button = QtWidgets.QPushButton()
        self.output_directory_button.setIcon(QtGui.QIcon(":fileOpen.png"))
        self.output_directory_dialog = QtWidgets.QFileDialog()

        self.create_mp4_checkbox = QtWidgets.QCheckBox()
        self.create_mp4_checkbox.setChecked(True)
        self.create_mp4_label = QtWidgets.QLabel("Create MP4: ")
        self.burn_in_checkbox = QtWidgets.QCheckBox()
        self.burn_in_checkbox.setChecked(True)
        self.burn_in_label = QtWidgets.QLabel("Burn In: ")

        self.shading_mode_combobox = QtWidgets.QComboBox()
        self.shading_mode_combobox.addItem("Wire", 0)
        self.shading_mode_combobox.addItem("Shaded", 1)
        self.shading_mode_combobox.addItem("Wire + Shaded", 2)
        self.shading_mode_combobox.addItem("Default Material", 3)
        self.shading_mode_combobox.addItem("Shaded + Textured", 4)
        self.shading_mode_combobox.addItem("Wire + Shaded + Textured", 5)
        self.shading_mode_combobox.setCurrentIndex(4)
        self.shading_mode_combobox_label = QtWidgets.QLabel("Shading Mode: ")

        self.xray_mode_checkbox = QtWidgets.QCheckBox()
        self.xray_mode_checkbox_label = QtWidgets.QLabel("X-Ray Mode: ")
        self.hwfog_checkbox = QtWidgets.QCheckBox()
        self.hwfog_checkbox_label = QtWidgets.QLabel("Hardware Fog: ")
        self.dof_checkbox = QtWidgets.QCheckBox()
        self.dof_checkbox_label = QtWidgets.QLabel("Depth Of Field: ")
        self.ao_checkbox = QtWidgets.QCheckBox()
        self.ao_checkbox_label = QtWidgets.QLabel("Ambient Occlusion: ")
        self.smooth_wireframe_checkbox = QtWidgets.QCheckBox()
        self.smooth_wireframe_checkbox_label = QtWidgets.QLabel("Smooth Wireframe: ")
        self.aa_checkbox = QtWidgets.QCheckBox()
        self.aa_checkbox_label = QtWidgets.QLabel("Anti-Alising: ")
        self.mask_checkbox_label = QtWidgets.QLabel("Mask")
        self.mask_checkbox = QtWidgets.QCheckBox()

        self.background_color_button = QtWidgets.QPushButton()
        self.background_color_button.setStyleSheet("background-color: rgb(73, 73, 73);")
        self.background_color_dialog = QtWidgets.QColorDialog(self)
        self.background_color_dialog.setCurrentColor(QtGui.QColor(73, 73, 73))
        self.background_color_slider_label = QtWidgets.QLabel("Background Colour")

        self.project_name_lineedit = QtWidgets.QLineEdit()
        self.project_name_label = QtWidgets.QLabel("Project Name: ")
        self.project_name_label.setMinimumWidth(80)
        self.shot_name_lineedit = QtWidgets.QLineEdit()
        self.shot_name_label = QtWidgets.QLabel("Shot Name: ")
        self.shot_name_label.setMinimumWidth(80)
        self.comment_lineedit = QtWidgets.QLineEdit()
        self.comment_label = QtWidgets.QLabel("Comment: ")
        self.comment_label.setMinimumWidth(80)

        self.create_button = QtWidgets.QPushButton("Create PlayBlast")
        self.cancel_button = QtWidgets.QPushButton("Cancel")

    def create_layouts(self):
        frame_range_box = QtWidgets.QGroupBox("Frame Range")
        frame_range_layout = QtWidgets.QHBoxLayout()
        frame_range_layout.addStretch()
        frame_range_layout.addWidget(self.frame_range_label_02)
        frame_range_layout.addWidget(self.from_frame_lineedit)
        frame_range_layout.addWidget(self.frame_range_label_03)
        frame_range_layout.addWidget(self.to_frame_lineedit)
        frame_range_box.setLayout(frame_range_layout)

        image_format_box = QtWidgets.QGroupBox("Image Format")
        image_format_layout = QtWidgets.QHBoxLayout()
        image_format_layout.addWidget(self.image_size_combobox_label)
        image_format_layout.addWidget(self.image_size_combobox)
        image_format_layout.addStretch()
        image_format_layout.addWidget(self.image_format_combobox_label)
        image_format_layout.addWidget(self.image_format_combobox)
        image_format_box.setLayout(image_format_layout)

        output_directory_box = QtWidgets.QGroupBox("Output Directory")
        output_directory_layout = QtWidgets.QHBoxLayout()
        output_directory_layout.addStretch()
        output_directory_layout.addWidget(self.output_directory_label)
        output_directory_layout.addWidget(self.output_directory_lineedit)
        output_directory_layout.addWidget(self.output_directory_button)
        output_directory_box.setLayout(output_directory_layout)

        ffmpeg_settings_box = QtWidgets.QGroupBox("Ffmpeg Settings")
        ffmpeg_settings_box_main_layout = QtWidgets.QHBoxLayout()
        ffmpeg_settings_box_layout_02 = QtWidgets.QHBoxLayout()
        ffmpeg_settings_box_layout_02.addStretch()
        ffmpeg_settings_box_layout_02.addWidget(self.burn_in_label)
        ffmpeg_settings_box_layout_02.addWidget(self.burn_in_checkbox)
        ffmpeg_settings_box_main_layout.addLayout(ffmpeg_settings_box_layout_02)
        ffmpeg_settings_box_layout_01 = QtWidgets.QHBoxLayout()
        ffmpeg_settings_box_layout_01.addStretch()
        ffmpeg_settings_box_layout_01.addWidget(self.create_mp4_label)
        ffmpeg_settings_box_layout_01.addWidget(self.create_mp4_checkbox)
        ffmpeg_settings_box_main_layout.addLayout(ffmpeg_settings_box_layout_01)
        ffmpeg_settings_box.setLayout(ffmpeg_settings_box_main_layout)

        render_settings_box = QtWidgets.QGroupBox("PlayBlast Options")
        render_settings_box_main_layout = QtWidgets.QVBoxLayout()
        render_settings_box_layout_01 = QtWidgets.QHBoxLayout()
        render_settings_box_layout_01.addStretch()
        render_settings_box_layout_01.addWidget(self.shading_mode_combobox_label)
        render_settings_box_layout_01.addWidget(self.shading_mode_combobox)
        render_settings_box_main_layout.addLayout(render_settings_box_layout_01)
        render_settings_box_layout_02 = QtWidgets.QHBoxLayout()
        render_settings_box_layout_02.addStretch()
        render_settings_box_layout_02.addWidget(self.xray_mode_checkbox_label)
        render_settings_box_layout_02.addWidget(self.xray_mode_checkbox)
        render_settings_box_main_layout.addLayout(render_settings_box_layout_02)
        render_settings_box_layout_03 = QtWidgets.QHBoxLayout()
        render_settings_box_layout_03.addStretch()
        render_settings_box_layout_03.addWidget(self.hwfog_checkbox_label)
        render_settings_box_layout_03.addWidget(self.hwfog_checkbox)
        render_settings_box_main_layout.addLayout(render_settings_box_layout_03)
        render_settings_box_layout_04 = QtWidgets.QHBoxLayout()
        render_settings_box_layout_04.addStretch()
        render_settings_box_layout_04.addWidget(self.dof_checkbox_label)
        render_settings_box_layout_04.addWidget(self.dof_checkbox)
        render_settings_box_main_layout.addLayout(render_settings_box_layout_04)
        render_settings_box_layout_06 = QtWidgets.QHBoxLayout()
        render_settings_box_layout_06.addStretch()
        render_settings_box_layout_06.addWidget(self.ao_checkbox_label)
        render_settings_box_layout_06.addWidget(self.ao_checkbox)
        render_settings_box_main_layout.addLayout(render_settings_box_layout_06)
        render_settings_box_layout_07 = QtWidgets.QHBoxLayout()
        render_settings_box_layout_07.addStretch()
        render_settings_box_layout_07.addWidget(self.smooth_wireframe_checkbox_label)
        render_settings_box_layout_07.addWidget(self.smooth_wireframe_checkbox)
        render_settings_box_main_layout.addLayout(render_settings_box_layout_07)
        render_settings_box_layout_08 = QtWidgets.QHBoxLayout()
        render_settings_box_layout_08.addStretch()
        render_settings_box_layout_08.addWidget(self.aa_checkbox_label)
        render_settings_box_layout_08.addWidget(self.aa_checkbox)
        render_settings_box_main_layout.addLayout(render_settings_box_layout_08)
        render_settings_box_layout_09 = QtWidgets.QHBoxLayout()
        render_settings_box_layout_09.addStretch()
        render_settings_box_layout_09.addWidget(self.mask_checkbox_label)
        render_settings_box_layout_09.addWidget(self.mask_checkbox)
        render_settings_box_main_layout.addLayout(render_settings_box_layout_09)
        render_settings_box_layout_05 = QtWidgets.QHBoxLayout()
        render_settings_box_layout_05.addStretch()
        render_settings_box_layout_05.addWidget(self.background_color_slider_label)
        render_settings_box_layout_05.addWidget(self.background_color_button)
        render_settings_box_main_layout.addLayout(render_settings_box_layout_05)
        render_settings_box.setLayout(render_settings_box_main_layout)

        project_settings_box = QtWidgets.QGroupBox("Project Settings")
        project_settings_box_main_layout = QtWidgets.QVBoxLayout()
        project_settings_box_layout_01 = QtWidgets.QHBoxLayout()
        project_settings_box_layout_01.addWidget(self.project_name_label)
        project_settings_box_layout_01.addWidget(self.project_name_lineedit)
        project_settings_box_main_layout.addLayout(project_settings_box_layout_01)
        project_settings_box_layout_02 = QtWidgets.QHBoxLayout()
        project_settings_box_layout_02.addWidget(self.shot_name_label)
        project_settings_box_layout_02.addWidget(self.shot_name_lineedit)
        project_settings_box_main_layout.addLayout(project_settings_box_layout_02)
        project_settings_box_layout_03 = QtWidgets.QHBoxLayout()
        project_settings_box_layout_03.addWidget(self.comment_label)
        project_settings_box_layout_03.addWidget(self.comment_lineedit)
        project_settings_box_main_layout.addLayout(project_settings_box_layout_03)
        project_settings_box.setLayout(project_settings_box_main_layout)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.create_button)
        button_layout.addWidget(self.cancel_button)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(frame_range_box)
        main_layout.addWidget(image_format_box)
        main_layout.addWidget(output_directory_box)
        main_layout.addWidget(ffmpeg_settings_box)
        main_layout.addWidget(render_settings_box)
        main_layout.addWidget(project_settings_box)
        main_layout.addLayout(button_layout)
        main_layout.addStretch()

    def connect_widgets(self):
        self.cancel_button.clicked.connect(self.close)
        self.output_directory_button.clicked.connect(self.set_ouput_dir)
        self.create_button.clicked.connect(self.create_playblast)
        self.background_color_button.clicked.connect(self.get_background_colour)
        self.background_color_dialog.currentColorChanged.connect(self.change_button_colour)
        self.from_frame_lineedit.editingFinished.connect(self.set_end_frame)
        self.to_frame_lineedit.editingFinished.connect(self.set_start_frame)

    def set_initial_state(self):
        self.start_frame = str(pc.animation.playbackOptions(q=1, minTime=1))
        self.end_frame = str(pc.animation.playbackOptions(q=1, maxTime=1))

        self.from_frame_lineedit.setText(self.start_frame)
        self.to_frame_lineedit.setText(self.end_frame)

        self.output_directory_lineedit.setText(self.get_info_from_path()[0])
        self.project_name_lineedit.setText(self.get_project())
        self.shot_name_lineedit.setText(self.get_info_from_path()[1])

    def set_end_frame(self):
        end_frame = float(self.to_frame_lineedit.text())
        start_frame = self.from_frame_lineedit.text()
        if not start_frame.replace(".", "", 1).isdigit():
            self.from_frame_lineedit.setText(str(self.start_frame))
            start_frame = self.start_frame
        start_frame = float(start_frame)
        if end_frame < start_frame:
            self.to_frame_lineedit.setText(str(start_frame))
        self.start_frame = start_frame

    def set_start_frame(self):
        start_frame = float(self.from_frame_lineedit.text())
        end_frame = self.to_frame_lineedit.text()
        if not end_frame.replace(".", "", 1).isdigit():
            self.to_frame_lineedit.setText(str(self.end_frame))
            end_frame = self.end_frame
        end_frame = float(end_frame)
        if end_frame < start_frame:
            self.from_frame_lineedit.setText(str(end_frame))
        self.end_frame = end_frame

    def change_button_colour(self):
        rgb = self.background_color_dialog.currentColor().getRgb()
        r = rgb[0]
        g = rgb[1]
        b = rgb[2]
        self.background_color_button.setStyleSheet("background-color: rgb({}, {}, {});".format(r, g, b))

    def get_background_colour(self):
        self.background_color_dialog.open()

    def set_ouput_dir(self):
        output_dir = self.output_directory_dialog.getExistingDirectory()

        if output_dir == "":
            return

        self.output_directory_lineedit.setText(output_dir)

    def strip_illegal_chars(self, this_string):
        illegal_chars = [
            '\\', '`', '*', '_', '{', '}', '[', ']', '(',
            ')', '>', '#', '+', '-', '.', '!', '$', '\''
        ]
        for char in illegal_chars:
            if char in this_string:
                this_string = this_string.replace(char, "_")
        return this_string

    def collect_info_from_ui(self):
        ui_data_dict = {}

        ui_data_dict["end_frame"] = int(float(self.to_frame_lineedit.text()))
        ui_data_dict["start_frame"] = int(float(self.from_frame_lineedit.text()))
        ui_data_dict["output_dir"] = self.output_directory_lineedit.text()
        ui_data_dict["file_type"] = self.image_format_combobox.itemData(
            self.image_format_combobox.currentIndex())

        widthHeight = self.image_size_combobox.itemData(
            self.image_size_combobox.currentIndex())
        ui_data_dict["width"] = widthHeight[0]
        ui_data_dict["height"] = widthHeight[1]

        ui_data_dict["background"] = self.background_color_dialog.currentColor().getRgbF()

        ui_data_dict["shading_mode"] = self.shading_mode_combobox.itemData(
            self.shading_mode_combobox.currentIndex())

        ui_data_dict["xray_mode"] = self.xray_mode_checkbox.isChecked()
        ui_data_dict["hwfog"] = self.hwfog_checkbox.isChecked()
        ui_data_dict["dof"] = self.dof_checkbox.isChecked()
        ui_data_dict["ao"] = self.ao_checkbox.isChecked()
        ui_data_dict["aa"] = self.aa_checkbox.isChecked()
        ui_data_dict["smooth_wireframe"] = self.smooth_wireframe_checkbox.isChecked()

        ui_data_dict["project_name"] = ""
        ui_data_dict["shot_name"] = ""
        ui_data_dict["comment"] = "playBlast"

        if self.project_name_lineedit.text() != "":
            ui_data_dict["project_name"] = self.strip_illegal_chars(self.project_name_lineedit.text())
        if self.shot_name_lineedit.text != "":
            ui_data_dict["shot_name"] = self.strip_illegal_chars(self.shot_name_lineedit.text())
        if self.comment_lineedit.text() != "":
            ui_data_dict["comment"] = self.strip_illegal_chars(self.comment_lineedit.text())

        ui_data_dict["mask"] = self.mask_checkbox.isChecked()

        ui_data_dict["playblast_name"] = "{}_{}_{}".format(
            ui_data_dict["project_name"],
            ui_data_dict["shot_name"],
            ui_data_dict["comment"]
        )

        return ui_data_dict

    def collect_info_from_scene(self):
        scene_data_dict = {}
        scene_data_dict["camera"] = pc.windows.modelPanel(pc.getPanel(withFocus=1), q=1, cam=1)
        scene_data_dict["frame_rate"] = pc.currentUnit(q=1, t=1)
        scene_data_dict["scene_name"] = cmds.file(q=True, sn=True)
        scene_data_dict["time_stamp"] = time.asctime(time.localtime(time.time()))
        current_scene_path = pc.sceneName()
        temp_scene_path = current_scene_path.split(".")
        temp_scene_path.insert(-1, "_TEMP_")
        temp_scene_path = ".".join(temp_scene_path)
        scene_data_dict["temp_scene_path"] = temp_scene_path

        beta_script_path = current_scene_path.split("/")
        beta_script_path[-1] = "playblast_beta.py"
        scene_data_dict["beta_script_path"] = "/".join(beta_script_path)

        return scene_data_dict

    def generate_render_command(self, output, name, start, end, camera, width, height, scene):
        render_command = " ".join([
            '"{render_location}"',
            '-r hw2',
            '-rd "{output}"',
            '-im "{name}"',
            '-s {start}',
            '-e {end}',
            '-pad 4',
            '-cam "{camera}"',
            '-x {width}',
            '-y {height}',
            '-percentRes 100',
            '"{scene}"'
        ]).format(
            render_location=self.RENDERER_PATH,
            output=output,
            name=name,
            start=start,
            end=end,
            camera=camera,
            width=width,
            height=height,
            scene=scene
        )

        return render_command

    def generate_ffmpeg_convert_command(self, start, frame_rate, output_dir, playblast_name, width, height, file_type):
        ffmpeg_command_convert = ""
        if self.create_mp4_checkbox.isChecked():
            ffmpeg_command_convert = " ".join([
                '"{ffmpeg_path}"',
                '-y',
                '-start_number {start}',
                '-r {frame_rate}',
                '-s {resolution}',
                '-i "{image_input_path}"',
                '-crf 20',
                '-pix_fmt yuv420p',
                '-vcodec libx264',
                '"{image_output_path}"'
            ]).format(
                ffmpeg_path=self.FFMPEG_PATH,
                start=start,
                frame_rate=self.FRAME_RATE_LIB[frame_rate],
                resolution="{}x{}".format(width, height),
                image_input_path=output_dir + "/" + playblast_name + ".%04d." + file_type,
                image_output_path=output_dir + "/" + playblast_name + ".mp4"
            )

        return ffmpeg_command_convert

    def generate_ffmpeg_burnin_command(self, start_frame, end_frame,
                                       output_dir, playblast_name,
                                       file_type, scene_name, height, width,
                                       time_stamp, camera, project_name, shot_name):
        ffmpeg_command_burnin = ""
        if self.burn_in_checkbox.isChecked():
            ffmpeg_command_burnin = " ".join(
                [
                    '"{ffmpeg_path}"',
                    '-y',
                    '-i "{image_input_path}"',
                    '-vf "drawbox=x=0:y={bottom_pos}:w={burnin_width}:h={burnin_height}:color=black@0.3:t=fill,',
                    'drawbox=x=0:y=0:w={burnin_width}:h={burnin_height}:color=black@0.3:t=fill,',
                    'drawtext=text={scene_name}:fontcolor=white:fontsize={scene_name_size}:font=ArialBlack:x={scene_name_xpos}:y={scene_name_ypos},',
                    'drawtext=text={project_info}:fontcolor=white:fontsize={scene_name_size}:font=ArialBlack:x={scene_name_xpos}:y=h-th-{scene_name_ypos},',
                    'drawtext=text={time_stamp}:fontcolor=white:fontsize={scene_name_size}:font=ArialBlack:x=w-tw-{scene_name_xpos}:y={scene_name_ypos},',
                    'drawtext=text=#{frame}:fontcolor=white:fontsize={scene_name_size}:font=ArialBlack:x=w-tw-{scene_name_xpos}:y=h-th-{scene_name_ypos},',
                    'drawtext=text={camera_data}:fontcolor=white:fontsize={scene_name_size}:font=ArialBlack:x=(main_w/2-text_w/2):y=h-th-{scene_name_ypos}"',
                    '"{image_output_path}"'
                ]
            )
            python_burnin_command = "\n".join([
                'project_info = "{project_info}"',
                'camera_data = "{camera_data}"',
                'start_frame = {start_frame}',
                'end_frame = {end_frame}',
                'FFMPEG_PATH = r"{ffmpeg_path}"',
                'output_dir = r"{output_dir}"',
                'playblast_name = "{playblast_name}"',
                'file_type = "{file_type}"',
                'height = {height}',
                'width = {width}',
                'time_stamp = "{time_stamp}"',
                'scene_name = "{scene_name}"',
                'ffmpeg_command_burnin = \'{ffmpeg_command_burnin}\'',
                'for i in range(start_frame, end_frame+1):',
                '    image_input_path = output_dir + "/" + playblast_name + "." + str(format(i, "04d")) + "." + file_type',
                '    image_output_path = output_dir + "/" + playblast_name + "_TEMP_" + "." + str(format(i, "04d")) + "." + file_type',
                '    command = ffmpeg_command_burnin.format(',
                '        ffmpeg_path=FFMPEG_PATH,',
                '        start_frame=start_frame,',
                '        image_input_path=image_input_path,',
                '        bottom_pos=int(height - height/20),',
                '        burnin_width=width,',
                '        burnin_height=int(height/20),',
                '        scene_name=scene_name,',
                '        scene_name_size=int(height/46),',
                '        scene_name_xpos=int(width/20),',
                '        scene_name_ypos=int((int(height/20)-int(height/43))/2),',
                '        time_stamp=time_stamp.replace(":", "_"),',
                '        image_output_path=image_output_path,',
                '        frame=i,',
                '        camera_data = camera_data,',
                '        project_info = project_info)',
                '    subprocess.check_call(command, shell=True)',
                '    os.remove(image_input_path)',
                '    os.rename(image_output_path, image_input_path)'
            ]).format(
                ffmpeg_command_burnin=ffmpeg_command_burnin,
                start_frame=start_frame,
                end_frame=end_frame,
                ffmpeg_path=self.FFMPEG_PATH,
                output_dir=output_dir,
                playblast_name=playblast_name,
                file_type=file_type,
                scene_name=scene_name,
                height=height,
                width=width,
                time_stamp=time_stamp,
                camera_data=str(camera) + " " + str(pc.PyNode(camera).getFocalLength()) + " mm",
                project_info="_".join([project_name, shot_name])
            )

            return python_burnin_command

    def generate_beta_script(
        self,
        file_type,
        shading_mode,
        camera,
        xray_mode,
        hwfog,
        dof,
        aa,
        ao,
        smooth_wireframe,
        background,
        render_command,
        beta_script_path,
        temp_scene_path,
        ffmpeg_command_convert,
        python_burnin_command,
        RV_play_command,
        mask
    ):
        beta_script = "\n".join([
            'import maya.standalone',
            'maya.standalone.initialize("Python")',
            'import maya.cmds as cmds',
            'import os',
            'import subprocess',
            'import nodes.load_plugins',
            'nodes.load_plugins.main()',
            'cmds.file("{scene}", o=1, f=1)',
            'cmds.setAttr("defaultRenderGlobals.imageFormat", {format})',
            'cmds.setAttr("defaultRenderGlobals.outFormatControl", 0)',
            'cmds.setAttr("defaultRenderGlobals.animation", 1)',
            'cmds.setAttr("defaultRenderGlobals.putFrameBeforeExt", 1)',
            'cmds.setAttr("defaultRenderGlobals.extensionPadding", 4)',
            'cmds.setAttr("hardwareRenderingGlobals.renderMode", {shading_mode})',
            'cmds.setAttr("hardwareRenderingGlobals.xrayMode", {xray_mode})',
            'cmds.setAttr("hardwareRenderingGlobals.hwFogEnable", {hwfog})',
            'cmds.setAttr("hardwareRenderingGlobals.renderDepthOfField", {dof})',
            'cmds.setAttr("hardwareRenderingGlobals.lineAAEnable", {aa})',
            'cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable", {smooth_wireframe})',
            'cmds.setAttr("hardwareRenderingGlobals.ssaoEnable", {ao})',
            'cmds.setAttr("{camera}"+".backgroundColor", {bg_0}, {bg_1}, {bg_2})',
            'cmds.setAttr("{camera}"+".mask", {mask})',
            'cmds.setAttr("{camera}"+".depth", 0)',
            'cmds.colorManagementPrefs(e=1, outputTransformEnabled=1)',
            # 'cmds.colorManagementPrefs(e=1, outputUseViewTransform=1)',
            # 'cmds.colorManagementPrefs(e=1, outputTransformName="sRGB gamma")',
            'cmds.file(save=1, force=1)',
            'subprocess.check_call(r\'{command}\')',
            '{python_burnin}',
            'subprocess.check_call(r\'{ffmpeg_convert}\', shell=True)',
            'subprocess.check_call(r\'{RV_play_command}\', shell=True)',
            'os.remove(r"{temp_file}")',
            'os.remove(r"{beta_script}")',
        ]).format(
            scene=temp_scene_path,
            format=self.IMAGE_FORMAT_LIB[file_type],
            shading_mode=shading_mode,
            camera=camera,
            xray_mode=xray_mode,
            hwfog=hwfog,
            dof=dof,
            aa=aa,
            ao=ao,
            smooth_wireframe=smooth_wireframe,
            bg_0=background[0],
            bg_1=background[1],
            bg_2=background[2],
            command=render_command,
            beta_script=beta_script_path,
            temp_file=temp_scene_path,
            ffmpeg_convert=ffmpeg_command_convert,
            python_burnin=python_burnin_command,
            RV_play_command=RV_play_command,
            mask=mask
        )

        return beta_script

    def generate_cmd_command(self, beta_script_path):
        cmd_command = " ".join([
            '"{mayapy_path}"',
            '"{beta_script_path}"'
        ]).format(
            mayapy_path=self.MAYAPY_PATH,
            beta_script_path=beta_script_path)

        return cmd_command

    def test_viewport(self):
        try:
            pc.windows.modelPanel(pc.getPanel(withFocus=1), q=1, cam=1)
            return True
        except Exception:
            pc.confirmDialog(
                ma="center",
                title="WARNING",
                message="Please select a viewport to playblast.",
                icon="warning",
                button="OK")
            return False

    def generate_RV_view_script(self, frame_rate, output_dir, playblast_name, file_type, start_frame):
        RV_play_command = " ".join([
            '"{RV_path}"',
            '-fps {frame_rate}',
            '"{image_path}"'
        ]).format(
            RV_path=self.RV_PATH,
            frame_rate=self.FRAME_RATE_LIB[frame_rate],
            image_path=output_dir
        )

        return RV_play_command

    def create_playblast(self):
        if self.test_viewport():
            ui_data_dict = self.collect_info_from_ui()

            end_frame = ui_data_dict["end_frame"]
            start_frame = ui_data_dict["start_frame"]
            output_dir = ui_data_dict["output_dir"]
            file_type = ui_data_dict["file_type"]
            height = ui_data_dict["height"]
            width = ui_data_dict["width"]
            background = ui_data_dict["background"]
            shading_mode = ui_data_dict["shading_mode"]
            xray_mode = ui_data_dict["xray_mode"]
            hwfog = ui_data_dict["hwfog"]
            dof = ui_data_dict["dof"]
            ao = ui_data_dict["ao"]
            aa = ui_data_dict["aa"]
            smooth_wireframe = ui_data_dict["smooth_wireframe"]
            project_name = ui_data_dict["project_name"]
            shot_name = ui_data_dict["shot_name"]
            comment = ui_data_dict["comment"]
            playblast_name = ui_data_dict["playblast_name"]
            mask = ui_data_dict["mask"]

            self.create_directory(output_dir)

            scene_data_dict = self.collect_info_from_scene()

            camera = scene_data_dict["camera"]
            frame_rate = scene_data_dict["frame_rate"]
            scene_name = scene_data_dict["scene_name"]
            time_stamp = scene_data_dict["time_stamp"]
            temp_scene_path = scene_data_dict["temp_scene_path"]
            beta_script_path = scene_data_dict["beta_script_path"]

            pc.exportAll(temp_scene_path, force=1)

            render_command = self.generate_render_command(
                output_dir,
                playblast_name,
                start_frame,
                end_frame,
                camera,
                width,
                height,
                temp_scene_path)

            ffmpeg_command_convert = self.generate_ffmpeg_convert_command(
                start_frame,
                frame_rate,
                output_dir,
                playblast_name,
                width,
                height,
                file_type)

            python_burnin_command = self.generate_ffmpeg_burnin_command(
                start_frame,
                end_frame,
                output_dir,
                playblast_name,
                file_type,
                scene_name,
                height,
                width,
                time_stamp,
                camera,
                project_name,
                shot_name)

            RV_play_command = self.generate_RV_view_script(
                frame_rate,
                output_dir,
                playblast_name,
                file_type,
                start_frame)

            beta_script = self.generate_beta_script(
                file_type,
                shading_mode,
                camera,
                xray_mode,
                hwfog,
                dof,
                aa,
                ao,
                smooth_wireframe,
                background,
                render_command,
                beta_script_path,
                temp_scene_path,
                ffmpeg_command_convert,
                python_burnin_command,
                RV_play_command,
                mask
            )

            with open(beta_script_path, "w+") as this_file:
                this_file.write(beta_script)

            cmd_command = self.generate_cmd_command(beta_script_path)

            t = threading.Thread(target=lambda: subprocess.check_call('{}'.format(cmd_command), shell=True))
            t.daemon = True
            t.start()

    def get_info_from_path(self):
        scene_path = pc.sceneName()
        if self.get_project() in scene_path:
            scene_name = os.path.split(scene_path)[-1].split(".")[0]
            dir_path = os.path.dirname(scene_path)

            user = scene_name.split("_")[-1]
            version = scene_name.split("_")[-2]
            step = scene_name.split("_")[-3]
            shot = "_".join(scene_name.split("_")[0:2])

            cg_dir = dir_path.split("work")[0][0:-1]
            step = dir_path.split("work")[-1].split("/")[1]

            root_dir = "/".join([cg_dir, "_export", "img-prv", "work", step, scene_name])

            return root_dir, shot
        else:
            return None, None

    def get_project(self):
        project_name = "test"
        # with open(self.JSON_PATH, "r") as file:
        #     data = json.load(file)

        # project_name = data["SG_PROJECTNAME"]

        return project_name

    def create_directory(self, path):
        if not os.path.isdir(path):
            os.makedirs(path)


def main():
    try:
        d.close()
    except:
        pass
    d = BackgroundPlayblast()
    d.show(dockable=True)
