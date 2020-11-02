from maya.utils import executeDeferred
from maya_settings import MAYA_SETTINGS
import maya_setup_utils

maya_setup_utils.set_env_vars(
	MAYA_SETTINGS['maya_env_vars'],
	MAYA_SETTINGS['path_prefixes']
)

executeDeferred(maya_setup_utils.build_shelfes)
executeDeferred(maya_setup_utils.add_hdm_button)
