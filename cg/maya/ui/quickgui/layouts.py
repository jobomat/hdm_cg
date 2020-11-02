# coding: utf-8
import pymel.core as pc
import core
reload(core)


class QGBaseLayout(core.QGItem):
    editfields = ["set_name", "backgroundColor", "enableBackground"]

    def __init__(self, *args, **kwargs):
        super(QGBaseLayout, self).__init__(*args, **kwargs)
        self.can_have_children = True
        self.treeview_color = [0.26, 0.61, 0.56]
        self.instance_kwargs['backgroundColor'] = core.QGItem.std_layout_background
        self.instance_kwargs['enableBackground'] = False

    def set_name(self, name):
        super(QGBaseLayout, self).set_name(name)
        self.editor_instance.build_tree_view()

    def build_edit_layout(self):
        super(QGBaseLayout, self).build_edit_layout()
        self.build_add_bar("layouts", "controls")

    def setBackgroundColor(self, *args):
        self.instance_kwargs['backgroundColor'] = args[0]
        if self.instance_kwargs['enableBackground']:
            self.instance.setBackgroundColor(self.instance_kwargs['backgroundColor'])
        return self.instance_kwargs['backgroundColor']

    def getBackgroundColor(self, *args):
        return self.instance_kwargs['backgroundColor']

    def setEnableBackground(self, *args):
        if not args[0]:
            self.instance.setBackgroundColor(core.QGItem.std_layout_background)
        else:
            self.instance.setBackgroundColor(self.instance_kwargs['backgroundColor'])
        self.instance_kwargs['enableBackground'] = args[0]
        self.instance.setEnableBackground(args[0])
        return args[0]


class QGColumnLayout(QGBaseLayout):
    editfields = QGBaseLayout.editfields

    def __init__(self, name="Column Layout", parent=None, instance_kwargs={}):
        super(QGColumnLayout, self).__init__(
            "columnLayout", name=name, icon_name="columnLayout",
            parent=parent, instance_kwargs=instance_kwargs
        )


class QGHVLayout(QGBaseLayout):
    def __init__(self, *args, **kwargs):
        self.ratios = []
        super(QGHVLayout, self).__init__(*args, **kwargs)

    def add_child(self, factory, supress_parent_edit_build=False):
        super(QGHVLayout, self).add_child(factory)
        self.ratios.append(1)
        self.redistribute()
        if not supress_parent_edit_build:
            self.append_child_layout(self.children[-1])

    def remove_child(self, child):
        self.ratios.pop(self.children.index(child))
        super(QGHVLayout, self).remove_child(child)
        self.redistribute()

    def build_edit_layout(self):
        super(QGHVLayout, self).build_edit_layout()
        for child in self.children:
            self.append_child_layout(child)

    def append_child_layout(self, child):
        pc.text(child.treeview_name, parent=self.editor_instance.edit_layout)

    def redistribute(self):
        self.instance.redistribute(*self.ratios)

    def call_post_recreate(self):
        self.redistribute()
        for child in self.children:
            child.call_post_recreate()


class QGHLayout(QGHVLayout):
    editfields = QGHVLayout.editfields

    def __init__(self, name="Horizontal Layout", parent=None):
        super(QGHLayout, self).__init__(
            "horizontalLayout", name=name, icon_name="horizontalLayout", parent=parent
        )


class QGVLayout(QGHVLayout):
    editfields = QGHVLayout.editfields

    def __init__(self, name="Vertical Layout", parent=None):
        super(QGVLayout, self).__init__(
            "verticalLayout", name=name, icon_name="verticalLayout", parent=parent
        )


class QGFreeLayout(QGBaseLayout):
    editfields = QGBaseLayout.editfields

    def __init__(self, name="Fixed Layout", parent=None, instance_kwargs={}):
        super(QGFreeLayout, self).__init__(
            "formLayout", name=name, icon_name="freeLayout", parent=parent
        )
        self.instance.dropCallback(self.drop_child_callback)
        self.needs_var_name = True

    def add_child(self, factory):
        super(QGFreeLayout, self).add_child(factory)
        self.children[-1].needs_var_name = True
        self.children[-1].instance.dragCallback(self.drag_child_callback)
        self.append_child_layout(self.children[-1])

    def drag_child_callback(self, drag_control, x, y, modifiers):
        pass

    def drop_child_callback(self, drag_control, drop_control, messages, left, top, drag_type):
        child = self.get_child_by_instancename(drag_control)
        self.position_child(child, left, top)

    def position_child(self, child, left=None, top=None):
        if left is None and top is None:
            child.left = child.top_left_ctrl.getValue1()
            child.top = child.top_left_ctrl.getValue2()
        else:
            child.left = left
            child.top = top
            if pc.intFieldGrp(child.top_left_ctrl, q=True, exists=True):
                child.top_left_ctrl.setValue1(left)
                child.top_left_ctrl.setValue2(top)
        pc.formLayout(
            self.instance, e=1, attachPosition=[child.instance, "left", child.left, 0]
        )
        pc.formLayout(
            self.instance, e=1, attachPosition=[child.instance, "top", child.top, 0]
        )

    def get_child_by_instancename(self, instancename):
        for child in self.children:
            if child.instance == instancename:
                return child

    def build_edit_layout(self):
        super(QGFreeLayout, self).build_edit_layout()
        self.needs_var_name_checkbox.setEnable(False)
        for child in self.children:
            self.append_child_layout(child)

    def append_child_layout(self, child):
        with pc.rowLayout(nc=1, parent=self.editor_instance.edit_layout):
            child.top_left_ctrl = pc.intFieldGrp(
                label=child.name, numberOfFields=2,
                value1=child.left, value2=child.top, extraLabel="left | top"
            )
            child.top_left_ctrl.changeCommand(pc.Callback(self.position_child, child))

    def get_post_creation_code(self):
        pcc = ""
        for child in self.children:
            pcc += "{layout}.attachPosition({ctrl}, 'left', {left}, 0)\n".format(
                layout=self.get_var_name(), ctrl=child.get_var_name(), left=child.left
            )
            pcc += "{layout}.attachPosition({ctrl}, 'top', {top}, 0)\n".format(
                layout=self.get_var_name(), ctrl=child.get_var_name(), top=child.top
            )
        for child in self.children:
            pcc += child.get_post_creation_code()
        return pcc
