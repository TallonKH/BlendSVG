# BlendSVG
BlendSVG is a simple Blender script for generating an SVG from a Blender scene. 
Unlike the [Freestyle SVG Exporter](https://docs.blender.org/manual/en/latest/addons/render/render_freestyle_svg.html) (which is suited for artistic rendering), BlendSVG is meant for <u>laser cutting</u>.

Renders are top-down and orthographic. All mesh edges are rendered regardless of occlusion. Anything that isn't a mesh edge is ignored.