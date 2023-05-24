#
#   Modified from katana plugins/Src/Resources/Examples/UIPlugins/CustomLayeredMenuExample.py
#   Note: in order for this to work properly, you may have to remove/rename that file in the
#   katana distribution so that this one will be used instead.
#
"""
Shading node menus.
Generates a sorted and searchable list of shading nodes in the Node Graph,
and Network Material Create or ShadingGroup nodes.
"""
import os
import re

from Katana import UI4, NodegraphAPI, LayeredMenuAPI, RenderingAPI, DrawingModule, Utils
from RenderingAPI import RenderPlugins
from PyUtilModule.UserNodes import _RegisteredCustomNodeTypes

# A list of shader file names that are available, but that are legacy'd or otherwise
# not good to use, so they are removed from from the popup list of shading nodes.
# This can be used to remove an outdated or buggy shader from the 'Alt+P' list,
# so new instances of it are no longer created even though it is still built
# and functional in existing scenes.
excludeList = []

# Contains a dictionary of shader names, and their custom display name:
#   'shaderName' : 'displayName'
# where 'shaderName' is the name of the built shader file (sans extension),
# and display name is the name that is displayed in the 'Atl+P' menu.
customDict = {}

# Node color dictionary.
# Sets the node color per shader category.
colorDict = {
    'Pxr'           :[ 0.650, 0.250, 0.250 ],
    'Lama'          :[ 0.200, 0.427, 0.714 ],
    'bxdf'          :[ 0.200, 0.427, 0.714 ],
    'color'         :[ 0.086, 0.478, 0.259 ],
    'convert'       :[ 0.478, 0.412, 0.090 ],
    'data'          :[ 0.420, 0.427, 0.255 ],
    'displace'      :[ 0.455, 0.373, 0.675 ],
    'LaD'           :[ 0.525, 0.365, 0.502 ],
    'mutable'       :[ 0.647, 0.325, 0.000 ],
    'osl'           :[ 0.000, 0.000, 0.000 ],
    'pattern'       :[ 0.000, 0.467, 0.510 ],
    'space'         :[ 0.596, 0.357, 0.157 ],
    'string'        :[ 0.605, 0.540, 0.133 ],
    'texture'       :[ 0.667, 0.298, 0.278 ],
    'trace'         :[ 0.000, 0.455, 0.608 ],
    'util'          :[ 0.306, 0.306, 0.306 ],
    'vector'        :[ 0.604, 0.310, 0.569 ],

    'dot_I'         :[ 0.184, 0.486, 0.482 ],
    'dot_F'         :[ 0.247, 0.369, 0.573 ],
    'dot_C'         :[ 0.263, 0.569, 0.318 ],
    'dot_P'         :[ 0.573, 0.455, 0.247 ],
    'dot_N'         :[ 0.567, 0.298, 0.188 ],
    'dot_V'         :[ 0.416, 0.443, 0.588 ],
    'dot_S'         :[ 0.605, 0.540, 0.133 ]
    }

def find_color( shader_name ):
    rgb = colorDict.get( shader_name )
    if rgb:
        return rgb
    else:
        for category in colorDict:
            if shader_name.startswith( category ):
                return colorDict.get( category )
        return None


def populateCallback( layeredMenu ):
    """
    Callback for the layered menu, which adds entries to the given
    C{layeredMenu} based on the available shading nodes.

    @type layeredMenu: L{LayeredMenuAPI.LayeredMenu}
    @param layeredMenu: The layered menu to add entries to.
    """
    # Obtain a list of names of available PRMan shaders from the PRMan renderer info plug-in.
    rendererInfoPlugin = RenderPlugins.GetInfoPlugin( 'prman' )
    shaderType = RenderingAPI.RendererInfo.kRendererObjectTypeShader
    shaderNames = rendererInfoPlugin.getRendererObjectNames( shaderType )

    # Add non-shading node entries.
    layeredMenu.addEntry( 'PrmanShadingNode', text='PrmanShadingNode', color=(1.0, 0.78, 0.0) )

    # Iterate over the names of shaders and add a menu entry for each of them to the given layered menu.
    # Note: Can set the text value to whatever you want the user to see when selecting a shading node.
    for shaderName in shaderNames:
        if( shaderName in excludeList ): continue

        displayName = shaderName

        # Handle custom shader naming.
        if( customDict.get( shaderName )):
            displayName = customDict.get( shaderName )

        # Set the node's color based on its shader category.
        displayColor = find_color( shaderName )
        layeredMenu.addEntry( shaderName, text=displayName, color=displayColor )


def populateCallbackSansPxr( layeredMenu ):
    """
    Callback for the layered menu, which adds entries to the given
    C{layeredMenu} based on the available shading nodes.

    @type layeredMenu: L{LayeredMenuAPI.LayeredMenu}
    @param layeredMenu: The layered menu to add entries to.
    """
    # Obtain a list of names of available PRMan shaders from the PRMan renderer info plug-in.
    rendererInfoPlugin = RenderPlugins.GetInfoPlugin( 'prman' )
    shaderType = RenderingAPI.RendererInfo.kRendererObjectTypeShader
    shaderNames = rendererInfoPlugin.getRendererObjectNames( shaderType )

    # Add non-shading node entries.
    layeredMenu.addEntry( 'PrmanShadingNode', text='PrmanShadingNode', color=(1.0, 0.78, 0.0) )

    # Iterate over the names of shaders and add a menu entry for each of them to the given layered menu.
    # Note: Can set the text value to whatever you want the user to see when selecting a shading node.
    for shaderName in shaderNames:
        if( shaderName in excludeList ): continue

        if( shaderName.startswith( 'Pxr' )
           and not shaderName == 'PxrDisplace'
           or shaderName == 'aaOceanPrmanShader'
           or shaderName == 'OmnidirectionalStereo'
           ): continue

        displayName = shaderName

        # Handle custom shader naming.
        if( customDict.get( shaderName )):
            displayName = customDict.get( shaderName )

        # Set the node's color based on its shader category.
        displayColor = find_color( shaderName )
        layeredMenu.addEntry( shaderName, text=displayName, color=displayColor )


def actionCallback( value ):
    """
    Callback for the layered menu, which creates a PrmanShadingNode node and
    sets its B{nodeType} parameter to the given C{value}, which is the name of
    a PRMan shader as set for the menu entry in L{populateCallback()}.

    @type value: C{str}
    @rtype: C{object}
    @param value: An arbitrary object that the menu entry that was chosen
        represents. In our case here, this is the name of a PRMan shader as
        passed to the L{LayeredMenuAPI.LayeredMenu.addEntry()} function in
        L{populateCallback()}.
    @return: An arbitrary object. In our case here, we return the created
        PrmanShadingNode node, which is then placed in the B{Node Graph} tab
        because it is a L{NodegraphAPI.Node} instance.
    """

    # root for node creation.
    root = NodegraphAPI.GetRootNode()

    # Initialize the node name to the shaderName value.
    name = value

    # Handle custom shader naming.
    if( customDict.get( value )):
        name = customDict.get( value )

    # Init nodes list.
    nodes = list()

    # Handle generation of networks from a selected node.
    if( value.startswith( 'space_2D' )):
        space = NodegraphAPI.CreateNode( 'PrmanShadingNode', root )
        space.getParameter( 'nodeType' ).setValue( 'space_2D', 0 )
        space.setName( 'space_2D' )
        space.getParameter( 'name' ).setValue( space.getName(), 0 )
        nodes.append( space )

        xform = NodegraphAPI.CreateNode( 'PrmanShadingNode', root )
        xform.getParameter( 'nodeType' ).setValue( 'space_2DXform', 0 )
        xform.setName( 'space_2DXform' )
        xform.getParameter( 'name' ).setValue( xform.getName(), 0 )
        nodes.append( xform )

        # Process the above function calls so
        # the nodes' information becomes available.
        Utils.EventModule.ProcessAllEvents()

        # Position the nodes.
        l, b, r, t = DrawingModule.nodeWorld_getBoundsOfListOfNodes([ space ])
        width = r-l
        NodegraphAPI.SetNodePosition( xform, (width+50,0) )

        # Connect their parameters.
        space.getOutputPort( "Out" ).connect( xform.getInputPort( "In" ))
        space.getOutputPort( "OutSize" ).connect( xform.getInputPort( "InSize" ))

    elif( value.startswith( 'space_3D' )):
        space = NodegraphAPI.CreateNode( 'PrmanShadingNode', root )
        space.getParameter( 'nodeType' ).setValue( 'space_3D', 0 )
        space.setName( 'space_3D' )
        space.getParameter( 'name' ).setValue( space.getName(), 0 )
        nodes.append( space )

        xform = NodegraphAPI.CreateNode( 'PrmanShadingNode', root )
        xform.getParameter( 'nodeType' ).setValue( 'space_3DXform', 0 )
        xform.setName( 'space_3DXform' )
        xform.getParameter( 'name' ).setValue( xform.getName(), 0 )
        nodes.append( xform )

        # Process the above function calls so
        # the nodes' information becomes available.
        Utils.EventModule.ProcessAllEvents()

        # Position the nodes.
        l, b, r, t = DrawingModule.nodeWorld_getBoundsOfListOfNodes([ space ])
        width = r-l
        NodegraphAPI.SetNodePosition( xform, (width+50,0) )

        # Connect their parameters.
        space.getOutputPort( "Out" ).connect( xform.getInputPort( "In" ))
        space.getOutputPort( "OutSize" ).connect( xform.getInputPort( "InSize" ))

    elif( value.startswith( 'texture_2D' )):
        space = NodegraphAPI.CreateNode( 'PrmanShadingNode', root )
        space.getParameter( 'nodeType' ).setValue( 'space_2D', 0 )
        space.setName( 'space_2D' )
        space.getParameter( 'name' ).setValue( space.getName(), 0 )
        nodes.append( space )

        xform = NodegraphAPI.CreateNode( 'PrmanShadingNode', root )
        xform.getParameter( 'nodeType' ).setValue( 'space_2DXform', 0 )
        xform.setName( 'space_2DXform' )
        xform.getParameter( 'name' ).setValue( xform.getName(), 0 )
        nodes.append( xform )

        texture = NodegraphAPI.CreateNode( 'PrmanShadingNode', root )
        texture.getParameter( 'nodeType' ).setValue( 'texture_2D', 0 )
        texture.setName( 'texture_2D' )
        texture.getParameter( 'name' ).setValue( texture.getName(), 0 )
        nodes.append( texture )

        # Process the above function calls so
        # the nodes' information becomes available.
        Utils.EventModule.ProcessAllEvents()

        # Position the nodes.
        l, b, r, t = DrawingModule.nodeWorld_getBoundsOfListOfNodes([ space ])
        width = r-l
        NodegraphAPI.SetNodePosition( xform, (width+50,0) )

        l, b, r, t = DrawingModule.nodeWorld_getBoundsOfListOfNodes([ xform ])
        NodegraphAPI.SetNodePosition( texture, (width+50 + r-l+50,0) )

        # Connect their parameters.
        space.getOutputPort( "Out" ).connect( xform.getInputPort( "In" ))
        space.getOutputPort( "OutSize" ).connect( xform.getInputPort( "InSize" ))
        xform.getOutputPort( "Out" ).connect( texture.getInputPort( "Space" ))
        xform.getOutputPort( "OutSize" ).connect( texture.getInputPort( "SpaceSize" ))

    # Create a node containing the chosen type.
    elif( value == 'PrmanShadingNode' ):
        node = NodegraphAPI.CreateNode( 'PrmanShadingNode', root )
        node.getParameter( 'nodeType' ).setValue( '', 0 )
        nodes.append( node )

    elif( value == 'ShadingGroup' ):
        node = NodegraphAPI.CreateNode( 'ShadingGroup', root )
        nodes.append( node )

    elif( value.startswith( 'ShadingGroup_' )):
        nodeTypeName = value.lstrip( 'ShadingGroup_' )
        node = NodegraphAPI.CreateNode( nodeTypeName, root )
        nodes.append( node )

    else:
        node = NodegraphAPI.CreateNode( 'PrmanShadingNode', root )
        node.getParameter( 'nodeType' ).setValue( value, 0 )
        node.setName( name )
        node.getParameter( 'name' ).setValue( node.getName(), 0 )
        nodes.append( node )

    # Set the node color based on its name.
    for node in nodes:
        name = node.getName()
        color = find_color( name )
        if color:
            DrawingModule.SetCustomNodeColor( node, color[0], color[1], color[2] )

    # Update the Node Graph.
    for tab in UI4.App.Tabs.GetTabsByType( 'Node Graph' ):
        tab.update()

    return nodes


# Shading Node Popup Menus.
layeredMenu = LayeredMenuAPI.LayeredMenu( populateCallback, actionCallback, 'Alt+Shift+P',
                                            alwaysPopulate = False,
                                            onlyMatchWordStart = False
                                            )
LayeredMenuAPI.RegisterLayeredMenu( layeredMenu, 'All Shading Nodes' )

layeredMenuSansPxr = LayeredMenuAPI.LayeredMenu( populateCallbackSansPxr, actionCallback, 'Alt+P',
                                                alwaysPopulate = False,
                                                onlyMatchWordStart = False
                                                )
LayeredMenuAPI.RegisterLayeredMenu( layeredMenuSansPxr, 'Shading Nodes' )
