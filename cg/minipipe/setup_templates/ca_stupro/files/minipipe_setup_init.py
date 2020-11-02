from maya.utils import executeDeferred
import pymel.core as pc
import cg.maya.minipipe.utils as mp_utils 

mp_utils.set_config_file_env(mp_utils.get_config_file())
executeDeferred(mp_utils.set_basepath_env)
executeDeferred(mp_utils.setup_maya)