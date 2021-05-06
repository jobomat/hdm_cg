from collections import defaultdict
import pymel.core as pc
import cg.maya.rig.utils as utils
from cg.maya.rig.utils import get_soft_selection_values, create_soft_cluster, edit_soft_cluster
import cg.maya.utils.nodes as nodes
import cg.maya.utils.hirarchies as hirarchies
reload(hirarchies)
reload(utils)
reload(nodes)


def create_on_mesh_control(vtx, orig_geo_shape, name="on_mesh",
                           orient_parent=None, maintain_orient_offset=True):
    """Creates a controler that follows a deforming mesh while able to deform the mesh.
    IMPORTANT: The meshVertex 'vtx' should be a vertex of a blendShape target of orig_geo_shape!

    :param vtx: The vtx that the cluster (and controler on orig_geo_shape) will be centered on.
    :type vtx: class:`pymel.core.nodetypes.MeshVertex`
    :param orig_geo_shape: The mesh that the controler will be attached to.
    :type orig_geo_shape: :class:`pymel.core.nodetypes.mesh`
    :param name: The name prefix for the cache-nodes.
    :type name: str
    :param orient_parent: Optional transform to orient the control to.
    :type orient_parent: :class:`pymel.core.nodetypes.transform`
    :param maintain_orient_offset: Maintain the offset when orient constraining?
    :type maintain_orient_offset: bool

    """
    # create "soft-cluster" and center its shape and pivot to vertex
    clust = utils.soft_cluster(name)
    utils.set_cluster_pivots_to_pos(clust, vtx.getPosition(space="world"))

    # create groups and controller attached to edge
    vtx_on_orig = pc.PyNode("{}.vtx[{}]".format(orig_geo_shape, vtx.index()))
    edge_on_orig = pc.ls(vtx_on_orig.connectedEdges(), fl=True)[0]

    attach_grp = utils.attach_group_to_edge(edge_on_orig, name, 1)[0]

    vtx_pos = abs(sum(list(vtx_on_orig.getPosition(space="world"))))
    attach_pos = abs(sum(list(attach_grp.getTranslation())))
    if abs(vtx_pos - attach_pos) > 0.001:
        attach_grp.setAttr("uPos", 1)

    offset_grp = attach_grp.getChildren()[0]
    ctrl = offset_grp.getChildren()[0]

    # connect ctrl and cluster attributes
    attrs = ["translate", "rotate", "scale"]
    nodes.connect_object_attributes([ctrl], attrs, [clust], attrs)

    # multiply node to put reversed control-translates on offset_grp
    mult = pc.createNode("multiplyDivide")

    for inp in ("input2X", "input2Y", "input2Z"):
        mult.setAttr(inp, -1)

    ctrl.translate >> mult.input1
    mult.output >> offset_grp.translate

    # orientConstraints from self.orient_parent to attach_grp
    if orient_parent:
        pc.orientConstraint(orient_parent, attach_grp, mo=maintain_orient_offset)
    pc.select(ctrl, r=True)


def glue_to_shape(ctrls, shape):
    for ctrl in ctrls:
        curve_from_edge = get_curveFromMeshEdge_node(ctrl)
        if curve_from_edge:
            shape.worldMesh.worldMesh[0] >> curve_from_edge.inputMesh


def get_curveFromMeshEdge_node(controler):
    for parent in hirarchies.list_all_parents(controler):
        if parent.hasAttr("uPos"):
            poc = parent.attr("uPos").listConnections(type="pointOnCurveInfo")
            if poc:
                cfme = poc[0].listConnections(type="curveFromMeshEdge")
                if cfme:
                    return cfme[0]
    return None


def slider_control(name, two_sided=True):
    min_val = -1 if two_sided else 0
    # build square
    rect = pc.curve(
        n="{}_frame_crv".format(name),
        d=1,
        p=[
            (-0.1, min_val, 0),
            (0.1, min_val, 0),
            (0.1, 1, 0),
            (-0.1, 1, 0),
            (-0.1, min_val, 0)
        ],
        k=[0, 1, 2, 3, 4]
    )
    rect_shape = rect.getShape()
    # set shape  to referenzed display mode
    rect_shape.overrideEnabled.set(True)
    rect_shape.setAttr("overrideDisplayType", 2)

    # the ctrl-circle
    ctrl = pc.circle(n="{}_ctrl".format(name), r=0.15)[0]
    # set limits
    pc.transformLimits(ctrl, tx=(0, 0), etx=(1, 1))
    pc.transformLimits(ctrl, ty=(min_val, 1), ety=(1, 1))
    pc.transformLimits(ctrl, tz=(0, 0), etz=(1, 1))
    # lock, hide and add attributes
    for attr in ("tx", "tz", "rx", "ry", "rz", "sx", "sy", "sz"):
        ctrl.setAttr(attr, keyable=False, lock=True, channelBox=False)

    pc.addAttr(ctrl, ln="val1", r=True, hidden=False, at='double', min=0, max=1, dv=0)
    if two_sided:
        pc.addAttr(ctrl, ln="val2", r=True, hidden=False, at='double', min=0, max=1, dv=0)
    # build expression
    expressionString = "{0}.val1 = clamp( 0, 1, {0}.ty );".format(ctrl)
    if two_sided:
        expressionString += "\n{0}.val2 = -1 * clamp( -1, 0, {0}.ty );".format(ctrl)
    # set expression
    pc.expression(o=ctrl, s=expressionString, n="{}_expression".format(ctrl))
    # parent
    pc.parent(ctrl, rect)
    return ctrl


def four_corner_control(name):
    # build square
    rect = pc.curve(
        n="{}_frame_crv".format(name),
        d=1,
        p=[
            (-1, -1, 0),
            (1, -1, 0),
            (1, 1, 0),
            (-1, 1, 0),
            (-1, -1, 0)
        ],
        k=[0, 1, 2, 3, 4]
    )
    rect_shape = rect.getShape()
    # set shape  to referenzed display mode
    rect_shape.overrideEnabled.set(True)
    rect_shape.setAttr("overrideDisplayType", 2)

    # the ctrl-circle
    ctrl = pc.circle(n="{}_ctrl".format(name), r=0.15)[0]
    # set limits
    pc.transformLimits(ctrl, tx=(-1, 1), etx=(1, 1))
    pc.transformLimits(ctrl, ty=(-1, 1), ety=(1, 1))
    pc.transformLimits(ctrl, tz=(0, 0), etz=(1, 1))
    # lock, hide and add attributes
    for attr in ["tz", "rx", "ry", "rz", "sx", "sy", "sz"]:
        ctrl.setAttr(attr, keyable=False, lock=True, channelBox=False)

    for attr in ["topLeftVal", "topRightVal", "bottomLeftVal", "bottomRightVal"]:
        pc.addAttr(ctrl, ln=attr, r=True, at='double', min=0, max=1, dv=0, keyable=True)

    # build expression
    expressionString = """
        {0}.topLeftVal = clamp( 0,1,{0}.translateY * (1 + clamp( -1,0,{0}.translateX ) ) );
        {0}.topRightVal = clamp( 0,1,{0}.translateY * (1 - clamp( 0,1,{0}.translateX ) ) );
        {0}.bottomRightVal = clamp( 0,1,-{0}.translateY * (1 - clamp( 0,1,{0}.translateX ) ) );
        {0}.bottomLeftVal = clamp( 0,1,-{0}.translateY * (1 + clamp( -1,0,{0}.translateX ) ) );
        """.format(ctrl)
    # set expression
    pc.expression(o=ctrl, s=expressionString, n="{}_expression".format(ctrl))
    # parent
    pc.parent(ctrl, rect)
    return ctrl


def create_sticky_base_setup(
    transform, name="sticky", bs_transform=None, bs_node=None, bs_channel=None, proximity_node=None
):
    sticky_grp = pc.group(empty=True, n="{}_grp".format(name))
    for channel in ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]:
        sticky_grp.attr(channel).setKeyable(
            not sticky_grp.attr(channel).isKeyable())
        sticky_grp.attr(channel).setLocked(
            not sticky_grp.attr(channel).isLocked())
    sticky_grp.addAttr("controler_visibility", at="bool", dv=1)
    sticky_grp.addAttr("sticky_blendshape_transform", at="bool")
    sticky_grp.addAttr("sticky_blendshape_node", at="bool")
    sticky_grp.addAttr("sticky_proximityPin", at="bool")
    sticky_grp.addAttr("sticky_transform", at="bool")
    sticky_grp.addAttr("sticky_controls", at="bool")
    transform.addAttr("sticky_grp", at="bool", dv=1)
    transform.sticky_grp >> sticky_grp.sticky_transform

    # check bs_transform
    shape_index = None
    if bs_node and bs_channel and bs_transform:
        shape_index = bs_channel
    else:
        if not bs_transform:
            bs_transform = pc.duplicate(transform)[0]
            bs_transform.rename("{}_bs_geo".format(name))
            bs_transform.hide()
            pc.parent(bs_transform, sticky_grp)
        if not bs_node:
            bs_node = pc.blendShape(bs_transform, transform, automatic=True)[0]
        else:
            bs_node.addTarget(
                baseObject=transform.getShape(),
                weightIndex=bs_node.weight.numElements(),
                newTarget=bs_transform.getShape(),
                fullWeight=1.0, targetType='object'
            )
        shape_index = bs_node.weight.numElements() - 1
        pc.aliasAttr("sticky_controls", "{}.w[{}]".format(
            bs_node.name(), shape_index))
    bs_node.setAttr("weight[{}]".format(shape_index), 1)

    sticky_grp.addAttr("sticky_bs_weight_index", at="short")
    sticky_grp.setAttr("sticky_bs_weight_index", shape_index)

    if not bs_transform.hasAttr("sticky_grp"):
        bs_transform.addAttr("sticky_grp", at="bool")
    sticky_grp.sticky_blendshape_transform >> bs_transform.sticky_grp
    if not bs_node.hasAttr("sticky_grp"):
        bs_node.addAttr("sticky_grp", at="bool")
    sticky_grp.sticky_blendshape_node >> bs_node.sticky_grp

    # check proximity_node
    if not proximity_node:
        pc.select(transform, r=True)
        pc.mel.eval("ProximityPin;")
        proximity_node = pc.selected()[0]
        proximity_node.rename("{}_proximityPin".format(name))
        proximity_node.setAttr("offsetOrientation", 1)
        pc.select(cl=True)
    proximity_node.addAttr("sticky_grp", at="bool")
    sticky_grp.sticky_proximityPin >> proximity_node.sticky_grp

    return sticky_grp


def get_sticky_grp(transform):
    if transform.hasAttr("sticky_grp"):
        if transform.attr("sticky_grp").listConnections():
            return transform.attr("sticky_grp").listConnections()[0]
    return None


def get_sticky_blendshape_transform(sticky_grp):
    return sticky_grp.attr("sticky_blendshape_transform").listConnections()[0]


def get_sticky_blendshape_node(sticky_grp):
    return sticky_grp.attr("sticky_blendshape_node").listConnections()[0]


def get_sticky_proximityPin(sticky_grp):
    return sticky_grp.attr("sticky_proximityPin").listConnections()[0]


def get_sticky_transform(sticky_grp):
    return sticky_grp.attr("sticky_transform").listConnections()[0]


def get_sticky_shape(sticky_grp):
    return [
        s for s in get_sticky_transform(sticky_grp).getShapes()
        if not s.getAttr("intermediateObject")
    ][0]


def get_sticky_bs_shape(sticky_grp):
    return get_sticky_blendshape_transform(sticky_grp).getShape()


def get_sticky_shape_orig(sticky_grp):
    return get_sticky_proximityPin(sticky_grp).attr("originalGeometry").listConnections()[0]


def get_ctrl_grp(ctrl):
    return ctrl.getParent().getParent().getParent()


def get_or_create_sticky_grp(transform, bs_node=None, bs_channel=None, bs_transform=None):
    if transform.hasAttr("sticky_grp"):
        con = transform.attr("sticky_grp").listConnections()
        if con:
            return con[0]
        else:
            transform.deleteAttr("sticky_grp")
    return create_sticky_base_setup(transform, bs_node=bs_node, bs_channel=bs_channel, bs_transform=bs_transform)


def create_sticky_control(
    name="sticky", transform=None,
    bs_transform=None, bs_node=None, bs_channel=None, orient_to=None,
    weight_list=None, ctrl=None, input_pin_pos=None,
    translate=True, rotate=True, scale=True
):
    if not weight_list:
        weight_list = get_soft_selection_values()

    sticky_grp = get_or_create_sticky_grp(
        transform, bs_node=bs_node, bs_channel=bs_channel, bs_transform=bs_transform,
    )
    sticky_bs_shape = get_sticky_bs_shape(sticky_grp)
    proximity_node = get_sticky_proximityPin(sticky_grp)

    if not input_pin_pos:
        input_pin_pos = get_sticky_blendshape_transform(sticky_grp).getShape().vtx[
            weight_list[0][0]
        ].getPosition(space="world")

    ctrl_grp = pc.group(empty=True, n="{}_ctrl_grp".format(name))
    sticky_grp.controler_visibility >> ctrl_grp.visibility
    pc.parent(ctrl_grp, sticky_grp)

    cluster_handle = create_soft_cluster(
        name=name, shape=sticky_bs_shape,
        weight_list=weight_list, pivot_pos=input_pin_pos
    )
    cluster_handle.hide()
    pc.parent(cluster_handle, sticky_grp)

    input_pin = pc.group(empty=True, n="{}_input_pin".format(name))
    pc.parent(input_pin, ctrl_grp)
    output_pin = pc.group(empty=True, n="{}_ouput_pin".format(name))
    pc.parent(output_pin, ctrl_grp)
    if orient_to:
        pc.orientConstraint(orient_to, output_pin, maintainOffset=True)

    input_pin.setTranslation(input_pin_pos, space="world")

    indices = proximity_node.attr("inputMatrix").getArrayIndices()
    i = 0 if not indices else max(indices) + 1
    input_pin.matrix >> proximity_node.attr("inputMatrix[{}]".format(i))
    proximity_node.attr("outputMatrix[{}]".format(
        i)) >> output_pin.offsetParentMatrix

    offset_grp = pc.group(empty=True, n="{}_offset_grp".format(name))
    ctrl = pc.circle(radius=0.2)[0]
    ctrl.rename("{}_ctrl".format(name))
    pc.delete(ctrl, ch=True)
    pc.parent(offset_grp, output_pin)
    pc.parent(ctrl, offset_grp)
    ctrl.addAttr("sticky_grp", at="bool")
    ctrl.addAttr("proximity_pin_index", at="short")
    ctrl.setAttr("proximity_pin_index", i)
    sticky_grp.sticky_controls >> ctrl.sticky_grp

    neg_mult = pc.createNode("multiplyDivide", n="{}_neg_mult".format(name))

    neg_mult.setAttr("input2", [-1, -1, -1])
    ctrl.translate >> neg_mult.input1
    neg_mult.output >> offset_grp.translate
    if translate:
        ctrl.translate >> cluster_handle.translate
    if rotate:
        ctrl.rotate >> cluster_handle.rotate
    if scale:
        ctrl.scale >> cluster_handle.scale

    pc.select(ctrl)


def create_mirrored_sticky_control(ctrl, name, mirror_matrix=[-1, 1, 1]):
    input_pin = ctrl.getParent().getParent().getSiblings()[0]
    input_pin_pos = [
        v*s for v, s in zip(input_pin.getTranslation(space="world"), mirror_matrix)
    ]

    cluster_handle = ctrl.attr(
        "translate").listConnections(type="transform")[0]
    cluster = cluster_handle.attr(
        "worldMatrix").listConnections(type="cluster")[0]
    cluster_set = pc.listConnections(cluster, type="objectSet")[0]
    pc.select(cluster_set.flattened())
    verts = pc.selected(fl=True)

    transform = get_sticky_transform(
        ctrl.getParent().getParent().getParent().getParent())

    weight_list = []
    for vert in verts:
        pc.select(vert, symmetry=True)
        sym_verts = [v for v in pc.selected() if v != vert]
        sym_vert = vert if not sym_verts else sym_verts[0]
        weight_list.append(
            (sym_vert.index(), pc.percent(cluster, vert, q=True, v=True)[0])
        )

    constraints = ctrl.getParent().getSiblings(type="orientConstraint")
    orient_con = None if not constraints else constraints[0]
    orient_to = None
    if orient_con:
        orient_to = orient_con.attr(
            "target[0].targetParentMatrix").listConnections()[0]

    create_sticky_control(
        name=name, transform=transform, bs_node=None, orient_to=orient_to,
        weight_list=weight_list, input_pin_pos=input_pin_pos
    )


class StickyControl():
    def __init__(self):
        self.win_id = "sticky_ctrl_window"
        self.sticky_bs_node = None
        self.orient_to = None
        self.bs_transform = None
        if pc.window(self.win_id, q=1, exists=1):
            pc.showWindow(self.win_id)
            return
        else:
            self.gui()
        self.mode = "create"

    def gui(self):
        window_width = 250
        window_height = 296

        if pc.window(self.win_id, q=1, exists=1):
            pc.deleteUI(self.win_id)

        with pc.window(self.win_id, title="Sticky Control", wh=[window_width, window_height]) as self.win:
            with pc.formLayout() as form_layout:
                with pc.columnLayout(adj=True) as cl:
                    with pc.frameLayout(visible=False, borderVisible=False, label="Create Sticky Control", marginWidth=7, marginHeight=7) as self.create_gui:
                        with pc.columnLayout(adj=True, rs=6):
                            self.name_textField = pc.textFieldGrp(
                                label="Name: ", text="on_mesh", cw2=[40, 2], adj=2
                            )
                            pc.separator(h=1)
                            pc.text(label="Connect:", align="left")
                            with pc.horizontalLayout():
                                self.translate_checkBox = pc.checkBox(
                                    label="Translate", value=True
                                )
                                self.rotate_checkBox = pc.checkBox(
                                    label="Rotate", value=True
                                )
                                self.scale_checkBox = pc.checkBox(
                                    label="Scale", value=True
                                )
                            pc.separator(h=1)
                            pc.text("Orient the Control to Object (Optional)")
                            with pc.horizontalLayout(ratios=[3, 1]):
                                self.orient_to_textField = pc.textField(
                                    pht="MMB Drop Object here",
                                    tcc=self.set_orient_to,
                                    editable=self.orient_to is None,
                                    text="" if self.orient_to is None else self.orient_to.name()
                                )
                                pc.button(label="Clear", c=pc.Callback(
                                    self.clear_orient_to, None))
                            pc.separator(h=1)
                            with pc.optionMenu(label="BlendShape Node: ", cc=self.build_bs_channel_menu) as self.bs_option_menu:
                                pc.menuItem("Create New")
                            with pc.optionMenu(label="BlendShape Channel: ") as self.bs_channel_menu:
                                pc.menuItem("---")
                            with pc.horizontalLayout(ratios=[3, 1]):
                                self.bs_transform_textField = pc.textField(
                                    pht="MMB Drop BlendShape Geo here",
                                    tcc=self.set_bs_transform,
                                    editable=self.bs_transform is None,
                                    text="" if self.bs_transform is None else self.bs_transform.name()
                                )
                                pc.button(label="Clear", c=pc.Callback(
                                    self.clear_bs_transform, None))
                            pc.separator(h=1)

                            self.create_button = pc.button(
                                label="Create", c=self.create_sticky_ctrl
                            )
                    with pc.frameLayout(visible=False, borderVisible=False, label="Edit / Delete Sticky Controler", marginWidth=7, marginHeight=7) as self.edit_gui:
                        with pc.columnLayout(adj=True, rs=6):
                            pc.separator(h=1)
                            pc.text(
                                label="Orient the Control to Object", align="left")
                            with pc.horizontalLayout(ratios=[2, 1, 1]):
                                self.orient_to_textField = pc.textField(
                                    pht="MMB Drop Object here",
                                    tcc=self.set_orient_to,
                                    editable=self.orient_to is None,
                                    text="" if self.orient_to is None else self.orient_to.name()
                                )
                                pc.button(label="Clear", c=pc.Callback(
                                    self.clear_orient_to, None))
                                pc.button(label="Orient!", c=pc.Callback(
                                    self.replace_orient_to))
                            pc.separator(h=1)
                            pc.text(
                                label="Check 'Symmetry' Settings before Mirroring!", align="left")
                            pc.text(
                                label="Topological Symmetry is not supported.", align="left")
                            with pc.horizontalLayout(ratios=[1, 1]):
                                self.search_textField = pc.textField(
                                    pht="Search", width=40
                                )
                                self.replace_textField = pc.textField(
                                    pht="Replace", width=40
                                )
                            pc.button(
                                label="Mirror Selected Sticky Controls",
                                c=self.create_mirrored_sticky_control
                            )
                            pc.separator(h=1)
                            self.edit_button = pc.button(
                                label="Delete Selected Controlers", c=self.delete_sticky_ctrl)
                    with pc.frameLayout(visible=True, borderVisible=False, label="Help", marginWidth=7, marginHeight=7) as self.help_gui:
                        with pc.columnLayout(adj=True, rs=6):
                            pc.text(label="CREATE CONTROLER",
                                    align="left", font="boldLabelFont")
                            pc.text(
                                label="Select a Vertex and switch to Soft-Select-Mode.\n\nScale should be frozen (1|1|1).\nNone 1 scaling may lead to strange results.", align="left")
                            pc.separator(h=1)
                            pc.text(label="EDIT OR DELETE CONTROLER",
                                    align="left", font="boldLabelFont")
                            pc.text(
                                label="Select an existing Sticky Controler.", align="left")
                            pc.separator(h=1)

            form_layout.attachForm(cl, 'top', 0)
            form_layout.attachForm(cl, 'left', 0)
            form_layout.attachForm(cl, 'bottom', 0)
            form_layout.attachForm(cl, 'right', 0)

        self.script_job = pc.scriptJob(
            e=("SelectionChanged", self.check_prerequisites))
        self.win.closeCommand(self.kill_script_jobs)
        self.win.setWidthHeight([window_width, window_height])
        self.check_prerequisites()

    def build_bs_channel_menu(self, *args):
        self.bs_channel_menu.clear()
        items = ["---"]
        if self.bs_option_menu.getEnable():
            bs.bs_channel_menu.setEnable(True)
            selection = self.bs_option_menu.getValue()
            if selection != "Create New":
                bs_node = pc.PyNode(selection)
                for i in bs_node.weightIndexList():
                    items.append(
                        bs_node.weight[i].getAlias() + " w[" + str(i) + "]")
        else:
            bs.bs_channel_menu.setEnable(False)
        self.bs_channel_menu.addMenuItems(items)

    def set_orient_to(self, obj_name=None):
        if obj_name:
            try:
                obj = pc.PyNode(obj_name)
            except:
                obj = None
            if obj and isinstance(obj, pc.nodetypes.Transform):
                self.orient_to_textField.setText(obj.name())
                self.orient_to_textField.setEditable(False)
                self.orient_to = obj
                return
        self.orient_to = None
        self.orient_to_textField.setText("")
        self.orient_to_textField.setEditable(True)

    def set_bs_transform(self, obj_name=None):
        if obj_name:
            try:
                obj = pc.PyNode(obj_name)
            except:
                obj = None
            if obj and isinstance(obj, pc.nodetypes.Transform):
                self.bs_transform_textField.setText(obj.name())
                self.bs_transform_textField.setEditable(False)
                self.bs_transform = obj
                return
        self.bs_transform = None
        self.bs_transform_textField.setText("")
        self.bs_transform_textField.setEditable(True)

    def clear_orient_to(self, *args):
        self.orient_to_textField.setText("")
        self.orient_to = None

    def clear_bs_transform(self, *args):
        self.bs_transform_textField.setText("")
        self.bs_transform = None

    def replace_orient_to(self, *args):
        for ctrl in pc.selected():
            out_pin = ctrl.getParent().getParent()
            constraint = out_pin.getChildren(type="orientConstraint")
            if constraint:
                pc.delete(out_pin.getChildren(type="orientConstraint")[0])
            if self.orient_to:
                pc.orientConstraint(self.orient_to, out_pin,
                                    maintainOffset=True)

    def hide_all_guis(self):
        self.create_gui.setVisible(False)
        self.edit_gui.setVisible(False)
        self.help_gui.setVisible(True)

    def show_gui(self, mode):
        self.hide_all_guis()
        self.help_gui.setVisible(False)
        if mode == "create":
            self.create_gui.setVisible(True)
        elif mode == "edit":
            self.edit_gui.setVisible(True)

    def check_prerequisites(self):
        sel = pc.selected()
        if not sel:
            self.hide_all_guis()
            return
        if isinstance(sel[0], pc.nodetypes.Transform):
            if not sel[0].hasAttr("sticky_grp") or not sel[0].attr("sticky_grp").listConnections():
                self.hide_all_guis()
                return

            a = sel[0].attr("sticky_grp").listConnections(
                plugs=True)[0].attrName()
            if a == "sticky_controls":
                self.enable_blendShape()
                self.show_gui("edit")
            elif a == "sticky_transform":
                self.hide_all_guis()
        elif isinstance(sel[0], pc.general.MeshVertex):
            sticky_grp = get_sticky_grp(sel[0].node().getParent())
            if sticky_grp:
                self.disable_blendShape(sticky_grp)
                self.update_bs_option_menu(
                    [get_sticky_blendshape_node(sticky_grp).name()], False)
                self.bs_transform_textField.setEnable(False)
            else:
                items = ["Create New"]
                bs_nodes = sel[0].node().listHistory(type="blendShape")
                if bs_nodes:
                    items.extend([b.name() for b in bs_nodes])
                self.update_bs_option_menu(items, True)
                self.bs_transform_textField.setEnable(True)
            self.show_gui("create")
        else:
            self.hide_all_guis()

    def disable_blendShape(self, sticky_grp):
        self.sticky_bs_node = get_sticky_blendshape_node(sticky_grp)
        self.sticky_bs_weight_index = sticky_grp.getAttr(
            "sticky_bs_weight_index")
        self.sticky_bs_node.weight[self.sticky_bs_weight_index].set(0)

    def enable_blendShape(self):
        if self.sticky_bs_node:
            self.sticky_bs_node.weight[self.sticky_bs_weight_index].set(1)

    def update_bs_option_menu(self, items, enable):
        self.bs_option_menu.clear()
        self.bs_option_menu.addMenuItems(items)
        self.bs_option_menu.setEnable(enable)

    def delete_sticky_ctrl(self, *args):
        ctrls = pc.selected()
        proximity_node = get_sticky_proximityPin(
            get_ctrl_grp(ctrls[0]).getParent())

        for ctrl in ctrls:
            in_attr = proximity_node.attr("inputMatrix[{}]".format(
                ctrl.getAttr("proximity_pin_index")
            ))
            in_attr.listConnections(plugs=True)[0] // in_attr

            out_attr = proximity_node.attr("outputMatrix[{}]".format(
                ctrl.getAttr("proximity_pin_index")
            ))
            out_attr // out_attr.listConnections(plugs=True)[0]

            pc.removeMultiInstance(out_attr, b=True)
            # delete cluster and multiply node
            pc.delete(ctrl.attr("translate").listConnections(
                type="multiplyDivide")[0])
            pc.delete(ctrl.attr("translate").listConnections(
                type="transform")[0])

            pc.delete(get_ctrl_grp(ctrl))

    def create_sticky_ctrl(self, *args):
        name = self.name_textField.getText() or "sticky"
        bs_node = None
        print self.orient_to
        if self.bs_option_menu.getEnable():
            selection = self.bs_option_menu.getValue()
            if selection != "Create New":
                bs_node = pc.PyNode(selection)

        bs_channel = self.bs_channel_menu.getValue()
        if bs_channel != "---":
            bs_channel = int(bs_channel.split("[")[1][:-1])
        else:
            bs_channel = None
        create_sticky_control(
            name=name, bs_transform=self.bs_transform,
            bs_node=bs_node, bs_channel=bs_channel, orient_to=self.orient_to,
            transform=pc.selected(fl=True)[0].node().getParent(),
            translate=self.translate_checkBox.getValue(),
            rotate=self.rotate_checkBox.getValue(),
            scale=self.scale_checkBox.getValue()
        )

    def create_mirrored_sticky_control(self, *args):
        sym_status = pc.symmetricModelling(q=True, symmetry=True)
        pc.symmetricModelling(symmetry=True)
        sym_matrix = [
            -1 if pc.symmetricModelling(q=True, axis=True) == "x" else 1,
            -1 if pc.symmetricModelling(q=True, axis=True) == "y" else 1,
            -1 if pc.symmetricModelling(q=True, axis=True) == "z" else 1
        ]
        search = self.search_textField.getText()
        replace = self.replace_textField.getText()

        for ctrl in pc.selected():
            name = ctrl.name().split("|")[-1]
            if name.endswith("_ctrl"):
                name = name[:-5]
            new_name = name
            if search and replace:
                new_name = name.replace(search, replace)
            if new_name != name:
                name = new_name
            else:
                name = name + "_mirrored"
            create_mirrored_sticky_control(
                ctrl, name, mirror_matrix=sym_matrix)
        pc.symmetricModelling(symmetry=sym_status)

    def kill_script_jobs(self, *args):
        pc.scriptJob(kill=self.script_job, force=True)
