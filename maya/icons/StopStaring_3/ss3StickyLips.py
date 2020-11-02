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

#doc A few tools to automate the process of creating "sticky lips"

#v0.2 Jason Osipa 101105 - minor updates to button command handling
#v0.1 Jason Osipa 100728

class ui():

  def __init__( self ):

    self.name  = 'ss3StickyLips'
    self.verts = []
    self.zips  = []
    self.red   = [0.8, 0.5, 0.5]
    self.green = [0.5, 0.8, 0.5]
    self.blue  = [0.5, 0.8, 1.0]
    self.vOK   = False
    self.sOK   = False

    if mc.window( self.name, exists = True ):
      mc.deleteUI( self.name, window = True )
    self.name = mc.window( self.name )

    mc.columnLayout()
    mc.frameLayout( label = 'Setup' )
    mc.columnLayout()
    self.mb = mc.button( label = 'Make Stickers', width = 200, command = self.makeStickers )
    self.vb = mc.button( label = 'Load Verts', width = 200, command = self.setVerts )
    self.zb = mc.button( label = 'Load Stickers', width = 200, command = self.setZips )
    self.lb = mc.button( label = 'Link Verts to Stickers', width = 200, bgc = self.red, enable = False, command = self.connect )
    mc.setParent('..')
    mc.setParent('..')
    mc.frameLayout( label = 'Helpers' )
    mc.columnLayout()
    self.pb = mc.button( label = 'Prep .pnts', width = 200, command = prepShape )
    self.db = mc.button( label = 'Default Zips', width = 200, command = defaultZips )
    mc.showWindow( self.name )

  def makeStickers( self, *args ):
    loft = utl.getType( 'nurbsSurface' )
    self.zips = buildStickers( loft )
    mc.button( self.zb, edit = True, bgc = self.green )
    self.sOK = True

  def setVerts( self, *args ):

    col = self.red[:]
    self.vOK = False
    sel = mc.ls( sl = True, flatten = True, type = 'float3' )

    if len( sel ):
      sel = [ s for s in sel if s.split( '.' )[1][:3] == 'vtx' ]
      if len( sel ):
        self.verts = sel
        col = self.green[:]
        self.vOK = True
    mc.button( self.vb, edit = True, bgc = col )
    self.connectActivate()

  def setZips( self, *args ):

    col = self.red[:]
    self.sOK = False
    sel = mc.ls( sl = True, type = 'transform' )
    if len( sel ):
      sel = [ s for s in sel if mc.attributeQuery( 'stickyPos', exists = True, node = s ) ]
      if len( sel ):
        self.zips = mc.ls( sl = True, flatten = True )
        col = self.green[:]
        self.sOK = True
    mc.button( self.zb, edit = True, bgc = col )
    self.connectActivate()

  def connectActivate( self ):
    if self.vOK and self.sOK:
      mc.button( self.lb, edit = True, enable = True, bgc = self.blue )
    else:
      mc.button( self.lb, edit = True, enable = False, bgc = self.red )

  def connect( self, *args ):
    linkZip( self.verts, self.zips )

def linkZip( verts = [], viz = [] ):

  closest = utl.getClosest( verts, viz )
  obj = verts[0].split( '.' )[0]

  [ mc.connectAttr( closest[ i ] + '.stickyPos', obj + '.pnts[%s]' % verts[ i ].split( '[' )[1][:-1], force = True ) for i in range( len( verts ) ) ]

def defaultZips( args = None ):

  sel = mc.ls( sl = True )

  if len( sel ):

    sel = sel[0]
    zips = [ a for a in mc.listAttr( sel, ud=True ) if a[:6] == 'sticky' ]
    zips.remove( 'stickyControl' )

    zLen = len( zips )

    if len( zips ):

      #Store curves
      uu = mc.ls( type = 'animCurveUU' )

      size = zLen / 2 + zLen % 2
      t = 10 / float( size )
      for i in range( size ):
        x = float( i * t )
        for z in list( set( [ zips[ i ], zips[ -( i + 1 ) ] ] ) ):
          mc.setDrivenKeyframe( sel + '.' + z, cd = sel + '.stickyControl', dv = x, v = 0 )
          mc.setDrivenKeyframe( sel + '.' + z, cd = sel + '.stickyControl', dv = t + x, v = 1.05 )

      #Set all the new driven keys to have flat tangents
      mc.keyTangent( [ u for u in mc.ls( type = 'animCurveUU' ) if u not in uu ], itt = 'flat', ott = 'flat' )

def prepShape( args = None ):

  mesh = utl.getType( 'mesh' )

  for i in range( len( mc.ls( mesh + '.vtx[*]', flatten = True ) ) ):
    try:
      mc.setAttr( mesh + '.pnts[%d]' % i, 0, 0, 0 )
    except:
      pass

  om.MGlobal.displayWarning( mesh + '.pnts attribute is now ready for connections' )

def buildStickers( loft = '' ):

  if not mc.attributeQuery( 'stickyControl', node = loft, exists = True ):
    mc.addAttr( loft, ln = 'stickyControl', at = 'float', k = 1 )

  span = mc.getAttr( loft + '.spansU' )

  viz = []

  for i in range( span + 1 ):

    u = float( i ) / span

    if not mc.attributeQuery( 'sticky%d' % i, node = loft, exists = True ):
      mc.addAttr( loft, ln = 'sticky%d' % i, at = 'float', k = 1, dv = 1 )

    n    = 1
    posi = []

    for s in [ 'A', 'B' ]:

      n = 1 - n
      posi.append( mc.createNode( 'pointOnSurfaceInfo', name = 'stickyPOSI_%d%s' % ( i, s ) ) )
      mc.connectAttr( loft + '.worldSpace[0]', posi[-1] + '.inputSurface' )
      mc.setAttr( posi[-1] + '.turnOnPercentage', 1 )
      mc.setAttr( posi[-1] + '.parameterU', u   )
      mc.setAttr( posi[-1] + '.parameterV', n )

      loc = mc.spaceLocator( name = 'sticker_%d%s' % ( i, s ) )[0]
      mc.connectAttr( posi[-1] + '.position', loc + '.t' )
      mc.addAttr( loc, ln = 'stickyPos', at = 'compound', numberOfChildren = 3, k = 1 )
      [ mc.addAttr( loc, ln = 'stickyPos' + a, at = 'float', parent = 'stickyPos', k = 1 ) for a in ['X','Y','Z'] ]
      viz.append( loc )

    pc = mc.createNode( 'pointConstraint', name = 'stickyPC_%d' % i, parent = viz[-2] )
    md = mc.createNode( 'multiplyDivide', name = 'stickyMD_%d' % i )

    mc.setAttr( md + '.input2', -1, -1, -1 )

    mc.connectAttr( posi[0] + '.position', pc + '.target[1].targetTranslate'  )
    mc.connectAttr( posi[0] + '.position', pc + '.constraintRotateTranslate'  )
    mc.connectAttr( posi[1] + '.position', pc + '.target[0].targetTranslate'  )
    mc.connectAttr( loft    + '.sticky%d' % i, pc + '.target[0].targetWeight' )
    mc.connectAttr( pc      + '.constraintTranslate', viz[-2] + '.stickyPos'  )
    mc.connectAttr( pc      + '.constraintTranslate', md + '.input1'  )
    mc.connectAttr( md      + '.output', viz[-1] + '.stickyPos'  )

  mc.group( viz, name = 'stickers' )

  return viz