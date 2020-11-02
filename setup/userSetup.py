import sys
import inspect
import json
import pymel.core as pc

this_file_path = inspect.getfile(lambda: None)
global_config_file = "{}/config.json".format(
    this_file_path[:this_file_path.index("userSetup.py") - 1]
)
pc.mel.eval(
    'putenv "GLOBAL_CONFIG_FILE" "{}"'.format(
        global_config_file
    )
)

try:
    with open(global_config_file) as cf:
        global_config = json.load(cf)
except IOError:
    print("File 'config.json' not found in 'maya/scripts'.")
except ValueError:
    print("File 'config.json' is not a valid JSON file.")

try:
    global_setup_path = global_config["GLOBAL_SETUP_PATH"]
    sys.path.append(global_setup_path)
    pc.mel.eval(
    'putenv "GLOBAL_SETUP_PATH" "{}"'.format(
        global_setup_path
    )
)
    from setup import *
except ImportError:
    print("'GLOBAL_SETUP_PATH' is not pointing to the setup module.")
    print("--> 'GLOBAL_SETUP_PATH': '{}'".format(global_setup_path))
    print("--> No global setup performed. Features may be missing.")
except NameError:
    print("Variable 'GLOBAL_SETUP_PATH' not set in 'userSetup.py'.")
    print("--> No global setup performed. Features may be missing.")
except KeyError:
    print("Missing key 'GLOBAL_SETUP_PATH in 'config.json'.")
    print("--> No global setup performed. Features may be missing.")

try:
    project_setup_path = global_config["PROJECT_SETUP_PATH"]
    pc.mel.eval(
        'putenv "PROJECT_SETUP_PATH" "{}"'.format(
            project_setup_path
        )
    )
    sys.path.append(project_setup_path)
    from project_setup import *
except ImportError:
        print("The project setup module was not found.")
        print("--> 'PROJECT_SETUP_PATH': '{}'".format(project_setup_path))
        print("--> No project setup performed.")
except NameError:
    print("Variable 'PROJECT_SETUP_PATH' not found in 'userSetup.py'.")
    print("--> No project setup performed.")
except KeyError:
    print("Missing key 'PROJECT_SETUP_PATH in 'config.json'.")
    print("--> No project setup performed.")
