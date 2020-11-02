# Copyright (C) 2010 Osipa Entertainment, LLC and/or its licensors.
# All rights reserved.

# Osipa Entertainment, LLC makes no guarantees or warranties related to
# download and/or use of any tools, mel and python scripts and plugins.

# Although Osipa Entertainment provides some tools, mel and python
# scripts and plugins for free, it is prohibited to remove any of the 
# documentation, copyright notices, and/or any references and links
# to Osipa Entertainment, LLC.

import maya.OpenMaya as om
import maya.cmds as mc
import ss3Utls as utl
import math
import sys

#doc Pins objects to the nearest point on a mesh

def negParent():

  for s in mc.ls( sl = True ):
    try:
      prnt = mc.listRelatives( s, parent = True, fullPath = True )[0]
      md = mc.createNode( 'multiplyDivide', n = s.split('|')[-1] + '_md' )
      mc.connectAttr( s + '.t', md + '.input1' )
      mc.connectAttr( md + '.output', prnt + '.t', force = True )
      mc.setAttr( md + '.input2', -1, -1, -1 )
    except:
      om.MGlobal.displayError( 'ss3Pin.negParent : Problem setting up negative connections with parent for ' + s)
      pass

def pin():

  sel = mc.ls( sl = True )

  if utl.listLenIf( sel ) == False:
    om.MGlobal.displayError( 'ss3Pin.go : Select objects to pin, and a mesh to stick them to' )
    sys.exit()

  if len( sel ) < 2:
    om.MGlobal.displayError( 'ss3Pin.go : Select objects to pin, and a mesh to stick them to' )
    sys.exit()

  mesh = sel.pop( -1 )

  mMesh = utl.getMFnMesh( mesh )

  xp = om.MPoint()
  rt = om.MPoint()
  #pt = om.MScriptUtil(0).asIntPtr()
  ov = om.MIntArray()

  for snap in sel:

    pos = mc.xform( snap, q=1,ws=1,t=1 )
    
    su=om.MScriptUtil(0)
    pt=su.asIntPtr()
    
    ps = om.MPoint( pos[0], pos[1], pos[2], 0.0 )
    mMesh.getClosestPoint( ps, rt, om.MSpace.kWorld, pt )
    #ht = om.MScriptUtil( pt ).asInt()
    ht=su.getInt(pt)

    edges = mc.ls( mc.polyListComponentConversion( '%s.f[%d]' % ( mesh, ht ), fromFace = True, toEdge   = True ), flatten  = True )

    dist = []
    for e in edges:
      ePos = mc.xform( e, q=1,ws=1,t=1 )
      dist.append( [ math.sqrt( sum( [ ( ePos[ i ] - pos[ i ] )**2 for i in range( 3 ) ] ) ), e ] )
    dist.sort()
    edge = dist[0][1]

    mc.select( edge )
    curve = mc.polyToCurve( form = 0, degree = 1, n = edge )

    mopa = mc.createNode( 'motionPath', n = curve[0] + 'mp' )
    mc.connectAttr( curve[1] + '.outputcurve', mopa + '.geometryPath' )
    cvPos = [ mc.xform( '%s.cv[%d]' % ( curve[0], i ), q=1, ws=1, t=1 ) for i in range( 2 ) ]
    mc.delete( curve[0] )

    ptCt = mc.createNode( 'pointConstraint', name = snap.split('|')[-1] + '_ss3Pin', parent = snap )

    mc.connectAttr( mopa + '.allCoordinates', ptCt + '.target[0].targetTranslate' )
    mc.connectAttr( snap + '.rotatePivotTranslate', ptCt + '.constraintRotateTranslate' )
    mc.connectAttr( snap + '.rotatePivot', ptCt + '.constraintRotatePivot' )
    mc.connectAttr( snap + '.parentInverseMatrix[0]', ptCt + '.constraintParentInverseMatrix' )
    mc.connectAttr( ptCt + '.constraintTranslate', snap + '.translate' )

    dist = [math.sqrt(sum([(cvPos[j][i]-pos[i])**2 for i in range(3)])) for j in range(2)]
    if dist[0] > dist[1]:
      mc.setAttr( mopa + '.uValue', 1.0 )

    #Finish up with the offset
    ePos = mc.xform( snap, q=1,ws=1,t=1 )
    diff = [ pos[ i ] - ePos[ i ] for i in range( 3 ) ]
    mc.setAttr( ptCt + '.offset', diff[0], diff[1], diff[2] )