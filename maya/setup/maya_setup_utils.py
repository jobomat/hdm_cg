import os
import platform
import pymel.core as pc
from maya_settings import MAYA_SETTINGS


def set_env_vars(env_vars, path_prefixes):
    if not path_prefixes["base"]:
        path_prefixes["base"] = os.path.dirname(
            os.path.dirname(
                os.path.dirname(__file__)
            )
        )

    for env_var in env_vars:
        recursive = env_var.get("recursive", False)
        include_self = env_var.get("include_self", False)
        replace = env_var.get("replace", False)
        values = [p.format(**path_prefixes) for p in env_var["values"]]
        orig_values = values[:]

        if recursive:
            values = []
            for val in orig_values:
                for root, dirs, files in os.walk(val):
                    if not include_self and root in orig_values:
                        continue
                    values.append(root.replace("\\", "/"))

        new_value = ";".join(
            values
        ).replace(
            "pc.versions.shortName()", str(pc.versions.shortName())
        ).replace(
            "platform.system()", str(platform.system())
        )
        # platform.system()
        # Linux: Linux
        # Mac: Darwin
        # Windows: Windows
        old_value = "" if replace else pc.language.Mel.eval('getenv "{}"'.format(env_var["name"]))
        all_values = "{}{}{}".format(
            old_value,
            ";" if old_value else "",
            new_value
        )

        print("{} '{}' with:".format("Replacing" if replace else "Updating", env_var["name"]))
        print(new_value)

        pc.language.Mel.eval(
            'putenv "{env_var}" "{val}"'.format(
                env_var=env_var["name"], val=all_values
            )
        )


def build_shelfes():
    from cg.maya.ui import shelfes
    global MAYA_SETTINGS

    json_shelf_dir = MAYA_SETTINGS["json_shelf_dir"].format(
        base=MAYA_SETTINGS['path_prefixes']['base']
    )
    r, d, files = next(os.walk(json_shelf_dir))

    tls = shelfes.TopLevelShelf()
    for f in files:
        if f.endswith(".json"): 
            tls.load_from_json(os.path.join(json_shelf_dir, f))


def open_minipipe(rebuild_win=False):
    import cg.maya.minipipe.ui as mp_ui
    reload(mp_ui)
    mp_ui.MainWindow(rebuild_win=rebuild_win)


def add_hdm_button():
    gToolBox = pc.language.getMelGlobal('string', 'gToolBox')
    # tool_box_button_names = pc.flowLayout(gToolBox, q=True, childArray=True)
    hdm_button = pc.iconTextButton(parent=gToolBox, image="hdm.png")
    hdm_button.setCommand(pc.Callback(open_minipipe, True))
