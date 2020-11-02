# coding: utf-8
import pymel.core as pc
import core
reload(core)


class QGWindow(core.QGItem):
    editfields = ["title"]

    def __init__(self, name, instance_kwargs, editor_instance):
        self.instance_kwargs = instance_kwargs
        self.instance_kwargs['title'] = name
        super(QGWindow, self).__init__(
            "window", name=name, icon_name="window",
            instance_kwargs=instance_kwargs, editor_instance=editor_instance
        )
        self.treeview_color = [0.173, 0.275, 0.322]
        self.can_have_children = True

    def add_child(self, factory, **kwargs):
        if self.children:
            pc.warning("Window can only contain one top layout.")
            return
        super(QGWindow, self).add_child(factory, **kwargs)

    def build_edit_layout(self):
        super(QGWindow, self).build_edit_layout()
        self.build_add_bar("layouts")
        with pc.rowLayout(nc=2):
            self.wh_intfield = pc.intFieldGrp(
                label="With | Height", numberOfFields=2,
                v=self.instance_kwargs["widthHeight"] + [0, 0], cc=self.setWidthHeight)
            pc.button(label="Read from Window", c=self.read_window_size)

    def setWidthHeight(self, *args):
        if any([x <= 0 for x in args]):
            pc.warning("Width|Height settings must be greater 0.")
            return
        self.instance.setWidthHeight(args)
        tlc = self.instance.getTopLeftCorner()
        tlc_copy = tlc[0:]
        tlc[0] -= 31 if self.instance.getTitleBar() else 0
        tlc[1] -= 8
        self.instance.setTopLeftCorner([int(v) for v in tlc])
        self.instance.setTopLeftCorner([int(v) for v in tlc_copy])
        self.instance_kwargs["widthHeight"] = args

    def read_window_size(self, *args):
        wh = [int(x) for x in self.instance.getWidthHeight()]
        self.instance_kwargs["widthHeight"] = wh
        self.wh_intfield.setValue1(wh[0])
        self.wh_intfield.setValue2(wh[1])

    def setTitle(self, title):
        self.set_name(title)
        self.instance.setTitle(title)
        self.editor_instance.build_tree_view()
        return str(title)
