from os.path import split
import pymel.core as pc
from cg.general.names import get_legal_character, hash_iterator


def get_namespace(filepath, namespace_map={}):
    filename = split(filepath)[-1].split(".")[0]
    return namespace_map.get(filename, None) or filename


class HashRenamer():
    def __init__(self):
        self.name_history = []

        self.template = pc.uiTemplate('HashRenamerTemplate', force=True)
        self.template.define(
            pc.window, widthHeight=[300, 24], toolbox=True,
            title="Hash Renamer", resizeToFitChildren=True
        )

        self.ui()

    def ui(self):
        win_name = "hash_renamer_win"
        if pc.window(win_name, exists=True):
            pc.deleteUI(win_name)

        with self.template:
            with pc.window():
                with pc.columnLayout(adjustableColumn=True):
                    self.name_textFieldGrp = pc.textField(
                        textChangedCommand=self.check_text_field_input,
                        enterCommand=self.hash_rename_sel,
                        alwaysInvokeEnterCommandOnReturn=True,
                        annotation="'spine_##_jnt' will be renamed to\n'spine_01_jnt', 'spine_02_jnt'...",
                        placeholderText="Type and press Enter to rename."
                    )
                    self.name_history_menu = pc.popupMenu()
                    for name in self.name_history:
                        pc.menuItem(label=name, c=pc.Callback(self.name_textFieldGrp.setText, name))

    def check_text_field_input(self, *args):
        if not len(args[0]):
            return ""
        self.name_textFieldGrp.setText(
            "{}{}".format(
                args[0][:-1],
                get_legal_character(args[0][-1].encode("utf-8"), allow="#")
            )
        )

    def hash_rename_sel(self, *args):
        sel = pc.selected()
        if not sel:
            pc.warning("Please select some objects to rename.")
            return

        name = hash_iterator(args[0])
        for obj in sel:
            obj.rename(next(name))

        self.name_textFieldGrp.setText("")

        self.name_history.append(args[0])
        pc.menuItem(
            label=args[0], parent=self.name_history_menu,
            c=pc.Callback(self.name_textFieldGrp.setText, args[0])
        )
