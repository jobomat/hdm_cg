import pymel.core as pc


def createStickyCtrl(component, name="mouth"):
    """
    Make sure to be in Bind-Pose
    Takes Vertex or Edge or Face
    Creates setup with sticky controller attached to selected component
    and joint that can be used to skin parts of a blendShape-duplicate

    Don't forget to orient-constrain the attach_grp to a controler/joint...
    """
    if not (obj[0].nodeType() == "mesh" and
        (isinstance(component, pc.general.MeshVertex) or
        isinstance(component, pc.general.MeshEdge) or
        isinstance(component, pc.general.MeshFace))):
        pc.warning("Select Vertex, Edge or Face of a PolyMesh.")
        return

    pc.select(cl=True)
    joint = pc.joint(p=(0, 0, 0), name="{}_sticky_bnd".format(name))
    buffer_grp = pc.group(name="{}_buffer_grp".format(name))
    pc.select([component, buffer_grp], replace=True)
    pop_constraint = pc.pointOnPolyConstraint(mo=False, weight=1)
    pc.delete(pop_constraint)
    buffer_grp.setRotation([0, 0, 0])

    pc.select(cl=True)
    ctrl = pc.circle(d=1, r=0.3, s=4, ch=0, name="{}_ctrl".format(name))[0]
    offset_grp = pc.group(ctrl, name="{}_offset_grp".format(name))
    reverse_grp = pc.group(name="{}_reverse_grp".format(name))
    attach_grp = pc.group(name="{}_attach_grp".format(name))

    pc.select([component, attach_grp], replace=True)
    pop_constraint = pc.pointOnPolyConstraint(mo=False, weight=1)

    pop_constraint.constraintRotateX // attach_grp.rotateX
    pop_constraint.constraintRotateY // attach_grp.rotateY
    pop_constraint.constraintRotateZ // attach_grp.rotateZ

    attach_grp.setRotation([0, 0, 0])

    mult_node = pc.createNode("multiplyDivide")
    mult_node.setAttr("input2X", -1)
    mult_node.setAttr("input2Y", -1)
    mult_node.setAttr("input2Z", -1)
    ctrl.translate >> mult_node.input1
    mult_node.output >> reverse_grp.translate
    ctrl.translate >> joint.translate
    ctrl.rotate >> joint.rotate


obj = pc.selected()
if obj:
    createStickyCtrl(obj[0])
