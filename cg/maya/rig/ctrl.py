from collections import defaultdict
import pymel.core as pc
import cg.maya.rig.utils as utils
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
    ctrl = offset_grp.getChildren()[0].getChildren()[0]

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


def glue_to_shape(ctrl, shape):
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


class StickyControl():
    def __init__(self):
        self.orig_geo_shape = None
        self.orient_parent = None
        self.maintain_orient_offset = True
        self.edit_ui = defaultdict(dict)
        self.edit_action = None
        self.edit_controler = None
        self.edit_attach_mesh = None
        self.edit_orient_object = None

    def gui(self):
        win_id = "sticky_ctrl_window"
        window_width = 250
        window_height = 275

        if pc.window(win_id, q=1, exists=1):
            pc.deleteUI(win_id)

        with pc.window(win_id, title="Sticky Control", wh=[window_width, window_height]) as self.win:
            with pc.formLayout() as form_layout:
                with pc.tabLayout(innerMarginWidth=7, innerMarginHeight=7) as tab_layout:
                    with pc.frameLayout(borderVisible=False, labelVisible=False, marginWidth=7, marginHeight=7):
                        with pc.columnLayout(adj=True, rs=6):
                            self.name_textField = pc.textFieldGrp(
                                label="Name: ", text="on_mesh", cw2=[40, 2], adj=2
                            )

                            pc.separator(h=1)

                            self.autodetect_checkBox = pc.checkBox(
                                label="Autodetect Sticky mesh", value=True,
                                cc=self.toggle_autodetect
                            )
                            self.sticky_object_text = pc.text(
                                label="Sticky mesh: Not specified", align="left",
                                font="boldLabelFont"
                            )
                            self.sticky_object_button = pc.button(
                                label="Set selected mesh as sticky mesh.", enable=False,
                                c=self.assign_sticky_object
                            )

                            pc.separator(h=1)

                            self.orient_object_text = pc.text(
                                label="Orient Object: Not specified", align="left",
                                font="boldLabelFont"
                            )
                            self.orient_object_button = pc.button(
                                label="Set Selected as orient object.",
                                c=self.assign_orient_object
                            )
                            self.maintain_offset_checkBox = pc.checkBox(
                                label="Maintain orient offset", value=True
                            )

                            pc.separator(h=1)

                            self.create_button = pc.button(
                                label="Create", enable=False,
                                c=self.create_setup
                            )
                    with pc.frameLayout(borderVisible=False, labelVisible=False, marginWidth=7, marginHeight=7):
                        with pc.columnLayout(adj=True, rs=6):
                            self.edit_sticky_ctrl_textFieldGrp = pc.textFieldButtonGrp(
                                text="No Controler specified", buttonLabel="Set selected",
                                cw2=[120, 80], adj=1, enable=True, editable=False,
                                bc=self.set_edit_controler
                            )

                            pc.separator(h=1)

                            pc.radioCollection()

                            self.edit_attach_radioButton = pc.radioButton(
                                label="Attach to another mesh",
                                onCommand=pc.Callback(self.toggle_edit_ui_enable, "attach")
                            )
                            self.edit_ui["attach"]["textFieldButtonGrp"] = pc.textFieldButtonGrp(
                                text="No mesh specified", buttonLabel="Set selected",
                                cw2=[120, 80], adj=1, enable=False, editable=False,
                                bc=self.set_attach_mesh
                            )

                            pc.separator(h=1)

                            self.edit_orient_radioButton = pc.radioButton(
                                label="Orient to another object",
                                onCommand=pc.Callback(self.toggle_edit_ui_enable, "orient")
                            )
                            self.edit_ui["orient"]["textFieldButtonGrp"] = pc.textFieldButtonGrp(
                                text="No object specified", buttonLabel="Set selected",
                                cw2=[120, 80], adj=1, enable=False, editable=False
                            )
                            self.edit_ui["orient"]["checkBox"] = pc.checkBox(
                                label="Maintain orient offset", value=True, enable=False
                            )
                            pc.separator(h=1)

                            self.edit_weights_radioButton = pc.radioButton(
                                label="Reweight Cluster via Soft Selection",
                                onCommand=pc.Callback(self.toggle_edit_ui_enable, "reweight")
                            )

                            self.edit_button = pc.button(label="Edit", enable=False, c=self.exec_edit)

            form_layout.attachForm(tab_layout, 'top', 0)
            form_layout.attachForm(tab_layout, 'left', 0)
            form_layout.attachForm(tab_layout, 'bottom', 0)
            form_layout.attachForm(tab_layout, 'right', 0)

            tab_layout.setTabLabelIndex((1, 'Create'))
            tab_layout.setTabLabelIndex((2, 'Edit'))

        self.script_job = pc.scriptJob(e=("SelectionChanged", self.check_prerequisites))
        self.win.closeCommand(self.kill_script_jobs)
        self.win.setWidthHeight([window_width, window_height])
        self.check_prerequisites()

    def exec_edit(self, *args):
        if self.edit_action == "reweight":
            self.reweight_cluster()
        elif self.edit_action == "attach":
            glue_to_shape(self.edit_controler, self.edit_attach_mesh)
        else:
            pc.warning("Not yet implemented.")

    def set_edit_controler(self, *args):
        sel = pc.selected()
        if sel:
            ctrl = sel[0]
            self.edit_cl_handle, self.edit_cl_shape, self.edit_cluster = self.get_cluster_from_ctrl(ctrl)
            if self.edit_cl_handle:
                self.edit_sticky_ctrl_textFieldGrp.setText(sel[0])
                self.edit_controler = sel[0]
                self.check_edit_prerequisites()
                return
        self.edit_sticky_ctrl_textFieldGrp.setText("Object is no Sticky Controler")
        self.edit_controler = None

    def set_attach_mesh(self, *args):
        sel = pc.selected()
        if sel:
            mesh = sel[0]
            self.edit_attach_mesh = mesh
            self.edit_ui["attach"]["textFieldButtonGrp"].setText(mesh)
        else:
            self.edit_attach_mesh = None
            self.edit_ui["attach"]["textFieldButtonGrp"].setText("No mesh specified")
        self.check_edit_prerequisites()

    def set_orient_object(self):
        pass

    def toggle_edit_ui_enable(self, section):
        self.edit_action = section
        for sec, ui_dict in self.edit_ui.items():
            for name, ui in ui_dict.items():
                ui.setEnable(False)
        uis = self.edit_ui.get(section, {})
        for name, ui in uis.items():
            ui.setEnable(True)

        self.check_edit_prerequisites()

    def check_edit_prerequisites(self):
        if not self.edit_controler or not self.edit_action:
            self.edit_button.setEnable(False)
            return
        elif self.edit_action == "attach" and not self.edit_attach_mesh:
            self.edit_button.setEnable(False)
            return
        elif self.edit_action == "orient" and not self.edit_orient_object:
            self.edit_button.setEnable(False)
            return
        self.edit_button.setEnable(True)

    def reweight_cluster(self):
        sel = pc.selected()
        if sel:
            target_mesh = self.edit_cluster.attr("outputGeometry").listConnections(type="mesh", shapes=True)[0]
            if sel[0].node() == target_mesh:
                utils.soft_cluster(cluster=self.edit_cluster)
            else:
                pc.warning("Please select Vertices of {}.".format(target_mesh))
        else:
            pc.warning("Please Soft-Select some Vertices to reweight.")

    def set_win_height(self, height):
        self.win.setHeight(height)

    def get_cluster_from_ctrl(self, ctrl):
        handle = ctrl.attr("t").listConnections(type="transform")
        if not handle:
            return None, None, None
        shape = handle[0].getShape()
        if not shape:
            return None, None, None
        cluster = handle[0].attr("worldMatrix").listConnections(type="cluster")
        if not cluster:
            return None, None, None
        return handle[0], shape, cluster[0]

    def toggle_autodetect(self, checked):
        if checked:
            self.sticky_object_button.setEnable(False)
        else:
            self.sticky_object_button.setEnable(True)

    def assign_sticky_object(self, args):
        sel = pc.selected()
        if not sel:
            self.orig_geo_shape = None
            self.sticky_object_text.setLabel("Sticky Mesh: Not specified")
            return
        if sel[0].type() == "transform":
            self.orig_geo_shape = sel[0].getShape()
            self.sticky_object_text.setLabel("Sticky Object: {}".format(sel[0]))

    def assign_orient_object(self, args):
        sel = pc.selected()
        if not sel:
            self.orient_object_text.setLabel("Orient Object: Not specified")
            self.orient_parent = None
        else:
            self.orient_object_text.setLabel("Orient Object: {}".format(sel[0].name()))
            self.orient_parent = sel[0]

    def check_prerequisites(self, *args):
        sel = pc.selected()
        if not sel or not isinstance(sel[0], pc.MeshVertex):
            self.create_button.setEnable(False)
            if self.autodetect_checkBox.getValue():
                self.sticky_object_text.setLabel("Sticky Mesh: Not specified")
            return

        if self.autodetect_checkBox.getValue():
            try:
                target_node = sel[0].node().attr("worldMesh").listConnections(type="blendShape")[0]
            except:
                self.sticky_object_text.setLabel("Sticky Mesh: Not specified")
                self.create_button.setEnable(False)
                self.orig_geo_shape = None
                return

            while target_node.type() != "transform":
                try:
                    target_node = target_node.attr("outputGeometry").listConnections()[0]
                except:
                    self.sticky_object_text.setLabel("Sticky Mesh: Not specified")
                    self.create_button.setEnable(False)
                    self.orig_geo_shape = None
                    return
            
            self.orig_geo_shape = [s for s in target_node.getShapes() if not s.getAttr("intermediateObject")][0]
            self.sticky_object_text.setLabel(
                "Sticky Mesh: {}".format(self.orig_geo_shape.name(long=None, stripNamespace=True))
            )
        else:
            if self.orig_geo_shape:
                self.create_button.setEnable(True)
            else:
                self.create_button.setEnable(False)
                self.orig_geo_shape = None

        self.create_button.setEnable(True)

    def create_setup(self, *args):
        create_on_mesh_control(
            pc.selected(fl=True)[0],
            self.orig_geo_shape,
            name=self.name_textField.getText(),
            orient_parent=self.orient_parent,
            maintain_orient_offset=self.maintain_offset_checkBox.getValue()
        )

    def kill_script_jobs(self, *args):
        pc.scriptJob(kill=self.script_job, force=True)
