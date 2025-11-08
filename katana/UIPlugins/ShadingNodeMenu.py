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

# Don't show these shading nodes.
excludeList = []

excludeCategory = [
    'LaB',
    'LaD'
]

# Add these specific nodes to the primary alt+p shader list.
primaryNodes = [
    'PrmanShadingNode',
    'PxrDisplace'
]

# Node color dictionary.
# Sets the node color per shader category.
colorDict = {
    'Prman'         :[ 0.7, 0.56, 0.0 ],
    'Pxr'           :[ 0.650, 0.250, 0.250 ],
    'Lama'          :[ 0.200, 0.427, 0.714 ],
    'bxdf'          :[ 0.200, 0.427, 0.714 ],
    'color'         :[ 0.086, 0.478, 0.259 ],
    'combine'       :[ 0.599, 0.469, 0.105 ],
    'convert'       :[ 0.478, 0.352, 0.090 ],
    'data'          :[ 0.255, 0.379, 0.427 ],
    'displace'      :[ 0.455, 0.373, 0.675 ],
    'LaB'           :[ 0.157, 0.460, 0.610 ],
    'LaD'           :[ 0.525, 0.365, 0.502 ],
    'LaSh'          :[ 0.675, 0.278, 0.428 ],
    'modify'        :[ 0.246, 0.380, 0.352 ],
    'mutable'       :[ 0.647, 0.325, 0.000 ],
    'osl'           :[ 0.000, 0.000, 0.000 ],
    'pattern'       :[ 0.000, 0.467, 0.510 ],
    'space'         :[ 0.596, 0.357, 0.157 ],
    'string'        :[ 0.605, 0.540, 0.133 ],
    'texture'       :[ 0.667, 0.298, 0.278 ],
    'trace'         :[ 0.000, 0.455, 0.608 ],
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

# Obtain the list of all available shaders.
def get_prman_shaders():
    rendererInfoPlugin = RenderPlugins.GetInfoPlugin('prman')
    shaderType = RenderingAPI.RendererInfo.kRendererObjectTypeShader
    shaderNames = rendererInfoPlugin.getRendererObjectNames(shaderType)

    excludeNodesSet = set(excludeList)
    shaderNames = [shader for shader in shaderNames if shader not in excludeNodesSet]

    return shaderNames

# Pxr shaders.
def get_pxr_shaders():
    prmanShaders = get_prman_shaders()

    pxrShaders = [shader for shader in prmanShaders
                    if shader.startswith('Pxr')
                    or shader == 'aaOceanPrmanShader'
                    or shader == 'OmnidirectionalStereo']

    return pxrShaders

# Primary shaders.
def get_primary_shaders():
    pixarNodesSet = set(get_pxr_shaders())

    primaryShaders = [shader for shader in get_prman_shaders() 
                      if shader not in pixarNodesSet]

    # Remove shaders that start with a value in excludeCategory.
    primaryShaders = [shader for shader in primaryShaders
                      if not any(shader.startswith(group) for group in excludeCategory)]

    primaryShaders.extend(primaryNodes)

    return primaryShaders

# Add menu entry.
def add_shader_to_menu(shaderName, layeredMenu, useColor=True):
    displayName = shaderName

    # Set the node's color based on its shader category.
    displayColor = find_color(shaderName) if useColor else None

    # Add the shader node to the menu.
    layeredMenu.addEntry(shaderName, text=displayName, color=displayColor)

# alt+p shading node list.
def populateCallback_Primary(layeredMenu):
    for shaderName in get_primary_shaders():
        add_shader_to_menu(shaderName, layeredMenu)

    # Add the LaSh macros.
    for nodeName, filename in _RegisteredCustomNodeTypes.items():
        if nodeName.startswith( 'LaSh' ):
            textName = nodeName
            displayColor = find_color( nodeName )
            layeredMenu.addEntry( nodeName, text=textName, color=displayColor )

# alt+r shading node list.
def populateCallback_Pxr(layeredMenu):
    for shaderName in get_pxr_shaders():
        add_shader_to_menu(shaderName, layeredMenu)


def actionCallback( value ):
    """
    Callback for the layered menu, which creates a PrmanShadingNode node and
    sets its B{nodeType} parameter to the given C{value}, which is the name of
    a PRMan shader as set for the menu entry in L{populateCallback_Primary()}.

    @type value: C{str}
    @rtype: C{object}
    @param value: An arbitrary object that the menu entry that was chosen
        represents. In our case here, this is the name of a PRMan shader as
        passed to the L{LayeredMenuAPI.LayeredMenu.addEntry()} function in
        L{populateCallback_Primary()}.
    @return: An arbitrary object. In our case here, we return the created
        PrmanShadingNode node, which is then placed in the B{Node Graph} tab
        because it is a L{NodegraphAPI.Node} instance.
    """

    # root for node creation.
    root = NodegraphAPI.GetRootNode()

    # Initialize the node name to the shaderName value.
    name = value

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

    elif( value.startswith( 'LaSh' )):
        node = NodegraphAPI.CreateNode( value, root )
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
layeredMenu = LayeredMenuAPI.LayeredMenu( populateCallback_Primary, actionCallback, 'Alt+P',
                                            alwaysPopulate = False,
                                            onlyMatchWordStart = False
                                            )
LayeredMenuAPI.RegisterLayeredMenu( layeredMenu, 'Shading Nodes' )

layeredMenuPxr = LayeredMenuAPI.LayeredMenu( populateCallback_Pxr, actionCallback, 'Alt+R',
                                                alwaysPopulate = False,
                                                onlyMatchWordStart = False
                                                )
LayeredMenuAPI.RegisterLayeredMenu( layeredMenuPxr, 'Pxr Nodes' )
