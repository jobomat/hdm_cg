#import inspect
import os
from shutil import copyfile
import json

import pymel.core as pc


def install(base_path):
	#this_file_path = inspect.getfile(lambda: None)
	#base_path = os.path.dirname(this_file_path)
	base_path = base_path[:-1] if base_path.endswith("/") else base_path
	app_dir = pc.mel.eval("getenv MAYA_APP_DIR;")
	script_dir = "{}/scripts".format(app_dir)
	config_filename = "config.json"
	setup_key = "GLOBAL_SETUP_PATH"
	config_dict = {setup_key: base_path}

	if not os.path.isdir(script_dir):
		pc.warning("Maya Configuration Warning: '{}' doesn't exist. Install aborted.".format(script_dir))
		return

	config_filepath = "{}/{}".format(script_dir, config_filename)
	
	if os.path.isfile(config_filepath):
		with open(config_filepath) as cf:
			old_conf = json.load(cf)
		result = pc.confirmDialog(
			title='Warning', message='Config.json already exists.\n{} key with install location?'.format(
				"Replace" if old_conf.get(setup_key, False) else "Add"
			),
			button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No'
		)
		if result == "Yes":
			old_conf[setup_key] = base_path
			config_dict = old_conf
		else:
			pc.warning("Config-Update/Install aborted by user.")
	with open(config_filepath, "w") as cf:
		json.dump(config_dict, cf, indent=4)

	user_setup_template = "{}/setup/{}".format(base_path, "userSetup.py")
	user_setup = "{}/{}".format(script_dir, "userSetup.py")
	if os.path.isfile(user_setup):
		result = pc.confirmDialog(
			title='Warning', message='userSetup.py already exists.\nReplace?',
			button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No'
		)
		if result == "No":
			pc.warning("Copying of userSetup.py aborted by user.")
			return
	copyfile(user_setup_template, user_setup)
	from userSetup import *
