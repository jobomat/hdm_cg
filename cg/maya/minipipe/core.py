import os
from shutil import copyfile
from time import time
from datetime import datetime
import sys
import importlib
import json
# from collections import defaultdict

import pymel.core as pc

from cg.maya.files.paths import normpath
from cg.maya.minipipe.utils import load_config, get_nested_dict


def get_meta_node(namespace=""):
    name = "{}:minipipe_meta".format(namespace)
    try:
        meta = pc.PyNode(name)
    except pc.MayaObjectError:
        meta = pc.group(empty=True, name=name)
        meta.setAttr("hiddenInOutliner", True)
        pc.mel.eval("AEdagNodeCommonRefreshOutliners();")
        meta.addAttr("data", type="string")
        meta.setAttr("data", "{}")

    return meta

def read_meta(namespace=""):
    meta_node = get_meta_node(namespace)
    return json.loads(meta_node.getAttr("data"))

def write_meta(data, namespace=""):
    meta_node = get_meta_node(namespace)
    meta_node.setAttr("data", json.dumps(data))


def parse_file_name(path_and_file):
    name = dept = user = ts = version = ""
    if not path_and_file:
        return name, dept, user, ts, version  # untitled / neue szene

    scene_name = path_and_file.split("/")[-1].split(".")[0]
    scene_parts = scene_name.split("_")

    if len(scene_parts) <= 1:
        return name, dept, user, ts, version  # not conforming to naming convention

    name = scene_parts[0]
    dept = scene_parts[1]

    try:
        user = scene_parts[2]
        ts = scene_parts[3]
        version = scene_parts[4]
    except:
        user = ts = version = ""

    return name, dept, user, ts, version


def get_scene_types():
    config = load_config()
    
    icon_path = "{}/setup_maya/".format(pc.mel.eval('getenv "PROJECT_SETUP_PATH"'))

    scenes_folder = pc.workspace.fileRules['mayaAscii']
    scenes_path = os.path.normpath(os.path.join(
        pc.workspace.path, scenes_folder
    ))
    # print scenes_path
    r, dirs, f = next(os.walk(scenes_path))
    scene_types = []
    for d in dirs:
        icon = config.get("scene_types", {}).get(d, {}).get("icon", "")
        icon = "{}{}".format(icon_path, icon) if icon else ""
        
        scene_types.append({
            "name": d,
            "path": normpath(os.path.join(scenes_path, d)),
            "nice_name": get_nested_dict(config, "scene_types", d, "nice_name", d),
            "icon": icon,
            "start_dept": get_nested_dict(config, "scene_types", d, "start_dept", "mod")
        })

    return scene_types


class Scene():
    types = get_scene_types()
    
    def __init__(self, name, scene_type_name="", scene_type=None):
        self.name = name
        self.type = scene_type
        if scene_type_name:
            self.type = filter(lambda x: x == scene_type_name, Scene.types)[0]
        self.absolute_path = "{}/{}".format(self.type["path"], name)
        self.relative_path = "{}/{}".format(self.type["name"], name)
        icon = "{}/thumb.jpg".format(self.absolute_path)
        self.icon = icon if os.path.isfile(icon) else self.type["icon"]
        self.releases = []
        self.versions = {}
        # self.depts = []

    @classmethod
    def reload_scene_types(self):
        Scene.types = get_scene_types()

    def create_asset_dirs(self, user):
        try:
            os.mkdir(os.path.normpath(os.path.join(
                self.type["path"], self.name
            )))
            os.mkdir(os.path.normpath(os.path.join(
                self.type["path"], self.name, "versions"
            )))
            os.mkdir(os.path.normpath(os.path.join(
                self.type["path"], self.name, "release_history"
            )))
            
            self.create_dept_folders(self.type["start_dept"])

            initial_file = os.path.normpath(os.path.join(
                pc.workspace.path,
                pc.workspace.fileRules["mayaAscii"],
                "initial.ma"
            ))
            initial_version = os.path.normpath(os.path.join(
                self.type["path"], self.name, "versions", self.type["start_dept"],
                self.create_version_file_name(self.type["start_dept"], user)
            ))
        
            copyfile(initial_file, initial_version)

            return True
        except:
            # print(sys.exc_info()[0])
            raise
            return False

    def create_dept_folders(self, dept):
        dept_v = os.path.normpath(os.path.join(
            self.type["path"], self.name, "versions", dept
        ))
        dept_rh = os.path.normpath(os.path.join(
            self.type["path"], self.name, "release_history", dept
        ))

        if not os.path.isdir(dept_v):
            os.mkdir(dept_v)
        if not os.path.isdir(dept_rh):
            os.mkdir(dept_rh)

        return dept_v, dept_rh

    def create_version_file_name(self, dept, user, version=1, ts=None):
        if not ts:
            ts = int(time())
        return "{}_{}_{}_{}_{}.ma".format(
            self.name, dept, user, ts, str(version).zfill(4)
        )

    def get_status(self):
        try:
            _, d, files = next(os.walk(self.absolute_path))
            
            self.releases = [
                (f.split("_")[-1][:-3], "{}/{}".format(self.absolute_path,f)) 
                for f in files if f.endswith(".ma") or f.endswith(".mb")
            ]

            _, dirs, f = next(os.walk(os.path.join(self.absolute_path, "versions")))
            
            self.versions = {}
            for d in dirs:
                self.versions[d] = []
                r, _, files = next(os.walk(
                    os.path.join(self.absolute_path, "versions", d)
                ))
                for f in reversed(files):
                    if f.endswith(".ma") or f.endswith(".mb"):
                        name, dept, user, ts, version = parse_file_name(
                            os.path.join(self.absolute_path, "versions", d, f)
                        )
                        self.versions[dept].append(
                            {   
                                "file": f, "user": user, "ts": ts, "version": version,
                                "absolute_path": "{}/versions/{}/{}".format(self.absolute_path, dept, f),
                                "nice_time": self.get_nice_time(int(ts))
                            }
                        )

            _, dirs, f = next(os.walk(os.path.join(self.absolute_path, "release_history")))
            
            self.release_history = {}
            for d in dirs:
                self.release_history[d] = []
                r, _, files = next(os.walk(
                    os.path.join(self.absolute_path, "release_history", d)
                ))
                for f in files:
                    if f.endswith(".ma") or f.endswith(".mb"):
                        self.release_history[d].append(f)

        except StopIteration:
            self.releases = []
            self.versions = {}
            self.release_history = {}

    def get_nice_time(self, ts=None):
        if not ts:
            ts = int(time())
        timeformat = '%d.%m.%Y %H:%M'
        return datetime.fromtimestamp(int(ts)).strftime(timeformat)

    def bump_version(self, dept, user):
        latest = self.get_latest_version(dept)
        new_version = int(latest["version"]) + 1
        file_name = self.create_version_file_name(
            dept, user, version=new_version
        )
        file_path = normpath(os.path.join(
            self.type["path"], self.name, "versions", dept, file_name
        ))
        
        res = pc.saveAs(file_path)
        if res:
            return ("success", "Saved as version {} ({})".format(new_version, res))
        else:
            return ("error", "Error saving new version.")
        
    def release(self, dept, user):
        file_path = normpath(os.path.join(
            self.type["path"], self.name, "{}_{}.ma".format(self.name, dept)
        ))
        try:
            if os.path.isfile(file_path):
                # wegkopieren alter releases
                release_history_dir = normpath(os.path.join(
                    self.type["path"], self.name, "release_history", dept
                ))
                if not os.path.isdir(release_history_dir):
                    os.mkdir(os.path.normpath(release_history_dir))

                copyfile(
                    file_path, 
                    normpath(os.path.join(
                        release_history_dir, "{}_{}_{}.ma".format(
                            str(len(self.release_history[dept]) + 1).zfill(4), self.name, dept 
                        )
                    ))
                )

            metadata = read_meta()
            if metadata.get("release_history", None) is None:
                metadata["release_history"] = []
            metadata["release_history"].append(pc.sceneName())
            write_meta(metadata)

            res = pc.saveFile()
            copyfile(res, file_path)
            return "success", "Released {} {}".format(self.name, dept)
        except:
            return "error", "Error releasing {} {}".format(self.name, dept)

    def reference(self, dept, namespace=""):
        ref_file = normpath(os.path.join(
            "${}".format(pc.mel.eval('getenv "env_var_name"')),
            pc.workspace.fileRules["mayaAscii"],
            self.relative_path,
            "{}_{}.ma".format(self.name, dept)
        ))
        pc.createReference(ref_file, namespace=namespace if namespace else dept)

    def get_depts(self):
        return self.versions.keys()

    def has_release(self, dept):
        return len([1 for d in self.releases if d[0]==dept]) > 0

    def get_latest_version(self, dept):
        return self.versions[dept][0]


def create_dynamic_actions_ui(parent_ui, actions, scene, dept, *args, **kwargs):
    for action in actions:
        mod = importlib.import_module(action)
        reload(mod)
        getattr(mod, "ui")(parent_ui, scene, dept, *args, **kwargs)
        

def get_scene_list():
    scene_list = []

    for scene_type in Scene.types:
        r, dirs, f = next(os.walk(scene_type["path"]))
        if not dirs:
            continue

        for d in dirs:  
            scene_list.append(Scene(d, scene_type))

    return scene_list


def scene_from_open_file():
    open_file = pc.sceneName()
    name, dept, user, ts, version = parse_file_name(open_file)

    possible_paths = [
        ("{}/{}".format(scene_type["path"], name), scene_type)
        for scene_type in Scene.types
    ]

    possible_path = ""
    for path, scene_type in possible_paths:
        if open_file.startswith(path):
            possible_path = path
            st = scene_type
            return Scene(name, scene_type=st), dept, user, ts, version

    return None, None, None, None, None  # not in Minipipe path
    