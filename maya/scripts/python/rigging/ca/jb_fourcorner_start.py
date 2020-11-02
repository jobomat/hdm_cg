import pymel.core as pc


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
        pc.addAttr(ctrl, ln=attr, r=True, hidden=False, at='double', min=0, max=1, dv=0)
    # build expression
    expressionString = """
        {0}.topRightVal = clamp( 0,1,{0}.translateY * (1 + clamp( -1,0,{0}.translateX ) ) );
        {0}.topLeftVal = clamp( 0,1,{0}.translateY * (1 - clamp( 0,1,{0}.translateX ) ) );
        {0}.bottomLeftVal = clamp( 0,1,-{0}.translateY * (1 - clamp( 0,1,{0}.translateX ) ) );
        {0}.bottomRightVal = clamp( 0,1,-{0}.translateY * (1 + clamp( -1,0,{0}.translateX ) ) );
        """.format(ctrl)
    # set expression
    pc.expression(o=ctrl, s=expressionString, n="{}_expression".format(ctrl))
    # parent
    pc.parent(ctrl, rect)


# fourCournerCtrl("test")
