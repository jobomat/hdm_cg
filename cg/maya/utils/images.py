import maya.OpenMaya as api


def get_size(image):
    img = api.MImage()
    img.readFromFile(image)

    scriptUtil = api.MScriptUtil()

    widthPtr = scriptUtil.asUintPtr()
    heightPtr = scriptUtil.asUintPtr()

    scriptUtil.setUint(widthPtr, 0)
    scriptUtil.setUint(heightPtr, 0)

    img.getSize(widthPtr, heightPtr)

    w = scriptUtil.getUint(widthPtr)
    h = scriptUtil.getUint(heightPtr)
    return w, h
