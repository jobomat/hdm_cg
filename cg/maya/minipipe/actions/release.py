import pymel.core as pc


def release(scene, dept, *args, **kwargs):
    user = kwargs.get("user", "unknown")
    variant = kwargs.get("variant", "")
    out_layout = kwargs.get("out_layout", None)
    update_status_message = kwargs.get("update_status_message", None)

    msg = scene.release(dept, user, variant)

    if dept == "ren" and msg[0] == "success":
        searchstring = pc.mel.eval('getenv "{}"'.format(pc.mel.eval('getenv "env_var_name"')))
        replacestring = "{}/{}".format(
            kwargs["config"]["render_base_path"],
            kwargs["config"]["maya_project_dir"]
        )
        if searchstring != replacestring:
            with open(msg[1]) as f:
                ma = f.read()
            ma = ma.replace(searchstring, replacestring)
            with open(msg[1], "w") as f:
                f.write(ma)

    if out_layout:
        out_layout()
    if update_status_message:
        update_status_message(msg)


def ui(parent_cl, scene, dept, *args, **kwargs):
    variant = kwargs.get("variant", "")
    help_text = "New clean version?"
    if dept == "mod":
        help_text = "Topo good? New UVs?"
    elif dept == "rig":
        help_text = "New rig feature?"
    elif dept == "shd":
        help_text = "New shader settings or maps?"
    pc.text(p=parent_cl, label=help_text)
    pc.button(
        p=parent_cl, label="Release this version as '{}{}_{}'".format(
            scene.name,
            "" if not variant else "_{}".format(variant),
            dept
        ),
        c=pc.Callback(release, scene, dept, *args, **kwargs)
    )
