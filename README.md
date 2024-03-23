# BlendSVG
BlendSVG is a simple Blender script for generating an SVG from a Blender scene. 
Unlike the [Freestyle SVG Exporter](https://docs.blender.org/manual/en/latest/addons/render/render_freestyle_svg.html) (which is suited for artistic rendering), BlendSVG is meant for <u>laser cutting</u>.

Renders are top-down and orthographic. All mesh edges are rendered regardless of occlusion. Anything that isn't a mesh edge is ignored. Objects will not be rendered if their rendering is disabled.

# Quick Usage
- Install dependencies listed below.
- Put script into Blender's scripting text editor.
- Change the output file path in the `run` function.
- Open the scene you wish to render to SVG.
- Run the script in the text editor.

# Dependencies
- [svg.py](https://pypi.org/project/svg.py/)

Note that packages must be added to Blender's native python installation. On MacOS, this is located at `Blender.app/Contents/Resources/<VERSION>/python/bin/python<VERSION>`.