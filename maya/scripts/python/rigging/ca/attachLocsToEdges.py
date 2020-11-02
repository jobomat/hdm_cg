import pymel.core as pc
import re
# edges auswaehlen
sel = pc.ls(sl=True, fl=True)

name = "test"

curves = []
groups = []
for edge in sel:
    edgenum = "".join(re.findall("[\d+]", edge.name()))
    n = edge.name().replace("[", "_").replace("]", "_").replace(".", "_")
    # augewaehlte edges duplizieren:
    dup_crv = pc.duplicateCurve(edge, n="{}crv".format(n), ch=1, rn=0, local=0)
    curves.append(dup_crv)
    # pointOnCurveInfo Node erstellen
    poc_info = pc.createNode("pointOnCurveInfo", n="{}info".format(n))
    # curve-Shape mit poc_info input verbinden & percentage einschalten:
    pc.PyNode(dup_crv[0]).getShapes()[0].worldSpace >> poc_info.inputCurve
    poc_info.setAttr("turnOnPercentage", 1)
    # locator erstellen und an position heften
    grp = pc.group(empty=True, n="{}_{}_grp".format(name, edgenum))
    poc_info.position >> grp.translate
    groups.append(grp)

pc.group(curves + groups, n="{}_crv_grp".format(curves[0][0].split("_")[0]))
