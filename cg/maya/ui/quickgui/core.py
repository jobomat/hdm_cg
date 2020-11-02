# coding: utf-8
from collections import namedtuple, OrderedDict
import pymel.core as pc


def merge_two_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z


EF = namedtuple(
    "EF",
    ["ui", "ui_get", "ui_cmds", "ui_flag", "ui_kwargs", "getter", "setter", "flag_processor"]
)


class QGItem(object):
    ui_counter = 0
    editor_instance = None
    pc_prefix = ""
    editfield_map = OrderedDict([
        ("title", EF(
            ui=pc.textFieldGrp, ui_get="getText",
            ui_cmds=["textChangedCommand"], ui_flag="text", ui_kwargs={"label": "Title"},
            getter="getTitle", setter="setTitle", flag_processor=lambda x: '"{}"'.format(x)
        )),
        ("label", EF(
            ui=pc.textFieldGrp, ui_get="getText",
            ui_cmds=["textChangedCommand"], ui_flag="text", ui_kwargs={"label": "Label"},
            getter="getLabel", setter="setLabel", flag_processor=lambda x: '"{}"'.format(x)
        )),
        ("set_name", EF(
            ui=pc.textFieldGrp, ui_get="getText",
            ui_cmds=["textChangedCommand"], ui_flag="text", ui_kwargs={"label": "Name"},
            getter="get_name", setter="set_name", flag_processor=lambda x: '"{}"'.format(x)
        )),
        ("width", EF(
            ui=pc.intSliderGrp, ui_get="getValue",
            ui_cmds=["changeCommand", "dragCommand"], ui_flag="value",
            ui_kwargs={"label": "Width", "minValue": 30, "maxValue": 400,
                       "fieldMinValue": 5, "fieldMaxValue": 1000, "f": True},
            getter="getWidth", setter="setWidth", flag_processor=lambda x: x
        )),
        ("cw1", EF(
            ui=pc.intSliderGrp, ui_get="getValue",
            ui_cmds=["changeCommand", "dragCommand"], ui_flag="value",
            ui_kwargs={"label": "Label Width", "minValue": 30, "maxValue": 200,
                       "fieldMinValue": 10, "fieldMaxValue": 400, "f": True},
            getter="getLabelWidth", setter="setLabelWidth", flag_processor=lambda x: x
        )),
        ("backgroundColor", EF(
            ui=pc.colorSliderGrp, ui_get="getRgbValue",
            ui_cmds=["changeCommand", "dragCommand"], ui_flag="rgbValue",
            ui_kwargs={"label": "Background Color"},
            getter="getBackgroundColor", setter="setBackgroundColor", flag_processor=lambda x: x
        )),
        ("enableBackground", EF(
            ui=pc.checkBoxGrp, ui_get="getValue1",
            ui_cmds=["changeCommand1"], ui_flag="value1",
            ui_kwargs={"label": "Enable Background Color"},
            getter="getEnableBackground", setter="setEnableBackground", flag_processor=lambda x: x
        )),
    ])

    editfields = []

    std_layout_background = [0.26666, 0.26666, 0.26666]
    std_button_background = [0.36471, 0.36471, 0.36471]
    std_field_background = [0.1863, 0.1863, 0.1863]

    def __init__(self, pymel_class, instance_kwargs={}, editor_instance=None,
                 name="unnamed", icon_name="", parent=None, **kwargs):
        QGItem.ui_counter += 1
        self.num = QGItem.ui_counter
        self.pymel_class = pymel_class
        self.name = name
        self.icon_name = icon_name
        self.instance_kwargs = instance_kwargs
        self.instance = None
        self.parent = parent
        self.editor_instance = editor_instance or parent.editor_instance
        self.create_instance()
        self.set_name(name)
        self.children = []
        self.treeview_color = [-1, -1, -1]
        self.needs_var_name = kwargs.get("needs_var_name", False)
        self.var_name = self.get_var_name()

    def create_instance(self):
        kwargs = self.instance_kwargs.copy()
        if not kwargs.get("enableBackground", False):
            kwargs.pop('backgroundColor', None)

        if self.parent:
            kwargs['parent'] = self.parent.instance
        self.instance = getattr(pc, self.pymel_class)(**kwargs)

    def call_post_recreate(self):
        for child in self.children:
            child.call_post_recreate()

    def get_editfields(self):
        return self.editfields

    def set_name(self, name):
        self.name = name
        self.treeview_name = "{} [{}]".format(name, self.num)

    def get_name(self, *args):
        return self.name

    def get_treeview_color(self):
        return [self.treeview_name] + self.treeview_color

    def add_child(self, factory, **kwargs):
        child = self.editor_instance.call_factory(factory, parent=self, **kwargs)
        self.children.append(child)
        self.editor_instance.build_tree_view()
        pc.treeView(self.editor_instance.tree_view, edit=True, selectItem=[self.treeview_name, True])

    def get_by_name(self, name):
        return self.flatten()[name]

    def flatten(self, flat={}):
        flat[self.treeview_name] = self
        for child in self.children:
            child.flatten(flat)
        return flat

    def introspect(self, *args):
        print("\n".join(dir(self.instance)))

    def delete(self, *args):
        self.parent.remove_child(self)
        for child in self.editor_instance.edit_layout.getChildren():
            pc.deleteUI(child)
        self.parent.build_edit_layout()

    def remove_child(self, child):
        pc.deleteUI(child.instance)
        self.children.remove(child)
        self.editor_instance.build_tree_view()

    def build_edit_layout(self):
        with pc.rowLayout(nc=5, cw2=[25, 25],
                          parent=self.editor_instance.edit_layout) as self.edit_toolbar:
            pc.button(label="Introspect", w=40, c=self.introspect)
            pc.button(label="Delete", w=40, c=self.delete)

        with pc.rowLayout(nc=3, cw3=[140, 20, 220], cat=[1, "right", 0]):
            pc.text("As Variable", align="right")
            self.needs_var_name_checkbox = pc.checkBox(
                label="", value=self.needs_var_name, cc=self.set_needs_var_name
            )
            self.var_name_textfield = pc.textField(
                text=self.var_name, width=220, textChangedCommand=self.set_var_name
            )
        if self.parent and self.parent.pymel_class == "formLayout":
            self.needs_var_name_checkbox.setEnable(False)

        for kwarg in self.get_editfields():
            ef = QGItem.editfield_map[kwarg]
            if hasattr(self, ef.getter):
                val = getattr(self, ef.getter)()
            elif hasattr(self.instance, ef.getter):
                val = getattr(self.instance, ef.getter)()
            else:
                val = getattr(pc, self.pymel_class)(self.instance, q=True, **{kwarg: True})
            ctrl_kwargs = merge_two_dicts(ef.ui_kwargs, {ef.ui_flag: val})
            ctrl = ef.ui(parent=self.editor_instance.edit_layout, **ctrl_kwargs)

            for cmd in ef.ui_cmds:
                getattr(ctrl, cmd)(
                    pc.Callback(self.set_instance_attr, ef, ctrl, kwarg)
                )

    def set_instance_attr(self, ef, ctrl, instance_kwarg):
        val = getattr(ctrl, ef.ui_get)()
        if hasattr(self, ef.setter):
            val = getattr(self, ef.setter)(val)
        else:
            getattr(self.instance, ef.setter)(val)
        if val:
            self.instance_kwargs[instance_kwarg] = val
            # print self.name, self.instance_kwargs[instance_kwarg]

    def build_add_bar(self, *types):
        if len(types):
            pc.text(" Add: ", parent=self.edit_toolbar)
        if "layouts" in types:
            with pc.optionMenu(cc=self.add_from_dropdown, w=100,
                               parent=self.edit_toolbar) as self.layout_dropdown:
                for label, attributes in self.editor_instance.layouts.items():
                    pc.menuItem(label=label)
        if "controls" in types:
            with pc.optionMenu(cc=self.add_from_dropdown, w=100,
                               parent=self.edit_toolbar) as self.control_dropdown:
                for label, attributes in self.editor_instance.controls.items():
                    pc.menuItem(label=label)

    def add_from_dropdown(self, item):
        if item in self.editor_instance.layouts:
            self.add_child(self.editor_instance.layouts[item])
            self.layout_dropdown.setSelect(1)
        elif item in self.editor_instance.controls:
            self.add_child(self.editor_instance.controls[item])
            self.control_dropdown.setSelect(1)

    def get_creation_code(self, indentation=0):
        flags = []
        kwargs = self.get_clean_instance_kwargs()
        for k, v in kwargs.items():
            flags.append("{}={}".format(k, v))

        ctrl_var_name = ""
        layout_var_name = ""
        if self.needs_var_name:
            if self.children:
                layout_var_name = " as {}".format(self.get_var_name())
            else:
                ctrl_var_name = "{} = ".format(self.get_var_name())

        code = "{tabs}{_with}{ctrl_var_name}{prefix}{pc_class}({flags}ADDITIONAL_FLAGS){layout_var_name}{colon}\n".format(
            tabs="\t" * indentation,
            _with="with " if self.children else "",
            ctrl_var_name=ctrl_var_name,
            prefix=self.editor_instance.pc_prefix_textfield.getText(),
            pc_class=self.pymel_class,
            flags=", ".join(flags),
            layout_var_name=layout_var_name,
            colon=":" if self.children else ""
        )
        for child in self.children:
            code += child.get_creation_code(indentation=indentation + 1)
        return code

    def get_post_creation_code(self):
        pcc = ""
        for child in self.children:
            pcc += child.get_post_creation_code()
        return pcc

    def get_clean_instance_kwargs(self):
        kwargs = self.instance_kwargs.copy()
        if not kwargs.get("enableBackground", False):
            kwargs.pop("enableBackground", None)
            kwargs.pop("backgroundColor", None)
        for k, v in kwargs.items():
            try:
                """Python 2.7"""
                if isinstance(v, (str, unicode)):
                    kwargs[k] = '"{}"'.format(v)
            except NameError:
                """Python 3.x"""
                if isinstance(v, str):
                    kwargs[k] = '"{}"'.format(v)
        return kwargs

    def get_var_name(self):
        try:
            return self.var_name
        except AttributeError:
            return "{}_{}{}".format(
                self.name.strip().lower().replace(" ", ""),
                self.pymel_class,
                self.num
            )

    def set_needs_var_name(self, args):
        self.needs_var_name = args

    def set_var_name(self, args):
        self.var_name = args

    def flag_preprocessor(self, value):
        return value
