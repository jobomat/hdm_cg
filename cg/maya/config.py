postfixes = {
    "transform": "geo",
    "shape": "shp",
    "joint": "jnt",
    "nurbsCurve": "crv",
    "bind": "bnd",
    "ikHandle": "ikh",
    "camera": "cam",
    "locator": "loc",
    "multiplyDivide": "mdn"
}

def to_postfix(node):
    ret = ""
    try:
        if node.type() == "transform" and node.getShape():
            print node.getShape().type()
            ret = postfixes[node.getShape().type()]
        else:
            ret = postfixes[node.type()]
    except KeyError:
        ret = node.type()[:3]
    except AttributeError:
        if isinstance(node, str):
            ret = node[:3]
        if isinstance(node, (int, float)):
            ret = str(node)
    return ret or "ukn"

print to_postfix(pc.selected()[0])