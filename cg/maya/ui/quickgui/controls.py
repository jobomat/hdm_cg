# coding: utf-8
import os.path
import pymel.core as pc
from cg.maya.utils.images import get_size
import cg.maya.viewport.capture as capture
import core
reload(capture)
reload(core)


class QGBaseControl(core.QGItem):
    editfields = core.QGItem.editfields

    def __init__(self, pymel_class, name="unnamed", icon_name="",
                 parent=None, instance_kwargs={}, **kwargs):
        if not os.path.isfile(os.path.join(os.path.dirname(__file__), "icons", icon_name + ".png")):
            icon_name = "defaultControl"
        super(QGBaseControl, self).__init__(pymel_class, name=name, icon_name=icon_name,
                                            parent=parent, instance_kwargs=instance_kwargs, **kwargs)
        self.treeview_color = [0.7, 0.28, 0.18]
        self.can_have_children = False
        self.top = 0
        self.left = 0
        self.top_left_ctrl = None


class QGButton(QGBaseControl):
    editfields = QGBaseControl.editfields + ["label", "width", "backgroundColor", "enableBackground"]

    def __init__(self, name="Button", icon_name="button", parent=None, instance_kwargs={}):
        # self.instance_kwargs = instance_kwargs
        super(QGButton, self).__init__(
            "button", name=name, icon_name=icon_name, parent=parent, instance_kwargs=instance_kwargs
        )
        self.instance_kwargs['backgroundColor'] = core.QGItem.std_button_background
        self.instance_kwargs['enableBackground'] = False

    def setLabel(self, label):
        self.set_name(label)
        self.instance.setLabel(label)
        self.editor_instance.build_tree_view()
        return label

    def setBackgroundColor(self, *args):
        self.instance_kwargs['backgroundColor'] = args[0]
        if self.instance_kwargs['enableBackground']:
            self.instance.setBackgroundColor(self.instance_kwargs['backgroundColor'])
        return self.instance_kwargs['backgroundColor']

    def getBackgroundColor(self, *args):
        return self.instance_kwargs['backgroundColor']

    def setEnableBackground(self, *args):
        if not args[0]:
            self.instance.setBackgroundColor(core.QGItem.std_button_background)
        else:
            self.instance.setBackgroundColor(self.instance_kwargs['backgroundColor'])
        self.instance_kwargs['enableBackground'] = args[0]
        self.instance.setEnableBackground(args[0])
        return args[0]


class QGText(QGBaseControl):
    editfields = QGBaseControl.editfields + ["label"]

    def __init__(self, name="Textfield", icon_name="text", parent=None, instance_kwargs={}):
        super(QGText, self).__init__(
            "text", name=name, icon_name=icon_name, parent=parent, instance_kwargs=instance_kwargs
        )

    def setLabel(self, label):
        self.set_name(label[0:10])
        self.instance.setLabel(label)
        self.editor_instance.build_tree_view()
        return label


class QGTextFieldGrp(QGBaseControl):
    editfields = QGBaseControl.editfields + ["label", "cw1"]

    def __init__(self, name="Text", icon_name="textFieldGrp", parent=None, instance_kwargs={}):
        instance_kwargs["cw1"] = 140
        super(QGTextFieldGrp, self).__init__(
            "textFieldGrp", name=name, icon_name=icon_name,
            parent=parent, instance_kwargs=instance_kwargs
        )

    def setLabel(self, label):
        self.set_name(label[0:10])
        self.instance.setLabel(label)
        self.editor_instance.build_tree_view()
        return label

    def setLabelWidth(self, width):
        pc.textFieldGrp(self.instance, e=True, cw=[1, width])
        return width

    def getLabelWidth(self):
        return self.instance_kwargs["cw1"]


class QGBaseFieldGrp(QGBaseControl):
    editfields = QGBaseControl.editfields + ["label"]

    def __init__(self, pymel_class, name="", icon_name="", instance_kwargs={}, parent=None):
        self.instance_kwargs = instance_kwargs

        if "numberOfFields" not in self.instance_kwargs:
            instance_kwargs["numberOfFields"] = int(pc.confirmDialog(
                message='Select the number of fields to be created',
                button=['1', '2', '3', '4'], title='Field-Group'
            ))
        self.number_of_fields = instance_kwargs["numberOfFields"]
        self.cw_key = "cw{}".format(self.number_of_fields + 1)

        if self.cw_key not in instance_kwargs:
            self.instance_kwargs[self.cw_key] = [80 for _ in range(self.number_of_fields + 1)]
        self.field_widths = instance_kwargs[self.cw_key]

        if "label" not in self.instance_kwargs:
            self.instance_kwargs["label"] = name

        self.labels = ["Label"] + ["Field {}".format(i + 1) for i in range(self.number_of_fields)]

        super(QGBaseFieldGrp, self).__init__(
            pymel_class, name=name, icon_name=icon_name, parent=parent,
            instance_kwargs=self.instance_kwargs
        )

    def setLabel(self, *args):
        self.set_name(args[0])
        self.instance.setLabel(*args)
        self.editor_instance.build_tree_view()
        return args[0]

    def build_edit_layout(self):
        super(QGBaseFieldGrp, self).build_edit_layout()
        with pc.frameLayout(label="Set Width of the fields", marginHeight=6,
                            parent=self.editor_instance.edit_layout):
            for i in range(self.number_of_fields + 1):
                self.append_child_layout(i)

    def append_child_layout(self, fieldnum):
        s = pc.intSliderGrp(label=self.labels[fieldnum], f=True, value=self.field_widths[fieldnum])
        s.dragCommand(pc.Callback(self.set_field_width, fieldnum, s))
        s.changeCommand(pc.Callback(self.set_field_width, fieldnum, s))

    def set_field_width(self, fieldnum, slider):
        self.field_widths[fieldnum] = slider.getValue()
        self.instance.columnWidth([fieldnum + 1, self.field_widths[fieldnum]])
        self.instance_kwargs[self.cw_key] = self.field_widths


class QGIntFieldGrp(QGBaseFieldGrp):
    editfields = QGBaseFieldGrp.editfields

    def __init__(self, name="Intfield", icon_name="intFieldGrp", parent=None):
        super(QGIntFieldGrp, self).__init__(
            "intFieldGrp", name=name, icon_name=icon_name,
            instance_kwargs={}, parent=parent
        )
        self.instance.setLabel(name)


class QGFloatFieldGrp(QGBaseFieldGrp):
    editfields = QGBaseFieldGrp.editfields

    def __init__(self, name="Floatfield", icon_name="floatFieldGrp", parent=None):
        super(QGFloatFieldGrp, self).__init__(
            "floatFieldGrp", name=name, icon_name=icon_name,
            instance_kwargs={}, parent=parent
        )
        self.instance.setLabel(name)


class QGOptionsGrp(QGBaseControl):
    editfields = QGBaseControl.editfields + ["label"]

    def __init__(self, pymel_class, name="", icon_name="", instance_kwargs={}, parent=None):
        types = {"checkBoxGrp": "numberOfCheckBoxes", "radioButtonGrp": "numberOfRadioButtons"}
        numberOfOptions = types[pymel_class]

        if numberOfOptions not in instance_kwargs:
            instance_kwargs[numberOfOptions] = int(pc.confirmDialog(
                message='Select the number of Options to be created',
                button=['1', '2', '3', '4'], title='Option-Group'
            ))
        self.number_of_fields = instance_kwargs[numberOfOptions]

        if "vertical" not in instance_kwargs:
            orientation = pc.confirmDialog(
                message='Orientation', button=['Horizontal', 'Vertical'],
                defaultButton="Horizontal", title='Field-Group'
            )
            instance_kwargs["vertical"] = orientation == "Vertical"

        if "label" not in instance_kwargs:
            instance_kwargs['label'] = name

        # if self.number_of_fields > 1:
        self.cw_key = "cw{}".format(self.number_of_fields + 1)
        if self.cw_key not in instance_kwargs:
            instance_kwargs[self.cw_key] = [80 for _ in range(self.number_of_fields + 1)]
        self.field_widths = instance_kwargs[self.cw_key]

        if self.number_of_fields > 1:
            self.la_key = "la{}".format(self.number_of_fields)
            if self.la_key not in instance_kwargs:
                instance_kwargs[self.la_key] = [
                    "Opt {}".format(i + 1) for i in range(self.number_of_fields)
                ]
            self.labels = [instance_kwargs['label']] + instance_kwargs[self.la_key]

        super(QGOptionsGrp, self).__init__(
            pymel_class, name=name, icon_name=icon_name,
            instance_kwargs=instance_kwargs, parent=parent
        )

    def setLabel(self, *args):
        self.set_name(args[0])
        self.instance.setLabel(*args)
        self.editor_instance.build_tree_view()
        return args[0]

    def build_edit_layout(self):
        super(QGOptionsGrp, self).build_edit_layout()
        if self.number_of_fields == 1:
            return None
        label = {"checkBoxGrp": "Checkbox Labels", "radioButtonGrp": "Radiobutton Labels"}
        with pc.frameLayout(label=label[self.pymel_class], marginHeight=6,
                            parent=self.editor_instance.edit_layout):
            if self.number_of_fields > 1:
                with pc.rowLayout(nc=self.number_of_fields):
                    for i in range(self.number_of_fields):
                        self.append_name_layout(i + 1)
        label = {"checkBoxGrp": "Checkbox Widths", "radioButtonGrp": "Radiobutton Widths"}
        with pc.frameLayout(label=label[self.pymel_class], marginHeight=6,
                            parent=self.editor_instance.edit_layout):
            with pc.columnLayout(adjustableColumn=True, rs=6):
                for i in range(self.number_of_fields + 1):
                    self.append_width_layout(i)

    def append_name_layout(self, fieldnum):
        tf = pc.textField(text=self.labels[fieldnum])
        tf.textChangedCommand(pc.Callback(self.set_field_label, fieldnum, tf))
        tf.changeCommand(pc.Callback(self.set_field_label, fieldnum, tf))

    def append_width_layout(self, fieldnum):
        s = pc.intSliderGrp(
            label=self.labels[fieldnum] if fieldnum else self.name,
            f=True, value=self.field_widths[fieldnum])
        s.dragCommand(pc.Callback(self.set_field_width, fieldnum, s))
        s.changeCommand(pc.Callback(self.set_field_width, fieldnum, s))

    def set_field_width(self, fieldnum, slider):
        self.field_widths[fieldnum] = self.instance_kwargs[self.cw_key][fieldnum] = slider.getValue()
        self.instance.columnWidth([fieldnum + 1, self.field_widths[fieldnum]])

    def set_field_label(self, fieldnum, textfield):
        self.labels[fieldnum] = self.instance_kwargs[self.la_key][fieldnum - 1] = textfield.getText()
        getattr(self.instance, "setLabel{}".format(fieldnum))(self.labels[fieldnum])


class QGCheckBoxGrp(QGOptionsGrp):
    editfields = QGOptionsGrp.editfields

    def __init__(self, name="Check Box", icon_name="checkBoxGrp", instance_kwargs={}, parent=None):
        super(QGCheckBoxGrp, self).__init__(
            "checkBoxGrp", name=name, icon_name=icon_name,
            instance_kwargs=instance_kwargs, parent=parent
        )


class QGRadioButtonGrp(QGOptionsGrp):
    editfields = QGOptionsGrp.editfields

    def __init__(self, name="Radiobtn", icon_name="radioButtonGrp", instance_kwargs={}, parent=None):
        super(QGRadioButtonGrp, self).__init__(
            "radioButtonGrp", name=name, icon_name=icon_name,
            instance_kwargs=instance_kwargs, parent=parent
        )


class QGImage(QGBaseControl):
    editfields = QGBaseControl.editfields

    def __init__(self, name="Image", icon_name="image", parent=None, instance_kwargs={}):
        super(QGImage, self).__init__(
            "image", name=name, icon_name=icon_name, parent=parent, instance_kwargs=instance_kwargs
        )
        if self.instance.getImage():
            w, h = get_size(self.instance.getImage())
            self.instance.setWidth(w)
            self.instance.setHeight(h)

    def build_edit_layout(self):
        super(QGImage, self).build_edit_layout()
        with pc.rowLayout(nc=3, parent=self.editor_instance.edit_layout, cw=[1, 80]):
            pc.button(label="Select Image", c=self.select_image)
            pc.button(label="From 3D View", c=self.set_from_3d_view)
            self.full_path_text = pc.text(label="No Image selected.")
        self.update_editor()

    def select_image(self, *args):
        image = pc.fileDialog()
        if not image:
            return
        self.set_image(image)

    def set_image(self, image, w=None, h=None):
        self.instance_kwargs["image"] = str(image)
        self.instance.setImage(self.instance_kwargs["image"])
        if w is None or h is None:
            w, h = get_size(self.instance_kwargs["image"])
        self.instance.setWidth(w)
        self.instance.setHeight(h)
        self.update_editor()

    def set_from_3d_view(self, *args):
        capture.screenshot(callback=self.set_image)

    def update_editor(self):
        if not self.instance_kwargs["image"]:
            return
        self.full_path_text.setLabel(self.instance_kwargs["image"])
        # self.file_text.setLabel(basename(self.instance_kwargs["image"]))
