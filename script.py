from __future__ import annotations
from typing import Callable, Generator, Iterator, NamedTuple, Optional
import svg as svglib
import bpy
import bmesh
from mathutils import *

BpyObject = bpy.types.Object

# Representation of a point on the canvas.
class CanvasPoint(NamedTuple):
    x: float
    y: float

    def min(pts: list[CanvasPoint]) -> CanvasPoint:
        return CanvasPoint(
            min(pt.x for pt in pts),
            min(pt.y for pt in pts),
        )

    def max(pts: list[CanvasPoint]) -> CanvasPoint:
        return CanvasPoint(
            max(pt.x for pt in pts),
            max(pt.y for pt in pts),
        )

    def __mul__(self, other):
        if isinstance(other, CanvasPoint):
            return CanvasPoint(self.x * other.x, self.y * other.y)
        elif isinstance(other, int) or isinstance(other, float):
            return CanvasPoint(self.x * other, self.y * other)
        raise NotImplementedError
    
    def __truediv__(self, other):
        if isinstance(other, CanvasPoint):
            return CanvasPoint(self.x / other.x, self.y / other.y)
        elif isinstance(other, int) or isinstance(other, float):
            return CanvasPoint(self.x / other, self.y / other)
        raise NotImplementedError
    
    def __add__(self, other):
        if isinstance(other, CanvasPoint):
            return CanvasPoint(self.x + other.x, self.y + other.y)
        elif isinstance(other, int) or isinstance(other, float):
            return CanvasPoint(self.x + other, self.y + other)
        raise NotImplementedError
    
    def __sub__(self, other):
        return self + other * -1
    
    def __neg__(self):
        return self * -1
    
    def __repr__(self) -> str:
        return f"<{self.x}, {self.y}>"

# Representation of a rectangle on the canvas.
class CanvasRect(NamedTuple):
    min: CanvasPoint
    max: CanvasPoint

    def from_points(points: list[CanvasPoint]) -> CanvasRect:
        return CanvasRect(
            CanvasPoint.min(points),
            CanvasPoint.max(points),
        )
    
    def dims(self) -> CanvasPoint:
        return self.max - self.min

    # Get the rectangle encompassing 2 rectangles.
    def __or__(self, other):
        if isinstance(other, CanvasRect):
            return CanvasRect(
                CanvasPoint.min([self.min, other.min]),
                CanvasPoint.max([self.max, other.max]),
            )
        if isinstance(other, CanvasPoint):
            return CanvasRect(
                CanvasPoint.min([self.min, other]),
                CanvasPoint.max([self.max, other]),
            )
        
        raise NotImplementedError

    # Get the rectangle encompassing many rectangles.
    def union_all(bounds: Iterator[CanvasRect]):
        return CanvasRect(
            CanvasPoint.min([bound.min for bound in bounds]),
            CanvasPoint.max([bound.max for bound in bounds]),
        )

# Parameters for rendering the SVG.
class SvgParams:
    projection_matrix: Matrix = None
    line_width: float = 1
    line_color: str = "red"
    draw_scale: float = 10
    padding: float = 10

    # Convert a 3D point in world space to a point on the canvas.
    def world_to_canvas(self, pos: Vector) -> CanvasPoint:
        proj_pos = pos
        if self.projection_matrix != None:
            proj_pos = self.projection_matrix @ canvas_pos
        canvas_pos = CanvasPoint(proj_pos.x, proj_pos.y)
        
        canvas_pos *= self.draw_scale

        return canvas_pos

# Generator that yields SVG elements and their bounding boxes.
ElemsGen = Generator[tuple[svglib.Element, CanvasRect], None, None]
ToElemsFunc = Callable[
    [BpyObject, SvgParams], 
    ElemsGen
]
def elements_from_mesh_obj(obj: BpyObject, params: SvgParams) -> ElemsGen:
    assert obj.type == "MESH"

    mesh: bpy.types.Mesh = obj.data
    world_mat = obj.matrix_world

    # Create an SVG Line for every edge in the mesh.
    for edge in mesh.edges:
        edge: bpy.types.MeshEdge

        point_positions = [params.world_to_canvas(world_mat @ mesh.vertices[vi].co) for vi in edge.vertices]

        yield (
            svglib.Line(
                x1=point_positions[0].x, y1=point_positions[0].y,
                x2=point_positions[1].x, y2=point_positions[1].y,
                stroke=params.line_color,
                stroke_width=params.line_width,
            ),
            CanvasRect.from_points(point_positions),
        )

# Mappings of object types to the functions to generate SVG elements from them.
obj_to_svg_elem_funcs: dict[str, ToElemsFunc] = {
    "MESH": elements_from_mesh_obj,
}

def scene_to_svg(scene: bpy.types.Scene, params=SvgParams) -> svglib.SVG:
    depsgraph = bpy.context.evaluated_depsgraph_get()

    # Get evaluated versions of all renderable objects.
    eval_objs = (
        obj.evaluated_get(depsgraph)
        for obj in scene.objects
        if not obj.hide_render
    )
    # Filter out objects with no known way to render to SVG.
    render_objs = [
        eval_obj for eval_obj in eval_objs
        if eval_obj.type in obj_to_svg_elem_funcs
    ]

    # Collect an SVG element and its bounds for each object.
    elem_pairs: list[svglib.Element] = list()
    for obj in render_objs:
        to_elems_func = obj_to_svg_elem_funcs.get(obj.type)
        elem_pairs.extend(to_elems_func(obj, params))
    
    canvas_bounds: CanvasRect = CanvasRect.union_all([pair[1] for pair in elem_pairs])
    canvas_dims: CanvasPoint = canvas_bounds.dims()

    # Offset all elements to center them in the canvas.
    offset = -canvas_bounds.min + params.padding
    for elem,bound in elem_pairs:
        if isinstance(elem, svglib.Line):
            elem.x1 += offset.x
            elem.y1 += offset.y
            elem.x2 += offset.x
            elem.y2 += offset.y

    return svglib.SVG(
        width=canvas_dims.x + params.padding * 2,
        height=canvas_dims.y + params.padding * 2,
        elements=[pair[0] for pair in elem_pairs],
    )

if __name__ == '__main__':
    params = SvgParams()

    with open("/Users/me/Desktop/svg_test.svg", "w") as svg_out:
        svg = scene_to_svg(bpy.context.scene, params)
        svg_str = str(svg)
        svg_out.write(svg_str)