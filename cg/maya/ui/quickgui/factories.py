import layouts
import controls
reload(layouts)
reload(controls)


def columnLayout(parent):
    return layouts.QGColumnLayout(parent=parent, instance_kwargs={"enableBackground": False})


def hLayout(parent):
    return layouts.QGHLayout(parent=parent)


def vLayout(parent):
    return layouts.QGVLayout(parent=parent)


def freeLayout(parent):
    return layouts.QGFreeLayout(parent=parent)


def text(parent):
    return controls.QGText(parent=parent, instance_kwargs={"label": "My Text"})


def textFieldGrp(parent):
    return controls.QGTextFieldGrp(
        parent=parent, instance_kwargs={"label": "Label", "placeholderText": "Text"}
    )


def button(parent):
    return controls.QGButton(parent=parent, instance_kwargs={"label": "Button"})


def floatFieldGrp(parent):
    return controls.QGFloatFieldGrp(parent=parent)


def intFieldGrp(parent):
    return controls.QGIntFieldGrp(parent=parent)


def checkBoxGrp(parent):
    return controls.QGCheckBoxGrp(parent=parent, name="CheckboxGrp", instance_kwargs={})


def radioButtonGrp(parent):
    return controls.QGRadioButtonGrp(parent=parent, name="RadioGroup", instance_kwargs={})


def image(parent):
    return controls.QGImage(parent=parent, instance_kwargs={"image": ""})
