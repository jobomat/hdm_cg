# coding: utf-8
import os
import getpass
import json
import inspect

import pymel.core as pc

from cg.maya.env.io import load_env_json, save_env_json
import cg.general.files as files
from cg.maya.files.paths import normpath


def get_config_file():
    psp = pc.mel.eval('getenv "PROJECT_SETUP_PATH"')
    if not psp:
        return ""
    return "{}/minipipe_config.json".format(psp)


def set_config_file_env(config_file_path):
    pc.mel.eval(
        'putenv "MINIPIPE_CONFIG_FILE" "{}"'.format(config_file_path)
    )


def load_config():
    try:
        # print "1"
        with open(os.path.normpath(pc.mel.eval('getenv "MINIPIPE_CONFIG_FILE"'))) as cf:
            config = json.load(cf)
        return config
    except:
        # print "1.2"
        try:
            # print "2"
            # try to load blueprint config
            blueprint_config_file = "{}/{}".format(
                pc.mel.eval('getenv "GLOBAL_SETUP_PATH"'),
                "cg/minipipe/minipipe_blueprint_config.json"
            )
            with open(os.path.normpath(blueprint_config_file)) as cf:
                config = json.load(cf)
            return config
        except:
            return {}


def set_basepath_env(base_path=None, config=None):
    if not base_path:
        config_file = get_config_file()
        if not config:
            # config_file = get_config_file()
            config = load_config()
        end = len(config["minipipe_dir"]) + len("/minipipe_config.json") + 1
        base_path = config_file[:-end]
    pc.mel.eval(
        'putenv "MINIPIPE_BASE_PATH" "{}"'.format(base_path)
    )
    return base_path


def get_base_path(config=None):
    mp_basepath = pc.mel.eval('getenv "MINIPIPE_BASE_PATH"')
    if not mp_basepath:
        mp_basepath = set_basepath_env(config=config)
    return mp_basepath


def set_maya_project_env(config):
    pc.mel.eval('putenv "env_var_name" "{}"'.format(config["env_var_name"]))
    pc.mel.eval(
        'putenv "{}" "{}"'.format(
            config["env_var_name"],
            "/".join([
                get_base_path(config),
                config["maya_project_dir"]
            ])
        )
    )


def change_config_file(config_file):
    set_config_file_env(config_file)
    config = load_config()
    end = len(config["minipipe_dir"]) + len("/minipipe_config.json") + 1
    mp_basepath = config_file[:-end]
    set_basepath_env(mp_basepath)
    psp = "{}/{}".format(
        mp_basepath, config["minipipe_dir"]
    )
    # set project path in global conf an env var
    global_config = load_env_json("GLOBAL_CONFIG_FILE")
    global_config["PROJECT_SETUP_PATH"] = psp
    save_env_json(global_config, "GLOBAL_CONFIG_FILE")
    pc.mel.eval(
        'putenv "PROJECT_SETUP_PATH" "{}"'.format(psp)
    )
    set_config_file_env(config_file)
    setup_maya()


def update_actions(mp_config):
    project_base_path = mp_config.get("project_base_path", False)
    if not project_base_path:
        env_var_path = pc.mel.eval('getenv "{}"'.format(mp_config["env_var_name"]))
        project_base_path = "/".join(env_var_path.split("/")[:-1])
    mp_config["project_base_path"] = project_base_path

    mp_template_dir = mp_config.get("mp_template_dir", "")
    if not mp_template_dir or not os.path.isfile(os.path.normpath(mp_template_dir)):
        this_file_path = normpath(inspect.getfile(lambda: None))
        mp_template_dir = "{}/minipipe/setup_templates/ca_stupro".format(
            "/".join(this_file_path.split("/")[:-3]
        ))
    mp_config["mp_template_dir"] = mp_template_dir

    with open(os.path.normpath("{}/files/minipipe_config.json".format(mp_template_dir))) as f:
        new_config = json.load(f)
    
    mp_config["actions"] = new_config["actions"]
    
    with open("{}/pipeline/minipipe/minipipe_config.json".format(get_base_path()), "w") as f:
        json.dump(mp_config, f, indent=4)


def set_maya_project(mp_config):
    pc.mel.setProject(pc.mel.eval('getenv "{}"'.format(mp_config["env_var_name"])))
    # print("Setting project to '{}'".format(pc.workspace.path))


def setup_maya():
    # maya project
    mp_config = load_config()

    print("Load Minipipe-Project '{}':".format(mp_config["env_var_name"]))

    set_maya_project_env(mp_config)
    set_maya_project(mp_config)
    print("Setting project to '{}'".format(pc.workspace.path))

    # framerate
    fps_name = [
        k for k in mp_config["fps_map"]
        if mp_config["fps_map"][k] == mp_config["framerate"]
    ][0]
    pc.currentUnit(time=fps_name)
    print("Setting framerate to {} ({})".format(mp_config["framerate"], fps_name))

    # resolution
    pc.PyNode("defaultResolution").setAttr("width", mp_config["image_resolution"][0])
    pc.PyNode("defaultResolution").setAttr("height", mp_config["image_resolution"][1])
    print(
        "Setting render resolution to {} x {} pixel".format(
            mp_config["image_resolution"][0], mp_config["image_resolution"][1]
        )
    )


def save_config(config_dict):
    with open(get_config_file(), "w+") as cf:
        json.dump(config_dict, cf, indent=4)
    return True


def to_save_string(string, allowed="", replace={}):
    valid_chars = "abcdefghijklmnopqrstuvwxyz1234567890"

    for k, v in replace.items():
        string = string.replace(k, v)
        valid_chars += v

    valid_chars = "{}{}{}".format(
        valid_chars, valid_chars.upper(), allowed
    )
    return "".join(char for char in string if char in valid_chars)


def get_system_user():
    return to_valid_file_name(str(getpass.getuser()))


def to_valid_file_name(name):
    return to_save_string(
        name.strip(), replace={
            u"ü": "ue", u"ö": "oe", u"ä": "ae", u"ß": "ss", "_": "-", " ": "-"
        }
    )


def get_nested_dict(dictionary, *keys_and_default):
    for key in keys_and_default[:-1]:
        dictionary = dictionary.get(key, None)
        #print dictionary, key
        if not dictionary:
            return keys_and_default[-1]
    return dictionary


def create_minipipe_project(destination, mp_template_dir, env_var_name, simulate=False):
    struct_file = os.path.join(mp_template_dir, "folder_structure.txt")
    files_dir = os.path.join(mp_template_dir, "files")

    set_basepath_env(destination)

    # Create folder structure
    try:
        with open(struct_file) as f:
            struct_string = f.read()
        files.folders_from_string(struct_string, destination, files_dir, simulate=simulate)
        if simulate:
            return (
                "info", "Check Script Editor to see simulated creation."
            )
    except IOError:
        return (
            "error",
            "Minipipe Template Dir, folder_structure.txt or minipipe_config.json seems not valid."
        )
    print("Filestructure created.")

    # Look if minipipe_config.json is there an readable
    try:
        minipipe_config_json = os.path.join(mp_template_dir, "files", "minipipe_config.json")
        with open(minipipe_config_json) as cf:
            minipipe_config = json.load(cf)

    except IOError:
        return (
            "error",
            "File 'minipipe_config.json' not found in '{}/files'.".format(mp_template_dir)
        )
    except ValueError:
        return ("error", "File '{}/files/minipipe_config.json' contains errors.".format(mp_template_dir))

    # Try to update minipipe_config.json
    try:
        minipipe_config["env_var_name"] = env_var_name
        minipipe_config["project_base_path"] = destination
        minipipe_config["mp_template_dir"] = mp_template_dir
        mp_project_json = os.path.join(
            destination,
            minipipe_config["minipipe_dir"],
            "minipipe_config.json"
        )
        with open(os.path.normpath(mp_project_json), "w+") as cf:
            json.dump(minipipe_config, cf, indent=4)
        set_config_file_env(normpath(mp_project_json))
    except:
        return (
            "error",
            "Error writing 'minipipe_config.json' to '{}/files'.".format(mp_project_json)
        )

    # Try to udate global config
    try:
        config = load_env_json("GLOBAL_CONFIG_FILE")
        config["PROJECT_SETUP_PATH"] = normpath(
            os.path.join(
                destination,
                minipipe_config["minipipe_dir"]
            )
        )
        save_env_json(config, "GLOBAL_CONFIG_FILE")
        pc.mel.eval(
            'putenv "PROJECT_SETUP_PATH" "{}"'.format(
                config["PROJECT_SETUP_PATH"]
            )
        )
    except NameError:
        return (
            "error",
            "Global variable 'GLOBAL_CONFIG_FILE' does not exist."
        )

    return (
        "success", "Minipipe project '{}' successfully created.".format(env_var_name)
    )
