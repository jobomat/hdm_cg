import pymel.core as pc

from cg.maya.minipipe.core import read_meta, write_meta
# from cg.maya.minipipe import colors
# reload(colors)
# COLOR = colors.COLOR


def set_start_end(intField, meta):
    meta[intField.getAnnotation()] = intField.getValue()
    write_meta(meta)


def ui(parent_cl, scene, dept, *args, **kwargs):
    meta = read_meta()
    with pc.columnLayout(adj=True, p=parent_cl):
        pc.separator(style="in")
        with pc.rowLayout(nc=5):
            pc.text(label="Shot Length:", font="boldLabelFont", w=95, align="left")
            pc.text(label="Start", w=50, align="right")
            if not meta.get("start", False):
                meta["start"] = 1
                write_meta(meta)
            if not meta.get("end", False):
                meta["end"] = 50
                write_meta(meta)
            start_if = pc.intField(annotation="start", value=meta["start"], w=40)
            pc.text(label="End", w=30, align="right")
            end_if = pc.intField(annotation="end", value=meta["end"], w=40)

            start_if.changeCommand(pc.Callback(set_start_end, start_if, meta))
            end_if.changeCommand(pc.Callback(set_start_end, end_if, meta))