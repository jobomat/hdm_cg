import pymel.core as pc


def release(scene, dept, *args, **kwargs):
    user = kwargs.get("user", "unknown")
    out_layout = kwargs.get("out_layout", None)
    update_status_message = kwargs.get("update_status_message", None)

    msg = scene.release(dept, user)

    if out_layout:
        out_layout()
    if update_status_message:
        update_status_message(msg)


def ui(parent_cl, scene, dept, *args, **kwargs):
    help_text = "New clean version?"
    if dept == "mod":
        help_text = "Topo good? New UVs?"
    elif dept == "rig":
        help_text = "New rig feature?"
    elif dept == "shd":
        help_text = "New shader settings or maps?" 
    pc.text(p=parent_cl, label=help_text)
    pc.button(
        p=parent_cl, label="Release this version as new '{}'".format(dept),
        c=pc.Callback(release, scene, dept, *args, **kwargs)
    )
