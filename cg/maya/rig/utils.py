import pymel.core as pc
import maya.OpenMaya as om


def place_at_point(child, parent, orient=False):
    """Places or places and orients child at parent.

    :param child: The transform node to be placed.
    :type child: :class:`pymel.core.nodetypes.Transform`
    :param parent: The transform node to place child at.
    :type locator: :class:`pymel.core.nodetypes.Transform`
    :param orient: If True additionally orients the child to parent.
    :type orient: bool

    :returns: None
    :rtype: None
    :raises: None
    """
    if orient:
        pc.delete(pc.parentConstraint(parent, child))
    else:
        pc.delete(pc.pointConstraint(parent, child))


def locator_at_point(point, locator=True, orient=False, name=None):
    """Returns a locator or empty transform at 'point'.

    :param point: The transform node to create the locator at.
    :type point: :class:`pymel.core.nodetypes.Transform`
    :param locator: If True creates a locator else an empty transform.
    :type locator: bool
    :param orient: If True additionally orients the locator to point.
    :type orient: bool
    :name: The name prefix for the locator to be created.
    :type name: str

    :returns: A locator or empty transform.
    :rtype: :class:`pymel.core.nodetypes.Transform`
    :raises: TypeError
    """
    if not isinstance(point, pc.nodetypes.Transform):
        raise TypeError('Parameter "point" must be of type pymel-Transform.')

    name = "{}_loc".format(name or point.name())
    if locator:
        loc = pc.spaceLocator(name=name)
    else:
        loc = pc.group(empty=True, name=name)
    place_at_point(loc, point)

    return loc


def distance_between(t1, t2):
    """Returns the exact distance between transforms t1 and t2.
    Not calculated using python (sqrt((x2-x1)**2 ...) because
    of loss of precision!

    :param t1: Transform that is the starting point of measurement.
    :type t1: :class:`pymel.core.nodetypes.Transform`
    :param t2: Transform that is the end point of measurement.
    :type t2: :class:`pymel.core.nodetypes.Transform`

    :returns: The world distance between t1 and t2
    :rtype: float
    :raises: None
    """
    distance_node = pc.createNode("distanceBetween")
    loc1 = pc.group(empty=True)
    loc2 = pc.group(empty=True)
    pc_temp = [pc.pointConstraint(t1, loc1), pc.pointConstraint(t2, loc2)]
    pc.delete(pc_temp)
    loc1.translate >> distance_node.point1
    loc2.translate >> distance_node.point2
    dist = distance_node.getAttr("distance")
    pc.delete(loc1, loc2, distance_node)
    return dist


def hierarchy_len(parent, child):
    """Returns the sum of distances between pivots of a hierarchical
    structure starting with parent and ending with child. Useful e.g.
    to get the combined (bone) length of a joint-chain.

    :param parent: Starting point of the hierarchy
    :type parent: :class:`pymel.core.nodetypes.Transform`
    :param child: End point of the hierarchy
    :type child: :class:`pymel.core.nodetypes.Transform`

    :returns: Combined length from parent over child1, 2, ... to child
    :rtype: float
    :raises: None
    """
    chain = [child] + child.getAllParents()
    dist = []
    while chain[0] != parent and len(chain):
        child = chain.pop(0)
        dist.append(distance_between(child, chain[0]))
    return sum(dist)


def get_free_md_channels(
    node=None,
    name=None,
):
    """Returns the first free channel of a given multiplyDivide node.
    If no node is given or no channel is availible creates a new node.

    :param node: The multiplyDivide node
    :type node: :class:`pymel.core.nodetypes.multiplyDivide`
    :param name: Name of the node to create.
    :type name: str

    :returns: Tuple with the free to connect in- and output channel
    :rtype: :class:`pymel.core.nodetypes.Attribute`
    :raises: None
    """
    input_1_channels = ["input1X", "input1Y", "input1Z"]
    input_2_channels = ["input2X", "input2Y", "input2Z"]
    output_channels = ["outputX", "outputY", "outputZ"]

    if not node:
        node = pc.createNode("multiplyDivide", name=name or "multDiv")
        return (
            node.attr(input_1_channels[0]),
            node.attr(input_2_channels[0]),
            node.attr(output_channels[0]),
        )

    for i, channel in enumerate(input_1_channels):
        if not node.attr(channel).isConnected():
            return (
                node.attr(input_1_channels[i]),
                node.attr(input_2_channels[i]),
                node.attr(output_channels[i]),
            )


def insert_normalized_scale_node(unnormalized_attr, scalefactor_attr, normalize_node=None, name=None):
    """Adds a multyplyDivide node to unnormalized_attr (which is usually
    the output of another multyplyDivide node) and compensates its output
    by a division with scalefactor_attr. Reconnects normalized value to old destination.

    :param unnormalized_attr: The output attribute to be normalized.
    :type unnormalized_attr: :class:`pymel.core.nodetypes.Attribute`
    :param scalefactor_attr: The attribute by which to normalize.
    :type scalefactor_attr: :class:`pymel.core.nodetypes.Attribute`
    :param normalize_node: If given it is tried to use a free channel of it.
    :type normalize_node: :class:`pymel.core.nodetypes.multiplyDivide`
    :param name: The name of newly created nodes.
    :type name: str

    :returns: The multiplyDivide node that was used
    :rtype: :class:`pymel.core.nodetypes.multiplyDivide`
    :raises: None
    """
    unnormalized_attr_node = unnormalized_attr.node()
    name = name or unnormalized_attr_node.name()[:-4]

    dest_attrs = unnormalized_attr.listConnections(plugs=True)

    normalize_node_channels = get_free_md_channels(
        node=normalize_node, name="{}_normalize_div".format(name)
    )

    normalize_node = normalize_node_channels[0].node()
    normalize_node.setAttr("operation", 2)

    unnormalized_attr >> normalize_node_channels[0]
    scalefactor_attr >> normalize_node_channels[1]
    for dest_attr in dest_attrs:
	    normalize_node_channels[2] >> dest_attr

    return normalize_node


def scalefactor_node(m1, m2, div_node=None, initial_len=None, name=None):
    """Set up nodes to calculate scale factor.
    (distance(m1 to m2) / initial_len)
    If initial_len is not provided the current distance(m1 to m2) will be used
    If div_node is specified the next free channel of this node will be used.
    Otherwise a new MulitiplyDivide node will be created.

    :param m1: Measurement point 1
    :type m1: :class:`pymel.core.nodetypes.Transform`
    :param m2: Measurement point 2
    :type m2: :class:`pymel.core.nodetypes.Transform`
    :param div_node: Divide-Node to use
    :type div_node: `pymel.core.nodetypes.MultiplyDivide`
    :param initial_len: The denominator of the scale-calculation.
    :type initial_len: float
    :param name: Name prefix for all created nodes.
    :type name: str

    :returns: Tuple with multyplyDivide node
        and the attribute where the result will be present.
    :rtype: (
        `pymel.core.nodetypes.MultiplyDivide`,
        `pymel.core.general.Attribute`
    )
    :raises: None
    """

    name = name or "{}_to_{}".format(m1.name(), m2.name())

    div_node_channels = get_free_md_channels(
        node=div_node, name="{}_normalize_div".format(name)
    )
    div_node = div_node_channels[0].node()
    div_node.setAttr("operation", 2)

    distance_node = pc.createNode("distanceBetween", name="{}_dist".format(name))

    m1.getShape().worldMatrix >> distance_node.inMatrix1
    m2.getShape().worldMatrix >> distance_node.inMatrix2
    distance_node.distance >> div_node_channels[0]

    initial_len = initial_len or distance_node.getAttr("distance")
    div_node_channels[1].set(initial_len)

    return div_node, div_node_channels[2]


class BlendConstrainWeights():
    def __init__(self):
        self.script_jobs = []
        self.main_padding = 3
        self.gui()

    def gui(self):
        win_id = "blend_constrain_window"
        window_width = 400
        window_height = 255

        if pc.window(win_id, q=1, exists=1):
            pc.deleteUI(win_id)

        with pc.window(win_id, title="Blend [x = 1 - y]", wh=[window_width, window_height]) as self.win:
            with pc.formLayout(numberOfDivisions=100) as self.main_fl:
                with pc.columnLayout(adj=True) as self.top_bar:
                    with pc.horizontalLayout():
                        with pc.columnLayout(adj=True, rs=5):
                            pc.button(label="Load Driver Node",
                                      c=self.load_driver)
                            self.driver_text = pc.text(
                                label="Select Driver Attribute:", align="left")
                        with pc.columnLayout(adj=True, rs=5):
                            pc.button(label="Load Driven Node",
                                      c=self.load_driven)
                            self.driven_text = pc.text(
                                label="Select Driven Attribute:", align="left")
                with pc.horizontalLayout() as self.content_hl:
                    self.driver_scrollList = pc.textScrollList()
                    self.driven_scrollList = pc.textScrollList(
                        allowMultiSelection=True)
                with pc.horizontalLayout() as self.bottom_bar:
                    pc.button(label="Create Blend or Switch Channels",
                              c=self.create_setup)

        self.main_fl.attachForm(self.top_bar, "top", self.main_padding)
        self.main_fl.attachForm(self.top_bar, "left", self.main_padding)
        self.main_fl.attachForm(self.top_bar, "right", self.main_padding)

        self.main_fl.attachForm(self.content_hl, "left", self.main_padding)
        self.main_fl.attachForm(self.content_hl, "right", self.main_padding)

        self.main_fl.attachForm(self.bottom_bar, "left", self.main_padding)
        self.main_fl.attachForm(self.bottom_bar, "right", self.main_padding)
        self.main_fl.attachForm(self.bottom_bar, "bottom", self.main_padding)

        self.main_fl.attachControl(
            self.content_hl, "top", 0, self.top_bar
        )
        self.main_fl.attachControl(
            self.content_hl, "bottom", self.main_padding, self.bottom_bar
        )
        self.main_fl.attachNone(self.top_bar, "bottom")
        self.main_fl.attachNone(self.bottom_bar, "top")

    def load_driver(self, *args):
        self.driver_scrollList.removeAll()
        self.driver = pc.selected()[0]
        self.driver_text.setLabel(self.driver.name())
        self.driver_scrollList.append(
            [a.name().split(".")[1]
             for a in self.driver.listAttr(keyable=True)]
        )

    def load_driven(self, *args):
        self.driven_scrollList.removeAll()
        self.driven = pc.selected()[0]
        self.driven_text.setLabel(self.driven.name())
        self.driven_scrollList.append(
            [a.name().split(".")[1]
             for a in self.driven.listAttr(keyable=True)]
        )

    def create_setup(self, *args):
        driver_attrs = self.driver_scrollList.getSelectItem()
        driven_attrs = self.driven_scrollList.getSelectItem()

        if len(driver_attrs) != 1:
            pc.confirmDialog(title="Specify Driver Attribute",
                             message='Please select a driver attributes.', button=["OK"])
            return

        driver_attr = self.driver.attr(driver_attrs[0])

        if len(driven_attrs) != 2:
            pc.confirmDialog(title="Wrong Number of Driven Attibutes",
                             message='Please select exactly 2 driven attributes.', button=["OK"])
            return

        driven_1 = self.driven.attr(driven_attrs[0])
        driven_2 = self.driven.attr(driven_attrs[1])

        direct_driven = driven_1
        reverse_driven = driven_2
        reverse_node = None

        if driven_1.listConnections(destination=False) and driven_2.listConnections(destination=False):
            print driven_1.listConnections(destination=False), driven_2.listConnections(destination=False)
            if driven_1.listConnections(type="reverse"):
                reverse_node = driven_1.listConnections(
                    type="reverse", destination=False)[0]
            elif driven_2.listConnections(type="reverse"):
                reverse_node = driven_2.listConnections(
                    type="reverse", destination=False)[0]
                direct_driven = driven_2
                reverse_driven = driven_1
            else:
                pc.warning(
                    "Initial connections not set up by this script... Aborted.")
                return
        else:
            reverse_node = pc.createNode("reverse")
            driver_attr >> reverse_node.attr("inputX")

        driver_attr >> direct_driven
        reverse_node.attr("outputX") >> reverse_driven


def attach_group_to_edge(edge, name="test", grp_count=1, ctrl=True):
    pnt_on_crv_grps = []
    shape = edge.node()
    edge_num = edge.index()
    curve_from_edge = pc.createNode(
        "curveFromMeshEdge", name="{}_crv_from_edge{}".format(name, edge_num)
    )
    shape.worldMesh.worldMesh[0] >> curve_from_edge.inputMesh

    u_step = 1 if grp_count == 1 else 1.0 / float(grp_count - 1)

    for i in range(grp_count):
        point_on_curve_info = pc.createNode(
            "pointOnCurveInfo", name="{}_pnt_on_crv{}_{}".format(name, edge_num, i)
        )
        point_on_curve_info.setAttr("turnOnPercentage", 1)
        pnt_on_crv_grp = pc.group(
            empty=True, name="{}_e{}_u{}_grp".format(name, edge_num, int(i * u_step * 100))
        )
        pnt_on_crv_grp.addAttr("uPos", k=True)
        pnt_on_crv_grp.uPos >> point_on_curve_info.parameter
        pnt_on_crv_grp.setAttr("uPos", i * u_step)

        if ctrl:
            offset_grp = pc.group(empty=True, name="{}_offset_grp".format(name))
            ctrl = pc.circle(n="{}_ctrl".format(name), radius=0.2)[0]
            pc.delete(ctrl, ch=True)
            pc.parent(ctrl, offset_grp)
            pc.parent(offset_grp, pnt_on_crv_grp)

        curve_from_edge.setAttr("edgeIndex[0]", edge_num)
        curve_from_edge.outputCurve >> point_on_curve_info.inputCurve
        point_on_curve_info.position >> pnt_on_crv_grp.translate

        pnt_on_crv_grps.append(pnt_on_crv_grp)

    return pnt_on_crv_grps


def get_soft_selection_values():
    selection = om.MSelectionList()
    softSelection = om.MRichSelection()
    om.MGlobal.getRichSelection(softSelection)
    softSelection.getSelection(selection)

    dagPath = om.MDagPath()
    component = om.MObject()

    iter = om.MItSelectionList(selection, om.MFn.kMeshVertComponent)
    vtx_list = []
    weight_list = []
    while not iter.isDone():
        iter.getDagPath(dagPath, component)
        dagPath.pop()
        node = dagPath.fullPathName()
        fnComp = om.MFnSingleIndexedComponent(component)

        for i in range(fnComp.elementCount()):
            vtx_list.append("{}.vtx[{}]".format(node, fnComp.element(i)))
            weight_list.append([fnComp.element(i), fnComp.weight(i).influence()])
        iter.next()
    return vtx_list, weight_list


def soft_cluster(name="inf", cluster=None):
    vtx_list, weight_list = get_soft_selection_values()
    pc.select(cl=True)
    cluster_handle = None

    if not cluster:
        pc.select(vtx_list, r=True)
        cluster, cluster_handle = pc.cluster(relative=True, name="{}_cl".format(name))
    else:
        mesh = pc.cluster(cluster, q=True, g=True)
        pc.cluster(cluster, edit=True, g=mesh, rm=True)
        cluster_set = pc.listConnections(cluster, type="objectSet")[0]
        pc.sets(cluster_set, add=pc.ls(vtx_list))

    for vtx, weight in zip(vtx_list, weight_list):
        pc.percent(cluster, vtx, v=weight[1])
    pc.select(cl=True)
    return cluster_handle


def set_cluster_pivots_to_pos(cluster_handle, pos):
    cluster_handle.setAttr("scalePivot", pos)
    cluster_handle.setAttr("rotatePivot", pos)
    cluster_handle.getShape().setAttr("origin", pos)
