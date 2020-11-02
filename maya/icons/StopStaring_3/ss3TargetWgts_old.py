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
import maya.mel as mel
import ss3Utls as utl
import sys

#doc Offers copying, inversing and tapering functionality paired with Stop Staring, 3rd Edition

#doc To copy weights:    ss3TargetWgts.copyWgtsUI()
#doc To inverse weights: ss3TargetWgts.inverse()
#doc To taper:           ss3TargetWgts.taper()
#doc To bake blends out: ss3TargetWgts.bake()

#v0.1 Jason Osipa, 100306

def copyWeightsPrep():

  #doc Make sure blend weight manipulation will work (without this flooding, it can get confused)

  keepIt = False

  if mc.window( 'toolProperties', q=1, exists = True ):
    keepIt = True

  c =     'ArtPaintBlendShapeWeightsToolOptions;'
  c = c + 'artAttrInitPaintableAttr;'
  c = c + 'artAttrPaintOperation artAttrCtx Add;'
  c = c + 'artAttrCtx -e -value 1e-006 `currentCtx`;'
  c = c + 'artAttrCtx -e -clear `currentCtx`;'
  mel.eval( c )

  try:
    if keepIt == False:
      mc.deleteUI( 'toolProperties' )
  except:
    pass


def copyWeights( obj = '', blendShape = '', copyFrom = 0, copyTo = [] ):

  #doc Copies blendShape painted weights from one shape to another
  #doc All correspondences are done through a weight's index
  
  #varDoc blendShape The blendShape to work with
  #varDoc copyFrom The target weight index to source from
  #varDoc copyTo The target weight index destination(s)

  mc.select( obj )

  copyWeightsPrep()

  blendShapeWeight = utl.getWeights( blendShape, False )

  numWeights = len( blendShapeWeight )

  weightVals = mc.getAttr( blendShape + '.inputTarget[0].inputTargetGroup[%d].targetWeights' % copyFrom )[0]
  size = len( weightVals )

  [ [ mc.setAttr( blendShape + '.inputTarget[0].inputTargetGroup[%d].targetWeights[%d]' % ( c, i ), weightVals[ i ] ) for i in range( size ) ] for c in copyTo ]


def inverse():

  #doc Inverses the weighting of any blendShape sliders set over 0.5

  sel = mc.ls( sl = True )

  blendShape = utl.getType( 'blendShape' )
  print 'Working with blendShape:',blendShape

  toInverse = [ i for i in range( len( utl.getWeights( blendShape, False ) ) ) ]

  mc.select( mc.ls( mc.listHistory( blendShape, future = True ), type = 'shape' )[0] )
  copyWeightsPrep()

  for ti in toInverse:
    if mc.getAttr( blendShape + '.weight[%d]' % ti )  >= 0.5:
      print 'ss3TargetWgts.inverse: Inversing %s.weight[%d]' % ( blendShape, ti )
      weightVals = mc.getAttr( blendShape + '.inputTarget[0].inputTargetGroup[%d].targetWeights' % ti )[0]
      size = len( weightVals )
      [ mc.setAttr(blendShape+'.inputTarget[0].inputTargetGroup[%d].targetWeights[%d]' % ( ti, i ), 1 - weightVals[ i ] ) for i in range( size ) ]
    else:
      print 'ss3TargetWgts.inverse: Skipping %s.weight[%d]' % ( blendShape, ti )

  if utl.listLenIf( sel ):
    mc.select( sel )
  else:
    mc.select( clear = True )


def taper():

  #doc Creates two objects for every blendShape slider over 0.5, one effectively a duplicate,
  #doc the other a version with blendShape weighting inversed

  sel   = mc.ls( sl = True )
  selBS = mc.ls( sel, type = 'blendShape' )

  [ sel.remove( x ) for x in selBS if x in sel ]

  if not utl.listLenIf( sel ):
    om.MGlobal.displayError( 'ss3TargetWgts.taper: Nothing valid selected' )
    sys.exit()

  blendShape = utl.getType( 'blendShape' )
  weights    = utl.getWeights( blendShape, False )
  baseFnMesh = utl.getMFnMesh( sel[0] )
  bases      = om.MPointArray()

  out        = []
  goWeights  = []
  allWeights = []
  warnings   = []
  setValues  = []

  for weight in weights:

    ba = blendShape + '.' + weight
    tv = mc.getAttr( ba )
    allWeights.append( ba )
    setValues.append( tv )

    if tv >= 0.5:
      goWeights.append( weight )

    try:
      mc.setAttr( ba, 0 )
    except:
      warnings.append( weight )

  if len( goWeights ) == 0:
    om.MGlobal.displayError( 'ss3TargetWgts.taper: Set blendShape sliders to 0.5 or more for those shapes to be tapered' )

  else:
    for weight in goWeights:

      mc.setAttr( blendShape + '.' + weight, 1 )

      for side in [ 'L_', 'R_' ]:
    
        targ       = utl.cleanDupe( sel[0], side + weight, True )
        targFnMesh = utl.getMFnMesh( targ )

        baseFnMesh.getPoints( bases, om.MSpace.kObject )
        targFnMesh.setPoints( bases, om.MSpace.kObject )

        out.append( targ )

        mc.select( sel ) #without this, the inverse may bust after the first
        inverse()

      mc.setAttr( blendShape + '.' + weight, 0 )

    aLen = len( allWeights )
    for i in range( aLen ):
      try:
        mc.setAttr( allWeights[ i ], setValues[ i ] )
      except:
        warnings.append( allweights[ i ] )

    warnings = list( set( warnings ) )
    for warn in warnings:
      om.MGlobal.displayWarning( 'ss3TargetWgts.taper: Problem setting weights for ' + warn + '; could mean output shapes are problematic' )

    [ mc.parent( o, world = True ) for o in out if type( mc.listRelatives( o, parent = True ) ) is list ]

  out = [ o for o in out if mc.objExists( o ) ]

  if len( out ):
    mc.select( out )
    return out

def copyWgtsUIGoButton():

  #doc This handles the button in the copWeightsUI

  nameSplit  = mc.window( 'copWgtsWin', q=1, title=1 ).split( ':' )
  obj        = nameSplit[0]
  blendShape = nameSplit[1]
  src = mc.textScrollList( 'copyWgtsUI_src', q=1, selectItem=1 )[0]
  dst = mc.textScrollList( 'copyWgtsUI_dst', q=1, selectItem=1 )

  copyWeights( obj, blendShape, utl.getWeightIndex( blendShape, src ), [ utl.getWeightIndex( blendShape, d ) for d in dst ] )

def copyWgtsUI():

  sel = mc.ls( sl = True )
  if not utl.listLenIf( sel ):
    om.MGlobal.displayError( 'ss3TargetWgts.copyWgtsUI: Nothing selected' )
    sys.exit()

  blendShape = utl.getType( 'blendShape' )
  weights    = utl.getWeights( blendShape )

  win = 'copWgtsWin'

  if mc.window ( win, exists = True ):
    mc.deleteUI( win )
  mc.window( win, title = sel[0] + ':' + blendShape, resizeToFitChildren = True )
  mc.frameLayout( labelVisible = 1, label = sel[0] + ':' + blendShape )
  f = mc.formLayout( numberOfDivisions = 9 )
  stx = mc.text( label = 'copy from', align = 'center' )
  dtx = mc.text( label = 'copy to'  , align = 'center' )
  src = mc.textScrollList( 'copyWgtsUI_src', allowMultiSelection = False )
  dst = mc.textScrollList( 'copyWgtsUI_dst', allowMultiSelection = True  )
  gob = mc.button( label = 'copy weights', command = 'ss3TargetWgts.copyWgtsUIGoButton()' )
  mc.formLayout(     f,
    edit           = True,
    attachPosition = [ ( stx, 'top'   ,0 ,0 ), ( stx, 'left'  ,0 ,0 ) ,
                       ( stx, 'right' ,0 ,4 ), ( stx, 'bottom',0 ,1 ) ,

                       ( dtx, 'top'   ,0 ,0 ), ( dtx, 'left'  ,0 ,5 ) ,
                       ( dtx, 'right' ,0 ,9 ), ( dtx, 'bottom',0 ,1 ) ,

                       ( src, 'top'   ,0 ,1 ), ( src, 'left'  ,0 ,0 ) ,
                       ( src, 'right' ,0 ,4 ), ( src, 'bottom',0 ,8 ) ,

                       ( dst, 'top'   ,0 ,1 ), ( dst, 'left'  ,0 ,5 ) ,
                       ( dst, 'right' ,0 ,9 ), ( dst, 'bottom',0 ,8 ) ,

                       ( gob, 'top'   ,0 ,8 ), ( gob, 'left'  ,0 ,0 ) ,
                       ( gob, 'right' ,0 ,9 ), ( gob, 'bottom',0 ,9 ) ] )

  for w in weights:
    mc.textScrollList( src, e=1, append = w )
    mc.textScrollList( dst, e=1, append = w )

  mc.textScrollList( src, e=1, selectIndexedItem = 1 )
  mc.textScrollList( dst, e=1, selectIndexedItem = 1 )

  mc.showWindow( win )

def bake():

  #doc Bakes out a model copy for every blendShape

  sel   = mc.ls( sl = True )
  selBS = mc.ls( sel, type = 'blendShape' )

  [ sel.remove( x ) for x in selBS if x in sel ]

  if not utl.listLenIf( sel ):
    om.MGlobal.displayError( 'ss3TargetWgts.bake: Nothing valid selected' )
    sys.exit()

  blendShape = utl.getType( 'blendShape' )
  weights    = utl.getWeights( blendShape, False )
  baseFnMesh = utl.getMFnMesh( sel[0] )
  bases      = om.MPointArray()

  out        = []
  allWeights = []
  warnings   = []
  setValues  = []

  for weight in weights:

    ba = blendShape + '.' + weight
    tv = mc.getAttr( ba )
    allWeights.append( ba )
    setValues.append( tv )

    try:
      mc.setAttr( ba, 0 )
    except:
      warnings.append( weight )

  for weight in weights:

    mc.setAttr( blendShape + '.' + weight, 1 )
  
    targ       = utl.cleanDupe( sel[0], weight, True )
    targFnMesh = utl.getMFnMesh( targ )

    baseFnMesh.getPoints( bases, om.MSpace.kObject )
    targFnMesh.setPoints( bases, om.MSpace.kObject )

    out.append( targ )

    mc.setAttr( blendShape + '.' + weight, 0 )

  aLen = len( allWeights )
  for i in range( aLen ):
    try:
      mc.setAttr( allWeights[ i ], setValues[ i ] )
    except:
      warnings.append( allweights[ i ] )

  warnings = list( set( warnings ) )
  for warn in warnings:
    om.MGlobal.displayWarning( 'ss3TargetWgts.bake: Problem setting weights for ' + warn + '; could mean output shapes are problematic' )

  [ mc.parent( o, world = True ) for o in out if type( mc.listRelatives( o, parent = True ) ) is list ]

  out = [ o for o in out if mc.objExists( o ) ]

  if len( out ):
    mc.select( out )
    return out