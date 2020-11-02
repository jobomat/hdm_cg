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
import math
import sys

#doc Library scripts for other tools used with Stop Staring, 3rd edition

#v0.2 Jason Osipa 100606 - Added "makeBuffer"
#v0.1 Jason Osipa 100306

def makeBuffer():

  sel = mc.ls( sl = True )

  if len( sel ):
    blnd = mc.ls( sl = True, type = 'blendShape' )
    if len( blnd ):
      blnd = blnd[0]
      wgts = getWeights( blnd, False )
    else:
      blnd = sel[0]
      wgts = mc.listAttr( blnd, ud=True )
      if type( wgts ) != list:
        blnd = getType( 'blendShape' )
        wgts = getWeights( blnd, False )       
  else:
    blnd = getType( 'blendShape' )
    wgts = mc.listAttr( blnd, ud=True )

  bail = False
  if type( wgts ) != list:
    bail = True
  elif len( wgts ) < 1:
    bail = True

  if bail is True:
    om.MGlobal.displayError( "ss3BlendUtls.makeBuffer: Select a blendShape or a node you've added float attributes to" )
    sys.exit()

  net = []
  for n in [ 'final', 'internalA', 'internalB', 'superDirect', 'direct', 'widgets', 'volume' ]:
    net.append( mc.group( em = True, n = blnd + '_' + n ) )
    [ mc.addAttr( net[-1], ln = w, at = 'float', k=1 ) for w in wgts ]

  finl, intA, intB, sdrc, drct, wdgt, vol = net

  bw = []
  for x, y, z, o, n in [ [ sdrc, intB, finl, blnd, '_addB' ],
                         [ drct, wdgt, intA, intB, '_addA' ] ]:
    for w in wgts:
      a = '.' + w
      bw.append( mc.createNode( 'blendWeighted', n = w + n ) )
      mc.connectAttr( x + a, bw[-1] + '.input[0]' )
      mc.connectAttr( y + a, bw[-1] + '.input[1]' )
      mc.connectAttr( bw[-1] + '.output', z + a)
      mc.connectAttr( z + a, o + a, f=1 )
      mc.setAttr( bw[-1] + '.weight[0]', 0.1 )

  for i in range( len( wgts ) ):
    mc.setAttr( vol + '.' + wgts[ i ], 1 )
    mc.connectAttr( vol + '.' + wgts[ i ], bw[ i ] + '.weight[1]' ) 

  prnt = mc.group( drct, sdrc, vol, wdgt, intA, intB, finl, name = blnd + '_buffers' )
  mc.select( prnt )
  return prnt

def turnOff( objects = [] ):

  #doc Sets the envelope attribute to 0 for anything in the history of
  #doc the objects sent in that have that attribute.  Returns a mel
  #doc string that will reset anything affected to what it's settings
  #doc were before running this function.

  out = ''

  lck = []
  key = []
  val = []

  for obj in objects:

    history = mc.listHistory( obj )
    dfm = []

    for h in history:
      if mc.objExists( h + '.envelope' ) == True:
        dfm.append( h )
        lck.append( mc.getAttr( h + '.envelope', l = True ) )
        key.append( mc.getAttr( h + '.envelope', k = True ) )
        val.append( mc.getAttr( h + '.envelope' ) )

    for d in dfm:
      mc.setAttr( d + '.envelope', k = True, l = False )
      mc.setAttr( d + '.envelope', 0 )

    for i in range( len( dfm ) ):
      out = out + ' setAttr -k %d -l %d %s.envelope %.2f;' % ( key[ i ], lck[ i ], dfm[ i ], val[ i ] )

  return out

def cleanDupe( node = '', name = '', envelopeOff = True ):

  #doc Create a duplicate of the node sent in, with no orig nodes left over, set to a custom name,
  #doc and the option to get the duplicate from the pre-deformed source or not

  if name == '':
    name = node + 'Copy'

  if mc.objExists( name ):
    om.MGlobal.displayWarning( 'ss3Utls.cleanDupe : Deleting object of same name for safety : ' + name )
    mc.delete( name )

  evalLater = ''

  if envelopeOff == True:
     evalLater = turnOff( [ node ] )

  dupe = mc.duplicate( node, rc = True )
  deleteList = []

  for d in dupe:
    relatives = mc.listRelatives( d, type = 'shape' )
    if relatives != None:
      for r in relatives:
        if mc.getAttr( r + '.intermediateObject' ) == 1:
          deleteList.append( r )

  xforms = mc.ls( dupe, type = 'transform' )
  deleteList.extend( xforms )
  deleteList = list( set( deleteList ) )
  if dupe[0] in deleteList:
    deleteList.remove( dupe[0] )

  if len( deleteList ):
    mc.delete( deleteList )

  newXForm = mc.rename( dupe[0], name )

  if envelopeOff == True:
    mel.eval( evalLater )

  return newXForm

def getMFnMesh( obj ):

  #doc Returns the MFnMesh for the object sent in

  sel = om.MSelectionList()
  om.MGlobal.getSelectionListByName( obj, sel )
  mesh = om.MDagPath()
  sel.getDagPath( 0, mesh )
  return om.MFnMesh( mesh )

def listLenIf( tester ):

  #doc Confirms valid returns from ls, listHistory

  if type( tester ) is list:
    if len( tester ) > 0:
      return True
    else:
      return False
  else:
    return False

def getType( typeToGet = '', sel = [] ):

  #doc Get the nearest "good" node of the typeToGet

  if len( sel ) < 1:
    sel = mc.ls( sl = True )

  #If anything is selected...
  if listLenIf( sel ):

    #See if it is the right type
    selT = mc.ls( sel, type = typeToGet )
    if listLenIf( selT ):
      #print 'ss3BlendUtls.getType: Found selected:',selT
      return selT[0]

    #Or, see if it has history of the right type
    t = mc.ls( mc.listHistory( sel[0], future = False ), type = typeToGet )
    if listLenIf( t ):
      #print 'ss3BlendUtls.getType: Found in past history:',selT
      return t[0]

    #Or, see if it has future history of the right type
    t = mc.ls( mc.listHistory( sel[0], future = True  ), type = typeToGet )
    if listLenIf( t ):
      #print 'ss3BlendUtls.getType: Found in future history:',selT
      return t[0]

    #Or, see if it has connections of the right type
    t = mc.ls( mc.listConnections( sel[0] ), type = typeToGet )
    if listLenIf( t ):
      #print 'ss3BlendUtls.getType: Found in connetions:',selT
      return t[0]

  #Failing all of that, just grab the first of the right type in the scene
  t = mc.ls( type = typeToGet )
  if listLenIf( t ):
    #print 'ss3BlendUtls.getType: Found generically first of type:',selT
    return t[0]

  #Finally, if there is not a valid return, just throw an error
  om.MGlobal.displayError( 'ss3BlendUtls.getType: No ' + typeToGet + 's found' )
  sys.exit()

def getWeights( blendShape = '', includeEmpties = False ):

  #doc Returns the names (aliases) of blendShape weights on a blendShape

  #varDoc blendShape The blendShape to affect
  #varDoc includeEmpties Include weights without an alias

  i = 0

  weightCount = mc.blendShape( blendShape, query = True, weightCount = True )

  alias = []

  while len( alias ) < weightCount:

    temp = mc.aliasAttr( '%s.weight[%d]' % ( blendShape, i ), query = True )

    if type( temp ) == unicode:
        alias.append( temp )
    elif includeEmpties == True:
        alias.append( '' )

    i = i + 1
    if i > weightCount * 2:
      break

  return alias

def getWeightIndex( blendShape = '', alias = '' ):

  #doc Returns the index of a blendShape weight alias

  #varDoc blendShape The blendShape to look at
  #varDoc alias The alias to look up

  for i in range( mc.blendShape( blendShape, query = True, weightCount = True ) ):
    if mc.aliasAttr( '%s.weight[%d]' % ( blendShape, i ), query = True ) == alias:
      return i

  om.MGlobal.displayError( 'ss3BlendUtls.getWeightIndex: Alias "' + alias + '" not found on ' + blendShape )

def getClosest( leadersIn = [], followersIn = [] ):

  leaders   = mc.ls( leadersIn,   flatten = True )
  followers = mc.ls( followersIn, flatten = True )

  leadersSize   = len( leaders   )
  followersSize = len( followers )

  lPos = [ mc.xform( l, q=1, ws=1, t=1 ) for l in leaders   ]
  fPos = [ mc.xform( f, q=1, ws=1, t=1 ) for f in followers ]

  closest = []
  for l in range( leadersSize ):
    dist = [ [ math.sqrt( sum( [ ( lPos[ l ][ i ] - fPos[ f ][ i ] )**2 for i in range( 3 ) ] ) ), followers[ f ] ] for f in range( followersSize ) ]
    closest.append( min( dist )[1] )

  return closest

def bwSwap():

  for bw in mc.ls( sl = True, type = 'blendWeighted' ):
    try:
      ac = mc.listConnections( bw + '.input[1]' )[0]
      mc.disconnectAttr( ac + '.output', bw + '.input[1]' )
      mc.connectAttr( ac + '.output', bw + '.weight[0]', force = True )
    except:
      pass

def xyz():

  #doc Creates three objects, each the X, Y, and Z portion of the delta
  #doc "target" from "base"

  sel = mc.ls( sl = True )
  if len( sel ) != 2:
    om.MGlobal.displayError( "ss3BlendUtls.xyz: Select a target and base object" )
    sys.exit()
  else:
    targ = sel[0]
    base = sel[1]

  bMesh = getMFnMesh( base )
  tMesh = getMFnMesh( targ )

  bases = om.MPointArray()
  targs = om.MPointArray()
  outpt = om.MPointArray()

  bMesh.getPoints( bases, om.MSpace.kObject )
  tMesh.getPoints( targs, om.MSpace.kObject )

  objs = [ getMFnMesh( mc.duplicate( base, name = a + targ )[0] ) for a in [ 'X_', 'Y_', 'Z_' ] ]

  mainCount = bases.length()

  outpt = om.MPointArray( bases )
  for i in range( mainCount ):
    outpt[ i ].x = targs[ i ][0]
  objs[0].setPoints( outpt, om.MSpace.kObject )

  outpt = om.MPointArray( bases )
  for i in range( mainCount ):
    outpt[ i ].y = targs[ i ][1]
  objs[1].setPoints( outpt, om.MSpace.kObject )

  outpt = om.MPointArray( bases )
  for i in range( mainCount ):
    outpt[ i ].z = targs[ i ][2]
  objs[2].setPoints( outpt, om.MSpace.kObject )