import os.path
from collections import OrderedDict
import pymel.core as pc
import windows
import factories
reload(windows)
reload(factories)


class QuickGUI():
    def __init__(self):
        self.layouts = OrderedDict([
            ("Layout", None),
            ("Horizontal", "hLayout"),
            ("Vertical", "vLayout"),
            ("Column", "columnLayout"),
            ("Free", "freeLayout"),
        ])
        self.controls = OrderedDict([
            ("Control", None),
            ("Button", "button"),
            ("Text", "text"),
            ("Textfield", "textFieldGrp"),
            ("Floatfield", "floatFieldGrp"),
            ("Intfield", "intFieldGrp"),
            ("Checkbox", "checkBoxGrp"),
            ("Radio Button", "radioButtonGrp"),
            ("Image", "image"),
        ])
        self.editwin_tlc = [200, 600]
        self.editwin_wh = [640, 480]

        with pc.window(title="Quick GUI", wh=self.editwin_wh, tlc=self.editwin_tlc):
            with pc.verticalLayout() as v:
                with pc.horizontalLayout(bgc=[.3, .3, .3]) as self.toolbar:
                    with pc.rowLayout(nc=6):
                        pc.button(label="Code", w=50, c=self.create_code)
                        pc.button(label="Recreate", w=50, c=self.recreate_instances)
                        self.pc_prefix_textfield = pc.textFieldGrp(text="pc.", label="prefix")
                with pc.paneLayout(configuration='vertical2', paneSize=[1, 32, 100]) as self.h2:
                    self.tree_view = pc.treeView(dragAndDropCommand=self.reorder_items, numberOfButtons=1)
                    with pc.columnLayout(adjustableColumn=True, rs=6) as self.edit_layout:
                        pass

        v.attachPosition(self.toolbar, "bottom", 30, 0)
        v.attachPosition(self.h2, "top", 30, 0)

        self.ui_tree = windows.QGWindow(
            name="Window", editor_instance=self,
            instance_kwargs={
                'tlc': [self.editwin_tlc[0], self.editwin_tlc[1] + self.editwin_wh[0]],
                'widthHeight': [500, 200]
            }
        )
        self.ui_tree.instance.show()

        self.build_tree_view()
        pc.treeView(self.tree_view, edit=True, selectItem=[self.ui_tree.treeview_name, True])
        self.ui_tree.build_edit_layout()

    def build_tree_view(self, ui_item=None, parent=""):
        ui_item = ui_item or self.ui_tree
        if ui_item == self.ui_tree:
            pc.treeView(self.tree_view, e=1, removeAll=True)
        pc.treeView(
            self.tree_view, e=1, addItem=(ui_item.treeview_name, parent),
            selectCommand=self.load_edit_panel
        )

        pc.treeView(
            self.tree_view, e=1, labelBackgroundColor=ui_item.get_treeview_color(),
            image=[
                ui_item.treeview_name, 1,
                os.path.join(os.path.dirname(__file__), "icons", ui_item.icon_name + ".png")
            ]
        )

        for child in ui_item.children:
            self.build_tree_view(child, ui_item.treeview_name)

    def load_edit_panel(self, *args):
        ui_item = self.ui_tree.get_by_name(args[0])
        for child in self.edit_layout.getChildren():
            pc.deleteUI(child)
        ui_item.build_edit_layout()
        return True

    def reorder_items(self, item, old_parent, old_index, new_parent, new_index, new_prev_item, new_post_item):
        qg_item = self.ui_tree.get_by_name(item[0])
        qg_old_parent = self.ui_tree.get_by_name(old_parent[0])
        qg_new_parent = self.ui_tree.get_by_name(new_parent)
        new_index = int(new_index[0])
        old_index = int(old_index[0])
        if qg_new_parent.can_have_children:
            qg_old_parent.remove_child(qg_item)
            qg_new_parent.children.insert(new_index, qg_item)
            pc.deleteUI(self.ui_tree.children[0].instance)
            self.create_instances()
            self.ui_tree.call_post_recreate()
        else:
            pc.warning("UI Element '{}' doesn't accept children.".format(qg_new_parent.name))
        self.build_tree_view()
        self.load_edit_panel(item[0])

    def create_instances(self, item=None):
        item = item or self.ui_tree.children[0]
        # print item.instance_kwargs
        item.create_instance()
        for child in item.children:
            self.create_instances(child)

    def recreate_instances(self, *args):
        self.ui_tree.recursive_setter_dict_creation()
        pc.deleteUI(self.ui_tree.children[0].instance)
        self.create_instances()
        self.ui_tree.recursive_setter_dict_execution()

    def create_code(self, *args):
        creation_code = self.ui_tree.get_creation_code().replace("ADDITIONAL_FLAGS", "")
        post_creation_code = self.ui_tree.get_post_creation_code()
        print("{}\n{}".format(creation_code, post_creation_code))

    def call_factory(self, factory, parent, **kwargs):
        return getattr(factories, factory)(parent=parent, **kwargs)
