# Copyright (C) 2010 Osipa Entertainment, LLC and/or its licensors.
# All rights reserved.

# Osipa Entertainment, LLC makes no guarantees or warranties related to
# download and/or use of any tools, mel and python scripts and plugins.

# Although Osipa Entertainment provides some tools, mel and python
# scripts and plugins for free, it is prohibited to remove any of the 
# documentation, copyright notices, and/or any references and links
# to Osipa Entertainment, LLC.

import maya.cmds as mc
import sys

#doc Creates the various eye rigs discussed in the 3rd Edition of Stop Staring

class ui():

  def __init__( self, **kwargs ):

    result = mc.promptDialog( title         = kwargs[ 'winTitle' ],
                              message       = 'Add a prefix',
                              button        = [ 'OK','No Prefix' ],
                              defaultButton = 'OK',
                              cancelButton  = 'No Prefix',
                              dismissString = 'No Prefix' )

    if result == 'OK':
      self.prefix = mc.promptDialog( q = 1 )
    else:
      self.prefix = ''

def joints( **kwargs ):

  if 'prefix' in kwargs:
    p = kwargs[ 'prefix' ]
  else:
    p = ''

  sel = mc.ls( sl = True )
  if len( sel ):
    eye = sel[0]
  else:
    eye = mc.spaceLocator( name = p + 'eye' )[0]

  try:
    pos = mc.xform( eye, q=1, ws=1, t=1 )
  except:
    pos = [0,0,0]

  for a in [ 'uprLid', 'lwrLid' ]:
    if not mc.attributeQuery( a, node = eye, exists = True ):
      mc.addAttr( eye, ln = a, at = 'float', k=1, dv=0, min = -10, max = 10 )

  lidRig = mc.group( em = True, name = p + 'lidRig')
  lwrTrk = mc.group( em = True, name = p + 'lwrTrack',  parent = lidRig )  
  lwrLid = mc.group( em = True, name = p + 'lwrLid',    parent = lwrTrk )
  uprLid = mc.group( em = True, name = p + 'uprLid',    parent = lwrLid )
  uprTrk = mc.group( em = True, name = p + 'uprTrack',  parent = lidRig )
  uprRef = mc.group( em = True, name = p + 'uprLidRef', parent = uprTrk )

  mc.xform( lidRig, ws=1, t = pos )

  mc.transformLimits( uprLid, rx=(0,0), erx=(0,1) )

  #Hook up tracking  
  trk = mc.createNode( 'multiplyDivide', name = p + 'trackMD' )
  mc.setAttr( trk + '.input2', 0.9, 0.9, 0.3 )

  mc.setDrivenKeyframe( trk + '.input2X', cd = trk + '.input1X', dv =   0, v = 0.9 )
  mc.setDrivenKeyframe( trk + '.input2X', cd = trk + '.input1X', dv = -30, v = 0.5 )

  mc.connectAttr( eye + '.rotateX', trk + '.input1X' )
  mc.connectAttr( eye + '.rotateX', trk + '.input1Y' )
  mc.connectAttr( eye + '.rotateY', trk + '.input1Z' )

  mc.connectAttr( trk + '.outputX', lwrTrk + '.rotateX' )
  mc.connectAttr( trk + '.outputY', uprTrk + '.rotateX' )
  mc.connectAttr( trk + '.outputZ', uprTrk + '.rotateY' )
  mc.connectAttr( trk + '.outputZ', lwrTrk + '.rotateY' )

  con = mc.orientConstraint( uprRef, lwrLid, uprLid )[0]

  #Upper lid anim
  mc.setDrivenKeyframe( uprRef + '.rx', cd = eye + '.uprLid', dv = -10, v = -30 )
  mc.setDrivenKeyframe( uprRef + '.rx', cd = eye + '.uprLid', dv =   0, v =   0 )
  mc.setDrivenKeyframe( uprRef + '.rx', cd = eye + '.uprLid', dv =  10, v =  30 )

  #Lower lid anim
  mc.setDrivenKeyframe( lwrLid + '.rx', cd = eye + '.lwrLid', dv = -10, v = -30 )
  mc.setDrivenKeyframe( lwrLid + '.rx', cd = eye + '.lwrLid', dv =   0, v =   0 )
  mc.setDrivenKeyframe( lwrLid + '.rx', cd = eye + '.lwrLid', dv =  10, v =  30 )

  #Blink lock
  wal = mc.orientConstraint( con, q=1, weightAliasList = True )
  mc.setDrivenKeyframe( con + '.' + wal[0], cd = eye + '.uprLid', dv =  7, v = 1.0 )
  mc.setDrivenKeyframe( con + '.' + wal[0], cd = eye + '.uprLid', dv = 10, v = 0.0 )
  mc.setDrivenKeyframe( con + '.' + wal[1], cd = eye + '.uprLid', dv =  7, v = 0.0 )
  mc.setDrivenKeyframe( con + '.' + wal[1], cd = eye + '.uprLid', dv = 10, v = 1.0 )

  if len( sel ):
    mc.select( sel )
  else:
    mc.select( clear = True )

def eye( **kwargs ):

  #Creates the eye network and nodes for anim and aim shared input.
  #Places rig at sel[0] if anything is selected.  Can take arguments
  #for prefix (string), and aimVector (list/tuple of len 3)

  if 'prefix' in kwargs:
    p = kwargs[ 'prefix' ]
  else:
    p = ''

  sel = mc.ls( sl = True )
  if len( sel ):
    try:
      pos = mc.xform( sel[0], q=1, ws=1, t=1 )
    except:
      pos = [0,0,0]
  else:
    pos = [0,0,0]

  aim = mc.group( em = True, name = p + 'aim'  )
  anm = mc.group( em = True, name = p + 'anim' )
  out = mc.group( em = True, name = p + 'out'  )
  egp = mc.group( aim, anm, out, name = p + 'eyeDir' )

  for a in [ 'aim', 'anim' ]:
    if not mc.attributeQuery( a, node = out, exists = True ):
      mc.addAttr( out, ln = a, at = 'float', k=1, dv=1 )

  amd = mc.createNode( 'multiplyDivide',   name = '%sMD' % aim )
  nmd = mc.createNode( 'multiplyDivide',   name = '%sMD' % anm )
  pma = mc.createNode( 'plusMinusAverage', name = '%seyeRotSum' % p   )

  mc.connectAttr( aim + '.rotate', amd + '.input1' )
  mc.connectAttr( anm + '.rotate', nmd + '.input1' )

  mc.connectAttr( amd + '.output', pma + '.input3D[0]', force = True )
  mc.connectAttr( nmd + '.output', pma + '.input3D[1]', force = True )
  mc.connectAttr( pma + '.output3D', out + '.rotate'  , force = True )

  [ mc.connectAttr( out + '.aim' , '%s.input2%s' % ( amd, ax ), force = True ) for ax in [ 'X','Y','Z' ] ]
  [ mc.connectAttr( out + '.anim', '%s.input2%s' % ( nmd, ax ), force = True ) for ax in [ 'X','Y','Z' ] ]

  #Handle the aim setup
  if 'aimVector' in kwargs:
    av = kwargs[ 'aimVector' ]
  else:
    av = [0,0,1]
  trg = mc.spaceLocator( name = p + 'aimTarget' )[0]
  mc.xform( trg, ws=1, t=av )
  mc.aimConstraint( trg, aim, aimVector = av, upVector = (0,0,0), worldUpType = 'none' )

  #Place things
  trg = mc.parent( trg, egp )
  mc.xform( egp, ws=1, t=pos )
  trg = mc.parent( trg, world = True )

  mc.select( egp )

def shapes( **kwargs ):

  #Set up a network to control eyelids through animation and eye tracking

  if 'prefix' in kwargs:
    p = kwargs[ 'prefix' ]
  else:
    p = ''

  sel = mc.ls( sl = True )

  if len( sel ):
    ctrl = sel[0]
  else:
    ctrl = mc.spaceLocator( name = p + 'ctrl' )[0]

  #Adding attrs, setting their min, max, and lock
  attrs = [ ( 'uprTrack', -1, 1, 0 ),
            ( 'uprAnim' , -1, 1, 0 ),
            ( 'lwrTrack', -1, 1, 0 ),
            ( 'lwrAnim' , -1, 1, 0 ),
            ( 'uprWork' , -1, 1, 0 ),
            ( 'lwrWork' , -1, 1, 0 ),
            ( 'divider' ,  0, 0, 1 ),
            ( 'uprLidUp',  0, 1, 0 ),
            ( 'uprLidDn',  0, 1, 0 ),
            ( 'lwrLidUp',  0, 1, 0 ),
            ( 'lwrLidDn',  0, 1, 0 ),
            ( 'blink'   ,  0, 1, 0 ) ]

  for a in attrs:
    if not mc.attributeQuery( a[0], node = ctrl, exists = True ):
      mc.addAttr( ctrl, ln = a[0], at = 'float', k=1, min = a[1], max = a[2] )
      mc.setAttr( ctrl + '.' + a[0], l=a[3] )
    else:
      print 'Need to kill only appropriate connections'

  #Store curves
  uu = mc.ls( type = 'animCurveUU' )

  #Drive lower lid shapes with work attr
  mc.setDrivenKeyframe( ctrl + '.lwrLidDn', cd = ctrl + '.lwrWork', dv =  0, v = 0  )
  mc.setDrivenKeyframe( ctrl + '.lwrLidDn', cd = ctrl + '.lwrWork', dv =  1, v = 1  )
  mc.setDrivenKeyframe( ctrl + '.lwrLidUp', cd = ctrl + '.lwrWork', dv =  0, v = 0  )
  mc.setDrivenKeyframe( ctrl + '.lwrLidUp', cd = ctrl + '.lwrWork', dv = -1, v = 1  )

  #Drive upper lid shapes with work attr
  mc.setDrivenKeyframe( ctrl + '.uprLidDn', cd = ctrl + '.uprWork', dv =  0, v = 0  )
  mc.setDrivenKeyframe( ctrl + '.uprLidDn', cd = ctrl + '.uprWork', dv =  1, v = 1  )
  mc.setDrivenKeyframe( ctrl + '.uprLidUp', cd = ctrl + '.uprWork', dv =  0, v = 0  )
  mc.setDrivenKeyframe( ctrl + '.uprLidUp', cd = ctrl + '.uprWork', dv = -1, v = 1  )

  #Weight uprLidDn away from blink's turf
  bws = mc.ls( type = 'blendWeighted' )
  mc.setDrivenKeyframe( ctrl + '.uprLidDn', cd = ctrl + '.lwrWork', dv = 0, v = 0   )
  mc.setDrivenKeyframe( ctrl + '.uprLidDn', cd = ctrl + '.lwrWork', dv = 1, v = 1   )
  bwg( bws )

  #Lower override collision with upper
  mc.setDrivenKeyframe( ctrl + '.uprLidUp', cd = ctrl + '.lwrWork', dv = -.6, v = 0 )
  mc.setDrivenKeyframe( ctrl + '.uprLidUp', cd = ctrl + '.lwrWork', dv =  -1, v = 1 )

  #Drive blink with uprWork, then weight it away from lwrWork 0
  mc.setDrivenKeyframe( ctrl + '.blink', cd = ctrl + '.uprWork', dv = 0, v = 0      )
  mc.setDrivenKeyframe( ctrl + '.blink', cd = ctrl + '.uprWork', dv = 1, v = 1      )

  bws = mc.ls( type = 'blendWeighted' )
  mc.setDrivenKeyframe( ctrl + '.blink', cd = ctrl + '.lwrWork', dv = -1, v = 0     )
  mc.setDrivenKeyframe( ctrl + '.blink', cd = ctrl + '.lwrWork', dv =  0, v = 1     )
  mc.setDrivenKeyframe( ctrl + '.blink', cd = ctrl + '.lwrWork', dv =  1, v = 0     )
  bwg( bws )

  #Hook up lwrLid anim/track
  mc.setDrivenKeyframe( ctrl + '.lwrWork', cd = ctrl + '.lwrAnim', dv = -1, v = -1  )
  mc.setDrivenKeyframe( ctrl + '.lwrWork', cd = ctrl + '.lwrAnim', dv =  1, v =  1  )

  mc.setDrivenKeyframe( ctrl + '.lwrWork', cd = ctrl + '.lwrTrack', dv = -1, v = -1 )
  mc.setDrivenKeyframe( ctrl + '.lwrWork', cd = ctrl + '.lwrTrack', dv =  1, v =  1 )

  #Hook up uprLid anim/track and keep the blink sealed
  mc.setDrivenKeyframe( ctrl + '.uprWork', cd = ctrl + '.uprTrack', dv = -1, v = -1 )
  mc.setDrivenKeyframe( ctrl + '.uprWork', cd = ctrl + '.uprTrack', dv =  1, v =  1 )

  mc.setDrivenKeyframe( ctrl + '.uprWork', cd = ctrl + '.uprAnim', dv = -1, v = -1  )
  mc.setDrivenKeyframe( ctrl + '.uprWork', cd = ctrl + '.uprAnim', dv = .7, v = .7  )
  mc.setDrivenKeyframe( ctrl + '.uprWork', cd = ctrl + '.uprAnim', dv =  1, v =  2  )

  #Set all the new driven keys to have linear tangents
  mc.keyTangent( [ u for u in mc.ls( type = 'animCurveUU' ) if u not in uu ], itt = 'linear', ott = 'linear' )

  mc.select( ctrl )

  return ctrl

def bwg( bws = [] ):

  #Handle the input[1]/weight[0] swap

  bw = [ b for b in mc.ls( type = 'blendWeighted' ) if b not in bws ][0]
  out = mc.listConnections( bw + '.input[1]', plugs = 1 )[0]
  mc.disconnectAttr( out, bw + '.input[1]' )
  mc.connectAttr( out, bw + '.weight[0]', force = True )