import pymel.core as pmc
from string import letters
import mayautils
# creates variable containing default name
fp = 'flexiPlane_'
sur = 'surface_'
YELLOW = 17
SETTINGS_DEFAULT = {
    'prefix': 'char',
    'num': 01,
}


#----------------------------------------------------------------------------------------------#

# creates material for flexiPlane 
def flexiplane_material(settings=SETTINGS_DEFAULT):
    """
    builds shading network for flexiPlane
    :return: shader and shading group
    """
    # creates shader
    fp_mat = pmc.shadingNode('lambert',
                             asShader=True,
                             n='%s%smaterial_%i' % (fp, sur, settings['num']))
    # creates shading group
    fp_matsg = pmc.sets(r=True,
                        nss=True,
                        em=True,
                        n='%s%smaterial_%iSG' % (fp, sur, settings['num']))
    connect = fp_mat.outColor >> fp_matsg.surfaceShader
    print connect
    fp_mat.color.set(0.2, 0.4, 0.9, type='double3')
    fp_mat.transparency.set(0.7, 0.7, 0.7, type='double3')
    return fp_mat, fp_matsg


#----------------------------------------------------------------------------------------------#

# function to make surface not render
def no_render(tgt):
    """
    makes selected node non-renderable
    :param tgt: node to be affected
    """
    tgt.castsShadows.set(0)
    tgt.receiveShadows.set(0)
    tgt.motionBlur.set(0)
    tgt.primaryVisibility.set(0)
    tgt.smoothShading.set(0)
    tgt.visibleInReflections.set(0)
    tgt.visibleInRefractions.set(0)


#----------------------------------------------------------------------------------------------#

# function to lock and hide attributes
def lock_and_hide_all(node):
    """
    lock and hide all transform attributes of selected node
    :param node: node to be affected
    """
    node.tx.set(l=1, k=0, cb=0)
    node.ty.set(l=1, k=0, cb=0)
    node.tz.set(l=1, k=0, cb=0)
    node.rx.set(l=1, k=0, cb=0)
    node.ry.set(l=1, k=0, cb=0)
    node.rz.set(l=1, k=0, cb=0)
    node.sx.set(l=1, k=0, cb=0)
    node.sy.set(l=1, k=0, cb=0)
    node.sz.set(l=1, k=0, cb=0)


#----------------------------------------------------------------------------------------------#

# function to create control curves
def cnt_square(settings=SETTINGS_DEFAULT, name=None, pos=None):
    """
    create square control curve
    :param settings: dictionary holding node number
    :param name: control curve name
    :param pos: control curves final position
    :return: control curve
    """
    if not name:
        name = 'cnt_%i' % settings['num']
    if not pos:
        pos = [0, 0, 0]
    fp_cnt = pmc.curve(d=1,
                       p=[(-1, 0, 1), (1, 0, 1), (1, 0, -1), (-1, 0, -1), (-1, 0, 1)],
                       k=[0, 1, 2, 3, 4],
                       n='%s' % name)
    fp_cnt.overrideEnabled.set(1)
    fp_cnt.overrideColor.set(17)
    pmc.move(pos,
             rpr=True)
    pmc.scale(0.5,
              0.5,
              0.5,
              r=True)
    pmc.makeIdentity(t=1,
                     r=1,
                     s=1,
                     a=True)
    pmc.xform(roo='xzy')
    return fp_cnt


#----------------------------------------------------------------------------------------------#

# function to create global move control curve
def global_cnt(name='cnt', settings=SETTINGS_DEFAULT):
    """
    create global control curve
    :param name: string for control curve name
    :param settings: dictionary holding node number
    :return: control curve
    """
    # creates primary global control curve
    glb_cnt = pmc.circle(c=[0, 0, -2],
                         sw=360,
                         r=0.3,
                         nr=[0, 1, 0],
                         ch=0,
                         n='%sglobal_%i' % (name, settings['num']))[0]
    # grab its shape and recolors it

    glb_cntshape = glb_cnt.getShape()
    glb_cntshape.overrideEnabled.set(1)
    glb_cntshape.overrideColor.set(17)
    # adds the volume label and an enable attribute
    pmc.addAttr(ln='_',
                at='enum',
                en='volume:')
    glb_cnt._.set(e=True,
                  cb=True)
    pmc.addAttr(ln='enable',
                sn='en',
                at='bool',
                k=True,
                h=False)
    # create secondary control curve 
    glb_cnt_b = pmc.circle(c=[0, 0, 2],
                           sw=360,
                           r=0.3,
                           nr=[0, 1, 0],
                           ch=0,
                           n='%sglobal_b_%i' % (name, settings['num']))[0]
    # grabs it's shape recolors it
    glb_cnt_bshape = glb_cnt_b.getShape()
    glb_cnt_bshape.overrideEnabled.set(1)
    glb_cnt_bshape.overrideColor.set(17)
    # parents the shapeNode of secondary curve the primary curve  
    pmc.parent(glb_cnt_bshape,
               glb_cnt,
               r=True,
               s=True)
    # deletes empty transformNode
    pmc.delete(glb_cnt_b)
    # return primary control transformNode
    pmc.select(glb_cnt,
               r=True)
    return glb_cnt

#----------------------------------------------------------------------------------------------#
def joint_cnt(joint, name, color=YELLOW):
    cnt = pmc.curve(d=2,
                    p=[[1, 0, 3.2], [1, 0, 3.2], [2.8, 0, 2.75], [3.5, 0, 1], [3.5, 0, 1],
                       [4, 0, 1], [4, 0, 1], [4, 0, 2], [4, 0, 2], [5, 0, 0], [5, 0, 0],
                       [4, 0, -2], [4, 0, -2], [4, 0, -1], [4, 0, -1], [3.5, 0, -1],
                       [3.5, 0, -1], [2.8, 0, -2.75], [1, 0, -3.2], [1, 0, -3.2], [1, 0, -4],
                       [1, 0, -4], [2, 0, -4], [2, 0, -4], [0, 0, -5], [0, 0, -5],
                       [-2, 0, -4], [-2, 0, -4], [-1, 0, -4], [-1, 0, -4], [-1, 0, -3.2],
                       [-1, 0, -3.2], [-2.8, 0, -2.75], [-3.5, 0, -1], [-3.5, 0, -1],
                       [-4, 0, -1], [-4, 0, -1], [-4, 0, -2], [-4, 0, -2], [-5, 0, 0],
                       [-5, 0, 0], [-4, 0, 2], [-4, 0, 2], [-4, 0, 1], [-4, 0, 1],
                       [-3.5, 0, 1], [-3.5, 0, 1], [-2.8, 0, 2.75], [-1, 0, 3.2],
                       [-1, 0, 3.2], [-1, 0, 4], [-1, 0, 4], [-2, 0, 4], [-2, 0, 4],
                       [0, 0, 5], [0, 0, 5], [2, 0, 4], [2, 0, 4], [1, 0, 4], [1, 0, 4],
                       [1, 0, 3.2]],
                    k=[0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
                       19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35,
                       36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53,
                       54, 55, 56, 57, 58, 59, 59],
                    n='%s' % name)
    cntshp = cnt.getShape()
    cntshp.overrideEnabled.set(1)
    cntshp.overrideColor.set(color)
    cnt.rz.set(90)
    cnt.scale.set([0.213, 0.213, 0.213])
    con = pmc.pointConstraint(joint, cnt, mo=False)
    pmc.delete(con)
    pmc.select(cnt, r=True)
    pmc.makeIdentity(cnt,
                     t=1,
                     r=1,
                     s=1,
                     a=True)
    cnt = pmc.ls(r=True, sl=True)
    return cnt


#----------------------------------------------------------------------------------------------#

def flexiplane_mid_cc(name=None, color=None):
    if not name:
        name = 'cnt_mid_'
    if not color:
        color = 17

    cc = pmc.curve(d=1,
                   p=[[-0.326, 0.651, -0.701], [-0.326, 0.842, -0.989], [-0.653, 0.842, -0.989],
                      [0, 1.036, -1.28], [0.653, 0.842, -0.989], [0.326, 0.842, -0.989],
                      [0.326, 0.649, -0.698], [0.326, -0.649, -0.698], [0.326, -0.842, -0.989],
                      [0.653, -0.842, -0.989], [0, -1.036, -1.28], [-0.653, -0.842, -0.989],
                      [-0.326, -0.842, -0.989], [-0.326, -0.649, -0.698], [-0.326, 0.651, -0.701]],
                   k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
                   n=name)
    cc_shp = cc.getShape()
    cc_shp.overrideEnabled.set(1)
    cc_shp.overrideColor.set(color)

    r_values = [90, 180, 270]
    cc_children = [pmc.duplicate(cc)[0] for i in range(0, 3)]
    [cc_children[i].ry.set(r_values[i]) for i in range(0, 3)]
    [pmc.makeIdentity(i, t=1, r=1, s=1, a=True) for i in cc_children]
    cc_children_shp = [i.getShape() for i in cc_children]
    [i.setParent(cc) for i in cc_children]
    pmc.parent(cc_children_shp, cc, r=True, shape=True)
    pmc.delete(cc_children)

    cc.ry.set(45)
    cc.rz.set(90)
    pmc.makeIdentity(cc, t=1, r=1, s=1, a=True)
    cc.rx.set(l=1, k=0, cb=0)
    cc.ry.set(l=1, k=0, cb=0)
    cc.rz.set(l=1, k=0, cb=0)
    cc.sx.set(l=1, k=0, cb=0)
    cc.sy.set(l=1, k=0, cb=0)
    cc.sz.set(l=1, k=0, cb=0)
    pmc.select(cl=True)

    return cc


#----------------------------------------------------------------------------------------------#

# funtion to create cluster
def make_cluster(target,
                 name=None,
                 origin=0,
                 pos_x=0,
                 pos_y=0,
                 pos_z=0):
    """
    creates a cluster on targeted cvs
    :param target: affect cvs
    :param name: name for cluster
    :param origin: integer value for cluster originX
    :param pos_x: integer for x value for move
    :param pos_y: integer for y value for move
    :param pos_z: integer for z value for move
    :return: new cluster
    """
    cl = pmc.cluster(target,
                     rel=1,
                     en=1.0,
                     n=name)
    if origin != 0:
        cl[1].originX.set(origin)
        pmc.move(pos_x, pos_y, pos_z, cl[1].scalePivot, cl[1].rotatePivot)
    else:
        pass
    return cl


#----------------------------------------------------------------------------------------------#

#function for creating and attaching follicles to flexiplane surface 
def create_follicle(onurbs,
                    name,
                    upos=0.0,
                    vpos=0.0):
    # manually place and connect a follicle onto a nurbs surface.
    if onurbs.type() == 'transform':
        onurbs = onurbs.getShape()
    elif onurbs.type() == 'nurbsSurface':
        pass
    else:
        'Warning: Input must be a nurbs surface.'
        return False
    
    # create a name with frame padding
    pname = '%sShape' % name


    ofoll = pmc.createNode('follicle', name=pname)
    onurbs.local.connect(ofoll.inputSurface)
    # if using a polygon mesh, use this line instead.
    # (The polygons will need to have UVs in order to work.)
    #oMesh.outMesh.connect(oFoll.inMesh)

    onurbs.worldMatrix[0].connect(ofoll.inputWorldMatrix)
    ofoll.outRotate.connect(ofoll.getParent().rotate)
    ofoll.outTranslate.connect(ofoll.getParent().translate)
    ofoll.parameterU.set(upos)
    ofoll.parameterV.set(vpos)
    ofoll.getParent().t.lock()
    ofoll.getParent().r.lock()

    return ofoll


def cluster_curve(curve, name, settings=SETTINGS_DEFAULT):
    """
    adds clusters to 3 cv curve
    :param curve: curve node to be affected
    :param name: string for cluster names
    :param settings: dictionary that holds node number
    :return: new clusters
    """
    cl_a = make_cluster(target=curve.cv[0:1],
                        name='%scl_a_%i' % (name, settings['num']),
                        origin=-6,
                        pos_x=-5,
                        pos_z=-5)

    cl_b = make_cluster(target=curve.cv[1:2],
                        name='%scl_b01' % name,
                        origin=6,
                        pos_x=5,
                        pos_z=-5)

    cl_mid = make_cluster(target=curve.cv[1],
                          name='%scl_mid01' % name)

    # redistributes cluster weight
    pmc.percent(cl_a[0], curve.cv[1], v=0.5)
    pmc.percent(cl_b[0], curve.cv[1], v=0.5)
    return cl_a, cl_b, cl_mid


#----------------------------------------------------------------------------------------------#

def flexiplane(settings=SETTINGS_DEFAULT):
    """
    builds flexi plane rig module
    :param settings: dictionary that holds prefix and node number values
    :return: flexiplane global control curve node
    """
    with mayautils.undo_chunk():
        fp_name = '%s_flexiPlane_' % settings['prefix']

        #creates flexiPlane surface
        fp_surf = pmc.nurbsPlane(ax=[0, 1, 0],
                                 w=10,
                                 lr=0.2,
                                 d=3,
                                 u=5,
                                 v=1,
                                 ch=0,
                                 n='%s%s_%i' % (fp_name, sur, settings['num']))[0]

        """assigns flexiPlane material to surface
        pmc.sets('flexiPlane_surface_material01SG',
                 e=True,
                 fe=fp_surf)"""


        #runs create_follicle function
        """
        pmc.select(fp_surf,
                   r=True)
        my_obj = pmc.selected()[0]
        """
        how_many_flc = 5
        v = 0.1
        num = 0
        flcs = []
        for i in range(0, how_many_flc):
            ofoll = create_follicle(fp_surf,
                                    '%sflc_%s_%i' % (fp_name, letters[num], settings['num']),
                                    v,
                                    0.5)
            flcs.append(ofoll)
            v += 0.2
            num += 1
        ### may have to come back to this for creating multiple flexiplanes
        #groups follicles together
        flc_grp = pmc.group(flcs, n='%sflcs_%i' % (fp_name, settings['num']))

        #creates flexiPlane controls curves at each end
        cnt_a = cnt_square(name='%scnt_a_%i' % (fp_name, settings['num']),
                           pos=[-5, 0, 0])
        cnt_ashape = cnt_a.getShape()
        pmc.rename(cnt_ashape, '%sShape' % cnt_a)

        cnt_b = cnt_square(name='%scnt_b_%i' % (fp_name, settings['num']),
                           pos=[5, 0, 0])
        cnt_bshape = cnt_b.getShape()
        pmc.rename(cnt_bshape, '%sShape' % cnt_b)

        pmc.select(cl=True)

        #creates flexiPlane blendshape
        fp_bshp = pmc.duplicate(fp_surf, n='%sbshp_%s_%i' % (fp_name, sur, settings['num']))[0]
        pmc.move(0, 0, -5, fp_bshp)

        fps_bshp_node = pmc.blendShape(fp_bshp, fp_surf, n='%sbshpNode_%s%i' % (fp_name, sur, settings['num']))[0]
        pmc.setAttr('%s.%s' % (fps_bshp_node, fp_bshp), 1)

        #pmc.rename('tweak1', '%sbshp_%stweak_01' % (fp_name, sur))

        #creates curve for wire deformer
        fp_curve = pmc.curve(d=2,
                             p=[(-5, 0, -5), (0, 0, -5), (5, 0, -5)],
                             k=[0, 0, 1, 1],
                             n='%swire_%s%i' % (fp_name, sur, settings['num']))
        cl_a, cl_b, cl_mid = cluster_curve(fp_curve, fp_name)

        # create and place twist deformer
        pmc.select(fp_bshp)
        fp_twist = pmc.nonLinear(type='twist', lowBound=-1, highBound=1)
        # displays warning: pymel.core.general : could not create desired mfn. Defaulting MfnDependencyNode.
        # doesn't seem to affect anything though
        pmc.rename(fp_twist[0], '%stwistAttr_surface_%i' % (fp_name, settings['num']))
        pmc.rename(fp_twist[1], '%stwist_%i_Handle' % (fp_name, settings['num']))
        fp_twist[1].rz.set(90)

        #connect start and end angle to their respective control
        connect = cnt_b.rx >> fp_twist[0].startAngle
        connect = cnt_a.rx >> fp_twist[0].endAngle

        # skins wire to blendshape
        fp_wire = pmc.wire(fp_bshp,
                           w=fp_curve,
                           gw=False,
                           en=1,
                           ce=0,
                           li=0,
                           n='%swireAttrs_%s%i' % (fp_name, sur, settings['num']))
        fp_wire[0].dropoffDistance[0].set(20)
        hist = pmc.listHistory(fp_surf)
        tweaks = [t for t in hist if 'tweak' in t.nodeName()]
        pmc.rename(tweaks[2], '%scl_cluster_tweak_%i' % (fp_name, settings['num']))
        pmc.rename(tweaks[0], '%swireAttrs_%stweak_%i' % (fp_name, sur, settings['num']))
        pmc.rename(tweaks[1], '%sextra_%stweak_%i' % (fp_name, sur, settings['num']))

        # group clusters
        cl_grp = pmc.group(cl_a[1],
                           cl_b[1],
                           cl_mid[1],
                           n='%scls_%i' % (fp_name, settings['num']))
        lock_and_hide_all(cl_grp)

        # creates mid control
        cnt_mid = flexiplane_mid_cc(name='%scnt_mid_%i' % (fp_name, settings['num']))

        #no_render(cnt_mid)
        # groups mid control and constrain that to controls a & b...
        #...so that it stays in the center of the 2 controls
        cnt_mid_grp = pmc.group(cnt_mid, n='%sgrp_midBend_%i' % (fp_name, settings['num']))
        pmc.pointConstraint(cnt_a,
                            cnt_b,
                            cnt_mid_grp,
                            o=[0, 0, 0],
                            w=1)

        # groups controls together and locks and hides group attributes
        cnt_grp = pmc.group(cnt_a, cnt_b, cnt_mid_grp, n='%scnts_%i' % (fp_name, settings['num']))
        lock_and_hide_all(cnt_grp)

        # connecting translate attrs of control curves for to the clusters
        connect = cnt_a.t >> cl_a[1].t
        connect = cnt_b.t >> cl_b[1].t
        connect = cnt_mid.t >> cl_mid[1].t

        # makes flexiPlane and blendShape surfaces non renderable
        no_render(fp_surf)
        no_render(fp_bshp)

        # groups everything under 1 group then locks...
        #...and hides the transform attrs of that group
        fp_grp = pmc.group([fp_surf,
                           flc_grp,
                           fp_bshp,
                           fp_wire,
                           '%swire_%s%iBaseWire' % (fp_name, sur, settings['num']),
                           cl_grp,
                           cnt_grp,
                           fp_twist[1]],
                           n='%s%i' % (fp_name, settings['num']))
        lock_and_hide_all(fp_grp)

        # creates global move group and extraNodes
        fp_gm_grp = pmc.group(fp_surf,
                              cnt_grp,
                              n='%sglobalMove_%i' % (fp_name, settings['num']))
        fp_xnodes_grp = pmc.group(flc_grp,
                                  fp_bshp,
                                  fp_wire,
                                  '%swire_%s%iBaseWire' % (fp_name, sur, settings['num']),
                                  cl_grp,
                                  fp_twist[1],
                                  n='%sextraNodes_%i' % (fp_name, settings['num']))

        num = 0
        posx = -4
        jnts = []
        for i in range(0, how_many_flc):
            parent = flcs[num].getParent()
            # scale constrains follicles to global move group
            pmc.scaleConstraint(fp_gm_grp, parent)

            jnt = pmc.joint(p=(posx, 0, 0),
                            n='%sbind_%s_%i' % (fp_name, letters[num], settings['num']),
                            rad = 0.5)
            cnt = joint_cnt(jnt,
                            '%sANIM_%s_%i' % (fp_name, letters[num], settings['num']))
            pmc.parent(jnt, cnt)
            pmc.parent(cnt, parent)
            jnts.append(jnt)
            num += 1
            posx += 2
        print jnts
        # creates global move control
        fp_gm_cnt = global_cnt(name='%scnt_' % fp_name,
                               settings=settings)

        # moves global control into flexiPlane group...
        #...then parent global move group to global move control.

        pmc.parent(fp_gm_cnt, fp_grp)
        pmc.parent(fp_gm_grp, fp_gm_cnt)

        # locks and hides transformNodes flexiPlane surface
        lock_and_hide_all(fp_surf)

        # selects the wire deformer and creates a curve info node...
        #...to get the wire deformers length
        pmc.select(fp_curve, r=True)
        length = pmc.arclen(ch=1)
        length.rename('%scurveInfo_%i' % (fp_name, settings['num']))

        # creates a multiplyDivideNode for squashStretch length...
        #...and sets it operation to divide
        fp_div = pmc.createNode('multiplyDivide',
                                n='%sdiv_squashStretch_length_%i' % (fp_name, settings['num']))
        fp_div.operation.set(2)

        # secondary multDivNode for volume, sets input1X to 1
        fp_div_vol = pmc.createNode('multiplyDivide',
                                    n='%sdiv_volume_%i' % (fp_name, settings['num']))
        fp_div_vol.operation.set(2)
        fp_div_vol.input1X.set(1)

        # creates a conditionNode for global_cnt enable attr
        fp_cond = pmc.createNode('condition', n='%scond_volume_%i' % (fp_name, settings['num']))
        fp_cond.secondTerm.set(1)

        # connects curve all the nodes
        connect = length.arcLength >> fp_div.input1.input1X
        fp_div.input2.input2X.set(10)
        connect = fp_div.outputX >> fp_div_vol.input2.input2X
        connect = fp_gm_cnt.enable >> fp_cond.firstTerm
        connect = fp_div_vol.outputX >> fp_cond.colorIfTrueR
        fp_cnt_global = fp_gm_cnt.getShape()

        num = 0
        for i in range(0, how_many_flc):
            connect = fp_cond.outColorR >> jnts[num].sy
            connect = fp_cond.outColorR >> jnts[num].sz
            flcs[num].visibility.set(0)
            num += 1

        # hides blendShape, clusters and twist Deformer
        fp_twist[1].visibility.set(0)
        cl_grp.visibility.set(0)
        fp_bshp.visibility.set(0)
        fp_curve.visibility.set(0)

        pmc.select(fp_gm_cnt, r=True)
        return fp_gm_cnt


#----------------------------------------------------------------------------------------------#

def _get_flexiplane_scale(joints=None):
    """
    get the global scale value for flexiPlane by measuring
    the distance between two nodes
    joints must be un parented for function to work properly
    :param joints: the nodes your measuring the distance between
    :return: global scale value for flexi plane
    """
    if len(joints) == 2:
        dd = pmc.distanceDimension(sp=joints[0].translate.get(), ep=joints[1].translate.get())
        inputs = dd.inputs()
        distance = dd.distance.get()
        pmc.delete([dd, inputs])
        return distance * 0.1
    elif len(joints) < 2:
        pmc.displayWarning('not enough joints selected')
        return 'fail'
    else:
        pmc.displayWarning('too many joints selected')
        return 'fail'


#----------------------------------------------------------------------------------------------#

def orient_flexiplane(flex=None, joints=None, up=None):
    """
    scale, translate and rotate a flexiplane between two joints
    :param flex: flexiplane to be oriented
    :param joints: the two joints the flexiplane will placed between, must be un-parented
    :return:flexiplane and joints in a list
    """
    scale = _get_flexiplane_scale(joints)
    flex.scale.set([scale, scale, scale])
    point = pmc.pointConstraint(joints, flex)
    pmc.delete(point)
    up_pos = {
        'x': [1, 0, 0],
        '-x': [-1, 0, 0],
        'y': [0, 1, 0],
        '-y': [0, -1, 0],
        'z': [0, 0, 1],
        '-z': [0, 0, -1]
    }
    if up.lower() not in up_pos:
        pmc.displayWarning('unrecognised value')
        return None

    else:
        return scale, up_pos[up.lower()]


#----------------------------------------------------------------------------------------------#

def select_check(name):
    """
    checks if a node exists by trying to select it
    :param name: name string checking for
    :return: node if it exists, None if it doesn't
    """
    pmc.select(cl=True)
    try:
        pmc.select(name)
    except TypeError:
        pass
    if not pmc.selected():
        pmc.select(cl=True)
        return None
    else:
        ch = pmc.selected()
        pmc.select(cl=True)
        return ch


#----------------------------------------------------------------------------------------------#

def number_check(settings=SETTINGS_DEFAULT):
    """
    checks if numbered node is safe to create
     :param settings: dictionary that holds prefix and node number
     :return: node number that is safe to create
    """
    name = '%s_%scnt_global_1' % (settings['prefix'], fp)

    check = select_check(name)
    number = 1
    while check is not None:
        name = '%s_%scnt_global_%i' % (settings['prefix'], fp, settings['num']+number)
        number += 1
        check = select_check(name)

    return number


#----------------------------------------------------------------------------------------------#

def flexiplane_safe_delete():
    """
    deletes curve info node then flexiplane group node
    :param : global control curve of flexiplane to be deleted
    """
    # filter out nodes that aren't a flexiplane global control
    selection = pmc.selected()
    flex = [f for f in selection if '_flexiPlane_cnt_global' in f.nodeName()]

    # get the flexiplane curve info node
    curve_name = [f.replace('cnt_global', 'curveInfo') for f in flex]

    # delete curve info node
    delete_curve = [pmc.delete(c) for c in curve_name]
    # delete the flexiplane
    delete_flex = [pmc.delete(f.getParent()) for f in flex]
    return flex, curve_name,


#----------------------------------------------------------------------------------------------#

def _py_test(settings=SETTINGS_DEFAULT):

    test_flex = flexiplane(settings)
    #test_sphere = pmc.polySphere(n='test')[0]
    #pmc.select([test_flex], r=True)
    #pmc.select([test_sphere], tgl=True)
    print 'created', test_flex
    test_delete = flexiplane_safe_delete()



    #return scale


if __name__ == '__main__':
    _py_test()