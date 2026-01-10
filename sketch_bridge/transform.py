"""Transform utilities for SketchDocument."""

from __future__ import annotations

import copy
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sketch_canonical import SketchDocument
    from sketch_canonical.types import Point2D


def transform_point(
    point: Point2D,
    dx: float = 0.0,
    dy: float = 0.0,
    angle: float = 0.0,
    center_x: float = 0.0,
    center_y: float = 0.0,
) -> Point2D:
    """Transform a single point.

    Args:
        point: The point to transform
        dx: Translation in X (mm)
        dy: Translation in Y (mm)
        angle: Rotation angle (degrees, counter-clockwise)
        center_x: X coordinate of rotation center
        center_y: Y coordinate of rotation center

    Returns:
        New transformed Point2D
    """
    from sketch_canonical.types import Point2D as Point2DClass

    x, y = point.x, point.y

    # Apply rotation around center
    if angle != 0.0:
        angle_rad = math.radians(angle)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        # Translate to origin, rotate, translate back
        x_rel = x - center_x
        y_rel = y - center_y

        x = x_rel * cos_a - y_rel * sin_a + center_x
        y = x_rel * sin_a + y_rel * cos_a + center_y

    # Apply translation
    x += dx
    y += dy

    return Point2DClass(x, y)


def get_sketch_centroid(doc: SketchDocument) -> tuple[float, float]:
    """Calculate the centroid of all geometry in a sketch.

    Args:
        doc: The SketchDocument

    Returns:
        Tuple of (center_x, center_y)
    """
    from sketch_canonical.primitives import Arc, Circle, Line, Point, Spline

    points = []

    for prim in doc.primitives.values():
        if isinstance(prim, Line):
            points.append((prim.start.x, prim.start.y))
            points.append((prim.end.x, prim.end.y))
        elif isinstance(prim, Circle):
            points.append((prim.center.x, prim.center.y))
        elif isinstance(prim, Arc):
            points.append((prim.center.x, prim.center.y))
            points.append((prim.start_point.x, prim.start_point.y))
            points.append((prim.end_point.x, prim.end_point.y))
        elif isinstance(prim, Point):
            points.append((prim.position.x, prim.position.y))
        elif isinstance(prim, Spline):
            for cp in prim.control_points:
                points.append((cp.x, cp.y))

    if not points:
        return (0.0, 0.0)

    cx = sum(p[0] for p in points) / len(points)
    cy = sum(p[1] for p in points) / len(points)

    return (cx, cy)


def get_sketch_bounds(doc: SketchDocument) -> tuple[float, float, float, float]:
    """Get the bounding box of a sketch.

    Args:
        doc: The SketchDocument

    Returns:
        Tuple of (min_x, min_y, max_x, max_y)
    """
    from sketch_canonical.primitives import Arc, Circle, Line, Point, Spline

    points = []

    for prim in doc.primitives.values():
        if isinstance(prim, Line):
            points.append((prim.start.x, prim.start.y))
            points.append((prim.end.x, prim.end.y))
        elif isinstance(prim, Circle):
            # Include circle bounds
            cx, cy, r = prim.center.x, prim.center.y, prim.radius
            points.append((cx - r, cy - r))
            points.append((cx + r, cy + r))
        elif isinstance(prim, Arc):
            # Simplified: use center and endpoints
            points.append((prim.center.x, prim.center.y))
            points.append((prim.start_point.x, prim.start_point.y))
            points.append((prim.end_point.x, prim.end_point.y))
        elif isinstance(prim, Point):
            points.append((prim.position.x, prim.position.y))
        elif isinstance(prim, Spline):
            for cp in prim.control_points:
                points.append((cp.x, cp.y))

    if not points:
        return (0.0, 0.0, 0.0, 0.0)

    min_x = min(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_x = max(p[0] for p in points)
    max_y = max(p[1] for p in points)

    return (min_x, min_y, max_x, max_y)


def transform_sketch(
    doc: SketchDocument,
    dx: float = 0.0,
    dy: float = 0.0,
    angle: float = 0.0,
    rotate_around_centroid: bool = True,
    strip_constraints: bool = False,
) -> SketchDocument:
    """Transform a sketch document.

    Creates a deep copy and applies translation and rotation to all primitives.

    Args:
        doc: The SketchDocument to transform
        dx: Translation in X (mm)
        dy: Translation in Y (mm)
        angle: Rotation angle (degrees, counter-clockwise)
        rotate_around_centroid: If True, rotate around sketch centroid.
                               If False, rotate around origin.
        strip_constraints: If True, remove all constraints from the transformed
                          sketch. This is recommended when applying rotation,
                          as geometric constraints may conflict with the transform
                          and cause the CAD solver to distort the geometry.

    Returns:
        New transformed SketchDocument
    """
    from sketch_canonical.primitives import Arc, Circle, Line, Point, Spline

    # Deep copy the document
    new_doc = copy.deepcopy(doc)

    # Optionally strip constraints to prevent solver conflicts
    if strip_constraints:
        new_doc.constraints = []

    # Get rotation center
    if rotate_around_centroid and angle != 0.0:
        center_x, center_y = get_sketch_centroid(doc)
    else:
        center_x, center_y = 0.0, 0.0

    # Transform each primitive
    for prim in new_doc.primitives.values():
        if isinstance(prim, Line):
            prim.start = transform_point(
                prim.start, dx, dy, angle, center_x, center_y
            )
            prim.end = transform_point(
                prim.end, dx, dy, angle, center_x, center_y
            )

        elif isinstance(prim, Circle):
            prim.center = transform_point(
                prim.center, dx, dy, angle, center_x, center_y
            )
            # Radius stays the same

        elif isinstance(prim, Arc):
            prim.center = transform_point(
                prim.center, dx, dy, angle, center_x, center_y
            )
            prim.start_point = transform_point(
                prim.start_point, dx, dy, angle, center_x, center_y
            )
            prim.end_point = transform_point(
                prim.end_point, dx, dy, angle, center_x, center_y
            )
            # Radius and direction stay the same

        elif isinstance(prim, Point):
            prim.position = transform_point(
                prim.position, dx, dy, angle, center_x, center_y
            )

        elif isinstance(prim, Spline):
            new_control_points = []
            for cp in prim.control_points:
                new_cp = transform_point(cp, dx, dy, angle, center_x, center_y)
                new_control_points.append(new_cp)
            prim.control_points = new_control_points

    return new_doc


def translate_sketch(
    doc: SketchDocument, dx: float, dy: float
) -> SketchDocument:
    """Translate a sketch document.

    Args:
        doc: The SketchDocument to translate
        dx: Translation in X (mm)
        dy: Translation in Y (mm)

    Returns:
        New translated SketchDocument
    """
    return transform_sketch(doc, dx=dx, dy=dy, angle=0.0)


def rotate_sketch(
    doc: SketchDocument, angle: float, around_centroid: bool = True
) -> SketchDocument:
    """Rotate a sketch document.

    Args:
        doc: The SketchDocument to rotate
        angle: Rotation angle (degrees, counter-clockwise)
        around_centroid: If True, rotate around sketch centroid.
                        If False, rotate around origin.

    Returns:
        New rotated SketchDocument
    """
    return transform_sketch(
        doc, dx=0.0, dy=0.0, angle=angle, rotate_around_centroid=around_centroid
    )
