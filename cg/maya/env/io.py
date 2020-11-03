import os
import json
import pymel.core as pc


def load_env_json(env_var_name, additional_path=""):
    """
    load json from file specified in environment variable
    env_var_name: The name of the environment variable that
                  contains path+filename of json-file 
    """
    try:
        cjf = pc.mel.eval('getenv "{}"'.format(env_var_name))
        if additional_path:
            cjf = os.path.normpath(os.path.join(
                cjf, additional_path
            ))
        with open(cjf) as cf:
            return json.load(cf)
    except NameError:
        print("Env-Var '{}' is not set.".format(env_var_name))
        return {}
    except IOError:
        print("File '{}' not found.".format(cjf))
        return {}
    except ValueError:
        print("File '{}' is not a valid JSON file.".format(cjf))
        return {}


def save_env_json(json_dict, env_var_name, additional_path=""):
    """
    save json to file specified in environment variable
    json_dict:    The dict to save
    env_var_name: The name of the environment variable that
                  contains path+filename of json-file 
    """
    try:
        cjf = pc.mel.eval('getenv "{}"'.format(env_var_name))
        if additional_path:
            cjf = os.path.normpath(os.path.join(
                cjf, additional_path
            ))
        if not cjf:
            pc.warning("Env-Var '{}' is not set. Nothing written.".format(env_var_name))
            return
        with open(cjf, 'w+') as outfile:
            json.dump(json_dict, outfile, indent=4)
    except:
        print("Error saving json.")