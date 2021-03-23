# encoding: utf-8
import pymel.core as pc


def is_exact_type(node, typename):
    return node.type() == typename


def remap_master(master_node=None, pos_value_list=[], num_childs=4):
    pass


def create_frame_caches(num_caches, anim_attr, name=None):
    """Creates num_caches frameCache nodes.
    The source AnimCurve node is the one attached to anim_attr.
    The varyTime attribute is evenly distributed from first to last key.

    :param num_caches: The number of frameCache nodes to create.
    :type num_caches: int
    :param anim_attr: The attribute to which the animCurve is attached to create the cache nodes for.
    :type anim_attr: :class:`pymel.core.nodetypes.Attribute`
    :param name: The name prefix for the cache-nodes.
    :type name: str

    """
    name = name or anim_attr.name().split(".")[-1]
    name = name.replace(".", "_")
    animcurve_node = anim_attr.connections()[0]

    keys = pc.keyframe(anim_attr, q=True, valueChange=True, timeChange=True)
    time_step = (keys[-1][0] - keys[0][0]) / (num_caches - 1)
    offset = keys[0][0]

    cache_nodes = []
    for i in range(num_caches):
        fcache = pc.createNode("frameCache", n="{}_{}_fcache".format(name, i + 1))
        fcache.setAttr("varyTime", i * time_step + offset)
        animcurve_node.output >> fcache.stream
        cache_nodes.append(fcache)

    return cache_nodes


def connect_object_attributes(from_objs, from_attrs, to_objs, to_attrs):
    """
    lame
    """
    for f, t in zip(from_objs, to_objs):
        for from_attr, to_attr in zip(from_attrs, to_attrs):
            f.attr(from_attr) >> t.attr(to_attr)


def batch_caller(batch_func, additional_kwargs={}, condition_func=None, *object_lists):
    """
    Example that orientConstraints j3-joints to j1 AND j2 joints.
    Per additional_kwargs the "maintainOffset" ("mo") parameter of the orientConstraint-Command is set to False.

    j1, j2, j3 = [j.getChildren(ad=True, type="joint") for j in pc.selected()]
    batch_caller(
        pc.orientConstraint, {"mo": False},
        lambda o: not o[0].name().endswith("_end"),
        j1, j2, j3
    )
    """
    for objs in zip(*object_lists):
        if condition_func(objs):
            batch_func(*objs, **additional_kwargs)
