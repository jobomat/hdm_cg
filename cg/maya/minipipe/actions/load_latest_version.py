import pymel.core as pc


def load(scene_file):
    try:
        pc.openFile(scene_file)
    except RuntimeError:
        answer = pc.confirmDialog(
            title='Unsaved Changes', 
            message='Current scene has unsaved changes.\nContinue and lose changes?',
            button=['Continue', 'No! Stop!'], defaultButton='Continue',
            cancelButton='No! Stop!', dismissString='No! Stop!'
        )
        if answer == 'No! Stop!':
            return None
        pc.openFile(scene_file, force=True)


def ui(parentColumnLayout, scene, dept, *args):
    lv = scene.get_latest_version(dept)

    with pc.rowLayout(p=parentColumnLayout, nc=2, adj=1):
        pc.text(
            label="Latest Version: {} - V {} - {} - by {}".format(
                dept, lv["version"], lv["nice_time"], lv["user"]
            ), font="boldLabelFont"
        )
        pc.button(
            h=30, w=50,
            c=pc.Callback(load, lv["absolute_path"]), bgc=(0.45, 0.79, 0.74),
            label="Open"
        )
        