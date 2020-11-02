# coding: utf8
import pymel.core as pc


def split(joint, num_segments=2):
    child_joints = joint.getChildren(f=True, c=True, type="joint")

    if not child_joints:
        pc.warning("Joint has no child-joint. Split cannot be performed.")
        return
    if len(child_joints) > 1:
        pc.warning("Joint has more than one child-joint. Aborted.")
        return

    radius = joint.getAttr("radius")
    name = joint.name()

    child_joint = child_joints[0]
    distances = child_joint.getTranslation()
    deltas = [dist / num_segments for dist in distances]

    for i in range(1, num_segments):
        new_joint = pc.insertJoint(joint)
        new_joint = pc.joint(
            new_joint, edit=True, co=True, r=True,
            p=deltas, rad=radius, name="{}_seg_{}".format(name, i)
        )
        joint = new_joint


class SplitSelected():
    def __init__(self):
        self.win = "splitSelectedJoint_win"

        if pc.window(self.win, exists=True):
            pc.deleteUI(self.win)

        self.ui()

    def ui(self):
        with pc.window(self.win, title="Split Selected Joints", widthHeight=[300, 50], toolbox=True):
            pc.columnLayout(adjustableColumn=True)
            self.num_seg_intfield = pc.intSliderGrp(
                label='Number of Segments', columnWidth3=[110, 25, 165], field=True,
                minValue=2, maxValue=20, fieldMinValue=2, fieldMaxValue=50, value=4
            )
            with pc.rowLayout(nc=2):
                pc.button(label='Split', w=145, c=pc.Callback(self.split))
                pc.button(label='Cancel', w=145, c=pc.Callback(pc.deleteUI, self.win))

    def split(self, arg=None):
        sel = pc.selected(type="joint")
        num_segments = pc.intSliderGrp(self.num_seg_intfield, q=True, value=True)

        for joint in sel:
            split(joint, num_segments)


def create_ribs_from_copies(orig, copies):
    """Creates 'rib-like' extensions of joints.
    :param orig: The top joint of the hirarchy to attach the ribs
    :type orig:  :class:`pymel.core.nodetypes.Joint`
    :param copies: The copied and translated top joint (+children)
    :type copies:  list of :class:`pymel.core.nodetypes.Joint`

    Example usage:
    sel = pc.selected()
    orig, copies = sel[0], sel[1:]
    """
    parents = orig.getChildren(ad=True)
    parents.append(orig)

    ribs_list = []
    for rib in copies:
        children = rib.getChildren(ad=True)
        children.append(rib)
        ribs_list.append(children)

    ribs_list = zip(*ribs_list)

    for p, ribs in zip(parents, ribs_list):
        for i, c in enumerate(ribs, 1):
            c.rename("{}_rib_{}".format(p.name(), i))
            pc.parent(c, p)
