import pymel.core as pc


def activate_guides(*args):
    guides_grp = pc.ls(regex='*l_hand_guides')[0]
    guides_grp.setAttr("visibility", True)
    guides = guides_grp.getChildren()
    for guide in guides:
        name = "*{}_bnd_ctrl_null".format(guide.name()[:-6])
        null_grp = pc.ls(regex=name)[0]
        null_grp.setAttr("visibility", False)
        pc.pointConstraint(guide, null_grp, maintainOffset=False)


def deactivate_guides(*args):
    guides_grp = pc.ls(regex='*l_hand_guides')[0]
    guides_grp.setAttr("visibility", False)
    guides = guides_grp.getChildren()
    for guide in guides:
        name = "*{}_bnd_ctrl_null".format(guide.name()[:-6])
        null_grp = pc.ls(regex=name)[0]
        null_grp.setAttr("visibility", True)
        for con in null_grp.getChildren(type="pointConstraint"):
            pc.delete(con)


def mirror_hand_positions(*args):
    guides_grp = pc.ls(regex='*l_hand_guides')[0]
    guides = guides_grp.getChildren()
    for guide in guides:
        name = "*{}_bnd_ctrl_null".format(guide.name()[:-6])
        null_grp_left = pc.ls(regex=name)[0]
        name = "*r{}".format(name[2:])
        null_grp_right = pc.ls(regex=name)[0]
        trans = null_grp_left.getTranslation()
        null_grp_right.setTranslation([-trans[0], trans[1], trans[2]])


with pc.window(tlc=[200, 240], widthHeight=[401, 127], title="Window"):
    with pc.formLayout() as freeLayout:
        text1 = pc.text(label="1. Make sure character is in bindpose, then:")
        show_btn = pc.button(c=activate_guides, enableBackground=True, w=153, backgroundColor=[0.4475109875202179, 0.6140000224113464, 0.18113002181053162], label="Show and Activate Guides")
        text2 = pc.text(label="2. Move guides to the  joint positions.")
        text3 = pc.text(label="3. When positions are set: ")
        hide_btn = pc.button(c=deactivate_guides, enableBackground=True, w=153, backgroundColor=[0.722000002861023, 0.23176199197769165, 0.23176199197769165], label="Hide and Deactivate Guides")
        text4 = pc.text(label="4. Mirror the positions from left to right")
        mirror_btn = pc.button(c=mirror_hand_positions, enableBackground=True, w=153, backgroundColor=[0.316709965467453, 0.468487024307251, 0.8100000023841858], label="Mirror")

freeLayout.attachPosition(text1, 'left', 8, 0)
freeLayout.attachPosition(text1, 'top', 10, 0)
freeLayout.attachPosition(show_btn, 'left', 242, 0)
freeLayout.attachPosition(show_btn, 'top', 7, 0)
freeLayout.attachPosition(text2, 'left', 8, 0)
freeLayout.attachPosition(text2, 'top', 40, 0)
freeLayout.attachPosition(text3, 'left', 8, 0)
freeLayout.attachPosition(text3, 'top', 70, 0)
freeLayout.attachPosition(hide_btn, 'left', 242, 0)
freeLayout.attachPosition(hide_btn, 'top', 67, 0)
freeLayout.attachPosition(mirror_btn, 'left', 242, 0)
freeLayout.attachPosition(mirror_btn, 'top', 97, 0)
freeLayout.attachPosition(text4, 'left', 8, 0)
freeLayout.attachPosition(text4, 'top', 100, 0)