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
import sys

#doc Creates in-scene slider widgets intended for use as facial controls

class ui():

  def __init__( self ):

    self.name  = 'ss3Sliders'

    if mc.window( self.name, exists = True ):
      mc.deleteUI( self.name, window = True )
    self.name = mc.window( self.name )

    n = 10

    mc.columnLayout()
    self.nt = mc.textFieldGrp( label="name", text='controlName', cw=[(1,n*35*.3),(2,n*35*.4)] )
    self.tc = mc.radioCollection()
    mc.rowLayout( numberOfColumns = n-1, cw = [ ( i, 35 ) for i in range( 1, n ) ] )
    rb = [ mc.radioButton( label=chr( i + 96 ) ) for i in range( 1, n ) ]
    mc.radioCollection( self.tc,e=1, select = rb[2] )

    mc.setParent('..')

    mc.button( label="make control", width= n * 33, command = self.doIt )

    mc.showWindow( self.name )

  def doIt( self, *args ):
    x = mc.radioButton( mc.radioCollection( self.tc, q=1, select=1 ), q=1, label=1 )
    makeControl( mc.textFieldGrp( self.nt, q=1, text=1 ), x )


def makeControl( name = '', sType = '' ):

  frm = name + '_frame'
  wgt = name + '_ctrl'

  if mc.objExists( frm ) or mc.objExists( wgt ):
    om.MGlobal.displayError( 'ss3Sliders.go: "' + name + '_ctrl" or "' + name + '_frame" already exists' )
    sys.exit() 

  #text
  text = mc.textCurves( ch=0, f="Arial|h-1|w1|c0", t=name )[0]
  bBox = mc.getAttr( text + '.boundingBoxMax' )[0]

  #frame
  if sType == 'a':
    pnts = [ [.1, 1,0],[-.1, 1,0],[-.1, -1,0],[.1, -1,0],[.1, 1,0] ]
    mc.setAttr( text + '.s', 2/bBox[0], 0.5/bBox[1], 1 )
    mc.setAttr( text + '.t', pnts[4][0] + .15, pnts[4][1], pnts[4][2] )
    mc.setAttr( text + '.rz', -90 )
  else:
    if   sType == 'b': pnts = [ [ 1,.1,0],[ -1,.1,0],[ -1,-.1,0],[ 1,-.1,0],[ 1,.1,0] ]
    elif sType == 'd': pnts = [ [ 1, 1,0],[ -1, 1,0],[ -1,  0,0],[ 1,  0,0],[ 1, 1,0] ]
    elif sType == 'e': pnts = [ [ 1, 0,0],[ -1, 0,0],[ -1, -1,0],[ 1, -1,0],[ 1, 0,0] ]
    elif sType == 'f': pnts = [ [ 1, 1,0],[  0, 1,0],[  0,  0,0],[ 1,  0,0],[ 1, 1,0] ]
    elif sType == 'g': pnts = [ [ 1, 0,0],[  0, 0,0],[  0, -1,0],[ 1, -1,0],[ 1, 0,0] ]
    elif sType == 'h': pnts = [ [ 0, 0,0],[ -1, 0,0],[ -1, -1,0],[ 0, -1,0],[ 0, 0,0] ]
    elif sType == 'i': pnts = [ [ 0, 1,0],[ -1, 1,0],[ -1,  0,0],[ 0,  0,0],[ 0, 1,0] ]
    else:              pnts = [ [ 1, 1,0],[ -1, 1,0],[ -1, -1,0],[ 1, -1,0],[ 1, 1,0] ]

    mc.setAttr( text + '.s', max( .5, pnts[0][0]-pnts[1][0] )/bBox[0], 0.5/bBox[1], 1 )
    mc.setAttr( text + '.t', pnts[1][0], pnts[1][1] + .15, pnts[1][2] )

  qnts = [ [ 10 * int( p[i] ) for i in range(3) ] for p in pnts ]
  pnts = [ [ 10 *      p[i]   for i in range(3) ] for p in pnts ]

  frm = mc.curve( d=1, n=frm, p=pnts )
  mc.setAttr( frm + '.s', 0.1, 0.1, 0.1 )

  #widget
  f = .5
  wgt = mc.curve( d=3, n=wgt, p=[(0,0,0),(0,f,0),(0,0,0),(-f,0,0),(0,0,0),(0,-f,0),(0,0,0),(f,0,0)] )
  mc.closeCurve( wgt, ch=0, ps=0, rpo=1, bb=0.5, bki=0, p=0.1 )
  mc.transformLimits( wgt, etx=(1,1),tx=(qnts[1][0], qnts[0][0]),
                           ety=(1,1),ty=(qnts[2][1], qnts[0][1]),
                           etz=(1,1),tz=(0,0))
  mc.parent( text, wgt, frm )
  [ mc.setAttr( wgt + a, k=0, l=1 ) for a in ['.tz','.rx','.ry','.rz','.sx','.sy','.sz','.v'] ]
  mc.setAttr( wgt + '.v', l=0 )
  frms = mc.listRelatives( frm, children = True, type = 'shape' )[0]
  [ mc.connectAttr( wgt + '.v', t + '.v' ) for t in [frms, text] ]
  [ mc.setAttr( t + a, 1 ) for t in [frms, text] for a in ['.overrideEnabled','.overrideDisplayType']]
  mc.rename( frms, frm + 'Shape' )

  #N/E/S/W
  for x in [ [  qnts[0][1], 'NN', '.ty',  10 ], [ -qnts[2][1], 'SS', '.ty', -10 ],
             [  qnts[0][0], 'EE', '.tx',  10 ], [ -qnts[2][0], 'WW', '.tx', -10 ] ]:
    if x[0]:
      mc.addAttr( frm, ln = x[1], at = 'float', min=0, max=0, k=1 )
      mc.setDrivenKeyframe( frm + '.' + x[1], cd = wgt + x[2], dv = 0,    v = 0 )
      mc.setDrivenKeyframe( frm + '.' + x[1], cd = wgt + x[2], dv = x[3], v = 1 )      

  #NE/SE/SW/NW
  for x in [ [  qnts[0][1],  qnts[0][0], '.NN', 'NE', -10 ], [ -qnts[2][1],  qnts[0][0], '.SS', 'SE', -10 ],
             [  qnts[0][1], -qnts[2][0], '.NN', 'NW',  10 ], [ -qnts[2][1], -qnts[2][0], '.SS', 'SW',  10 ] ]:
    if x[0] and x[1]:
      c = mc.listConnections( frm + x[2] )[0]
      mc.addAttr( frm, ln = x[3], at = 'float', min=0, max=0, k=1 )
      mc.connectAttr( c + '.output', frm + '.' + x[3] )
      ac = mc.ls( type = 'animCurve'     )
      bw = mc.ls( type = 'blendWeighted' )
      mc.setDrivenKeyframe( frm + '.' + x[3], cd = wgt + '.tx', dv = 0,    v = 1 )
      mc.setDrivenKeyframe( frm + '.' + x[3], cd = wgt + '.tx', dv = x[4], v = 0 )    
      bw = [ b for b in mc.ls( type = 'blendWeighted' ) if b not in bw ][0]
      ac = [ a for a in mc.ls( type = 'animCurve'     ) if a not in ac ][0]
      mc.disconnectAttr( ac + '.output', bw + '.input[1]'  )
      mc.connectAttr(    ac + '.output', bw + '.weight[0]' )
      mc.rename( bw, name + '_' + x[3] + '_dkeys' )
      mc.rename( ac, frm  + '_' + x[3] )

  mc.select( frm )