from random import uniform
import pymel.core as pc


def randomize_components(components, mini=[-0.1, -0.1, -0.1], maxi=[0.1, 0.1, 0.1], space="object"):
    for comp in components:
        new_pos = [
            pos + uniform(mi, ma)
            for pos, mi, ma
            in zip(comp.getPosition(space=space), mini, maxi)
        ]
        comp.setPosition(new_pos, space=space)
    if components[0].node().type() == "nurbsCurve":
        components[0].node().updateCurve()


def rotate_shapes(transform, amount=[90, 0, 0], pivot=None):
    """
    Rotates the components (shapes) of a given pymel-transform
    transform: The pymel transform which shapes are to rotate
    amount: Degrees to rotate around [x, y, z]
    """
    component_type = ""
    try:
        shapes = transform.getShapes()
        if hasattr(shapes[0], "vtx"):
            component_type = "vtx"
        elif hasattr(shapes[0], "cv"):
            component_type = "cv"
        else:
            pc.warning("Transform Node doesn't contain rotatable shapes.")
            return
    except IndexError:
        pc.warning("Transform Node doesn't contain any shapes.")

    sym = pc.symmetricModelling(q=True)
    pc.symmetricModelling(e=True, symmetry=False)

    pivot = pivot or transform.getAttr("worldMatrix")[3][:-1]
    component_lists = [
        getattr(shape, component_type) for shape in transform.getShapes()
    ]
    for component_list in component_lists:
        pc.rotate(
            component_list, amount, p=pivot,
            r=True, os=True, eu=True
        )
    pc.symmetricModelling(e=True, symmetry=sym)


def set_unrenderable(shapes):
    attributes = [
        "visibleInRefractions", "visibleInReflections", "primaryVisibility", "motionBlur",
        "receiveShadows", "castsShadows", "smoothShading", "aiVisibleInDiffuseReflection",
        "aiVisibleInSpecularReflection", "aiVisibleInDiffuseTransmission",
        "aiVisibleInSpecularTransmission", "aiVisibleInVolume", "aiSelfShadows"
    ]
    for shp in shapes:
        for attr in attributes:
            if shp.hasAttr(attr):
                shp.setAttr(attr, 0)
