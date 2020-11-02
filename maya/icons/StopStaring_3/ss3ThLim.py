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
import sys

#doc Sets up a scale limiting relationship for latticed teeth

#v0.1 Jason Osipa 100728

def go ( **kwargs ):

  sel = mc.ls( sl = True )

  if len( sel ) == 2:
    lee = sel[0]
    ler = sel[1]

  else:
    om.MGlobal.displayError( 'ss3ThLim.go : requires two objects' )
    sys.exit()

  #Figure out tthe axis to work in
  axis = 'Y'
  if 'axis' in kwargs:
    if type( kwargs[ 'axis' ] ) == str:
      axt = kwargs[ 'axis' ].upper()
      if axt in [ 'X', 'Y', 'Z' ]:
        axis = axt

  #Get existing connections
  con = mc.listConnections( lee + '.scaleY', scn=1, plugs=1, source=1, destination=0 )

  #Plug in old connections if applicable - if not, make some noise
  if len( con ):

    #Create nodes
    pma = mc.createNode( 'plusMinusAverage' )
    rev = mc.createNode( 'reverse' )
    clm = mc.createNode( 'clamp' )

    #Set limiting attrs
    if   axis == 'X':
      [ mc.transformLimits( x, scaleX=(0,2), enableScaleX=(1,1) ) for x in [ ler, lee ] ]
    elif axis == 'Y':
      [ mc.transformLimits( y, scaleY=(0,2), enableScaleY=(1,1) ) for y in [ ler, lee ] ]
    elif axis == 'Z':
      [ mc.transformLimits( z, scaleZ=(0,2), enableScaleZ=(1,1) ) for z in [ ler, lee ] ]

    mc.setAttr( pma + '.input1D[1]', 1 )

    #Make new Connections
    mc.connectAttr( con[0],            clm + '.inputG',     force=True )
    mc.connectAttr( ler + '.scaleY',   rev + '.inputY',     force=True )
    mc.connectAttr( rev + '.outputY',  pma + '.input1D[0]', force=True )
    mc.connectAttr( pma + '.output1D', clm + '.maxG',       force=True )
    mc.connectAttr( clm + '.outputG',  lee + '.scaleY',     force=True )

  else:
    om.MGlobal.displayError( 'ss3ThLim.go : ' + ler + ' has no existing connections; you don\'t want to run this tool until AFTER you\'ve set up some driven keys' )
    sys.exit()

  #Restore selection
  mc.select( sel )