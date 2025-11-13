# Installation

## Requirements
* `make`
* `python3`
* [Pixar's RenderMan](https://renderman.pixar.com) is used in the examples
and by the `make` system to compile the [`osl`](../osl/) shaders.
* Foundry's [Katana](https://www.foundry.com/products/katana) and its
associated [RenderMan Bridge Application](https://renderman.pixar.com/bridge-tools)
are required to make use of the [LaSh Material](doc/README.md#the-lash-material) functionality packaged for use in Katana,
as well as the [Example](doc/README.md#examples) Katana [`project`](./katana/project/) files.

Other rendering and application systems can still make use of the core [`osl`](../osl/) shading nodes and `make` system to assemble the necessary functionality to implement the LaSh system in those environments.

## Quick Start
To use the supplied repository content as is:

1. Set up RenderMan:

    1. [Install RenderManProServer](https://renderman.pixar.com/store) and ensure it is functioning properly.

    1. Optionally install [Katana](https://www.foundry.com/products/katana) and [RenderMan for Katana](https://renderman.pixar.com/bridge-tools) and ensure they are functioning properly.
     While optional, this step is highly recommended, as the core LaSh functionality is packaged into Katana [ShadingGroup](https://learn.foundry.com/katana/Content/ug/adding_assigning_materials/using_the_shadinggroup_node.html) macros.
     If another [RenderMan Bridge Application](https://renderman.pixar.com/bridge-tools) is used, you'll have to implement their functionality yourself using the individual [`osl`](../osl/) and [Lama](https://rmanwiki.pixar.com/display/REN/MaterialX+Lama) shading nodes.

1. Set these environment variables appropriately. These are required by the [make](https://www.gnu.org/software/make/manual/) system that's used to compile and install the shaders:
    * PIXAR_ROOT
    * RMAN_VERSION

    For example, if your version of RenderManProServer is installed in
    `/opt/pixar/RenderManProServer-26.0`, then using `bash` shell:

    ```bash
    export PIXAR_ROOT="/opt/pixar"
    export RMAN_VERSION="26.0"
    ```
    
    Since RenderManProServer requires an RMANTREE environment variable to be set to its installation location, you can conveniently use these to define it as well:
    
    ```bash
    export RMANTREE="${PIXAR_ROOT}/RenderManProServer-${RMAN_VERSION}"
    ```

1. Download or [clone](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) this repository.
1. `cd` into the dowloaded or cloned repository's directory.

1. At this point, you can use the `make` or `make all` command (they are equivalent) to build the shaders.
You can also `cd osl` into the osl directory and `make` the shaders there.
The osl Makefile will only make shaders for .osl files that are more recent than their complied shader.
In this way, you can edit a source file and execute `make` from within the osl directory and only the updated source file(s) will be built.

    `make clean` and `make help` can also be executed from either the top-level directory or the osl directory.
`make clean` removes the built shaders, and `make help` provides additional information about the make system and how it's controlled.

1. Set these environment variables appropriately.
    1. This is required so the built shaders can be found by [RenderMan](https://rmanwiki.pixar.com/display/REN) and a [RenderMan Bridge Application](https://renderman.pixar.com/bridge-tools):

        - RMAN_SHADERPATH

        For example, if you downloaded or cloned this repository to `${HOME}/LaSh`, then using `bash` shell:

        ```bash
        export RMAN_SHADERPATH="${HOME}/LaSh/build/${RMAN_VERSION}/shaders:${RMAN_SHADERPATH}"
        ```

    1. If you're using [Katana](https://www.foundry.com/products/katana) and you want to make use of the supplied
    [LaSh Nodes](doc/README.md#lash-nodes) and the Katana **alt+p** and **alt+r** Shading Node Menus:

        ```bash
        export KATANA_RESOURCES="${HOME}/LaSh/build/katana:${KATANA_RESOURCES}"
        ```
        so that katana will load them and the custom shading node menus when it starts.
        The **alt+p** menu lists all the (primary) shaders built from this repository and the **alt+r** menu shows the (RenderMan) Pixar-supplied shaders.
