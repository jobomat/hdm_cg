import pymel.core as pc


def release(scene, dept, *args, **kwargs):
    user = kwargs.get("user", "unknown")
    variant = kwargs.get("variant", "")
    out_layout = kwargs.get("out_layout", None)
    update_status_message = kwargs.get("update_status_message", None)

    if dept == "mod":
        dept_v, dept_rh = scene.create_dept_folders("shd")
        pc.saveAs("/".join([dept_v, scene.create_version_file_name("shd", user)]))

    msg = scene.release("shd", user, variant)

    if out_layout:
        out_layout()
    if update_status_message:
        update_status_message(msg)


def ui(parent_cl, scene, dept, *args, **kwargs):
    variant = kwargs.get("variant", "")
    help_text = "New shader settings or maps?"
    pc.text(p=parent_cl, label=help_text)
    pc.button(
        p=parent_cl, label="Release this version as '{}{}_shd'".format(
            scene.name,
            "" if not variant else "_{}".format(variant)
        ),
        c=pc.Callback(release, scene, dept, *args, **kwargs)
    )
