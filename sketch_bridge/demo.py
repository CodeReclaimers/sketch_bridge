"""
Demo sketch generator for SketchBridge.

This module provides a comprehensive demo sketch that exercises all primitive
types and constraint types supported by the morphe library.

Primitives demonstrated:
    - Line (horizontal, vertical, angled)
    - Arc (clockwise and counter-clockwise)
    - Circle
    - Point (standalone)
    - Spline (B-spline with control points)
    - Ellipse
    - EllipticalArc

Constraints demonstrated:
    - Coincident (points sharing location)
    - Tangent (smooth curve connections)
    - Perpendicular (90° between lines)
    - Parallel (same direction)
    - Concentric (shared center)
    - Equal (same length/radius)
    - Collinear (on same infinite line)
    - Horizontal (parallel to X-axis)
    - Vertical (parallel to Y-axis)
    - Fixed (locked position)
    - Distance (point-to-point)
    - DistanceX (horizontal distance)
    - DistanceY (vertical distance)
    - Length (line segment length)
    - Radius (arc/circle radius)
    - Diameter (arc/circle diameter)
    - Angle (between two lines)
    - Symmetric (about an axis)
    - Midpoint (point at line center)
"""

from __future__ import annotations

import math

from morphe import SketchDocument
from morphe.constraints import (
    Angle,
    Coincident,
    Concentric,
    Diameter,
    Distance,
    DistanceX,
    DistanceY,
    Equal,
    Horizontal,
    Length,
    MidpointConstraint,
    Parallel,
    Perpendicular,
    Radius,
    Symmetric,
    Tangent,
    Vertical,
)
from morphe.primitives import (
    Arc,
    Circle,
    Ellipse,
    EllipticalArc,
    Line,
    Point,
    Spline,
)
from morphe.types import Point2D, PointRef, PointType


def create_demo_sketch() -> SketchDocument:
    """
    Create a comprehensive demo sketch showcasing all supported features.

    The sketch is organized into several regions:
    - Left side: Rectangle with perpendicular/parallel constraints
    - Center: Circles and arcs with tangent/concentric constraints
    - Right side: Lines at various angles with angle constraints
    - Top: Spline curve
    - Bottom: Ellipse and elliptical arc

    Returns:
        A SketchDocument containing the demo sketch.
    """
    doc = SketchDocument(name="SketchBridge Demo")

    # =========================================================================
    # Region 1: Rectangle with constraints (left side)
    # Demonstrates: Line, Horizontal, Vertical, Length, Coincident
    # =========================================================================

    # Create a rectangle from four lines
    rect_bottom = Line(
        start=Point2D(0, 0),
        end=Point2D(40, 0),
    )
    rect_right = Line(
        start=Point2D(40, 0),
        end=Point2D(40, 25),
    )
    rect_top = Line(
        start=Point2D(40, 25),
        end=Point2D(0, 25),
    )
    rect_left = Line(
        start=Point2D(0, 25),
        end=Point2D(0, 0),
    )

    # Add primitives and get their IDs
    id_rect_bottom = doc.add_primitive(rect_bottom)
    id_rect_right = doc.add_primitive(rect_right)
    id_rect_top = doc.add_primitive(rect_top)
    id_rect_left = doc.add_primitive(rect_left)

    # Add rectangle constraints
    doc.add_constraint(Horizontal(id_rect_bottom, id="H1"))
    doc.add_constraint(Horizontal(id_rect_top, id="H2"))
    doc.add_constraint(Vertical(id_rect_left, id="V1"))
    doc.add_constraint(Vertical(id_rect_right, id="V2"))

    # Coincident corners
    doc.add_constraint(Coincident(
        PointRef(id_rect_bottom, PointType.END),
        PointRef(id_rect_right, PointType.START),
        id="C1"
    ))
    doc.add_constraint(Coincident(
        PointRef(id_rect_right, PointType.END),
        PointRef(id_rect_top, PointType.START),
        id="C2"
    ))
    doc.add_constraint(Coincident(
        PointRef(id_rect_top, PointType.END),
        PointRef(id_rect_left, PointType.START),
        id="C3"
    ))
    doc.add_constraint(Coincident(
        PointRef(id_rect_left, PointType.END),
        PointRef(id_rect_bottom, PointType.START),
        id="C4"
    ))

    # Dimensional constraints
    doc.add_constraint(Length(id_rect_bottom, 40.0, id="LEN1"))
    doc.add_constraint(Length(id_rect_left, 25.0, id="LEN2"))

    # =========================================================================
    # Region 2: Circles and arcs (center)
    # Demonstrates: Circle, Arc, Concentric, Tangent, Radius, Diameter
    # =========================================================================

    # Main circle
    main_circle = Circle(
        center=Point2D(70, 12.5),
        radius=12,
    )
    id_main_circle = doc.add_primitive(main_circle)

    # Concentric inner circle
    inner_circle = Circle(
        center=Point2D(70, 12.5),
        radius=6,
    )
    id_inner_circle = doc.add_primitive(inner_circle)

    # Concentric constraint
    doc.add_constraint(Concentric(id_main_circle, id_inner_circle, id="CON1"))

    # Diameter constraint on main circle
    doc.add_constraint(Diameter(id_main_circle, 24.0, id="DIA1"))

    # Radius constraint on inner circle
    doc.add_constraint(Radius(id_inner_circle, 6.0, id="RAD1"))

    # Arc tangent to main circle (CCW arc on the right)
    arc_tangent = Arc(
        center=Point2D(95, 12.5),
        start_point=Point2D(82, 12.5),
        end_point=Point2D(95, 25.5),
        ccw=True,
    )
    id_arc_tangent = doc.add_primitive(arc_tangent)

    # Tangent constraint
    doc.add_constraint(Tangent(id_main_circle, id_arc_tangent, id="TAN1"))

    # Radius on the arc
    doc.add_constraint(Radius(id_arc_tangent, 13.0, id="RAD2"))

    # Small clockwise arc (demonstrates CW direction)
    arc_cw = Arc(
        center=Point2D(70, 12.5),
        start_point=Point2D(67, 4),
        end_point=Point2D(73, 4),
        ccw=False,
    )
    doc.add_primitive(arc_cw)  # Demonstrates CW arc direction

    # =========================================================================
    # Region 3: Angular lines (right side)
    # Demonstrates: Angle, Distance, DistanceX, DistanceY
    # =========================================================================

    # Angled line 1 (30 degrees from horizontal)
    angle_rad = math.radians(30)
    line_angled1 = Line(
        start=Point2D(110, 0),
        end=Point2D(110 + 25 * math.cos(angle_rad), 25 * math.sin(angle_rad)),
    )
    id_line_angled1 = doc.add_primitive(line_angled1)

    # Angled line 2 (60 degrees from line 1, so 90 from horizontal)
    angle_rad2 = math.radians(90)
    line_angled2 = Line(
        start=Point2D(110, 0),
        end=Point2D(110 + 20 * math.cos(angle_rad2), 20 * math.sin(angle_rad2)),
    )
    id_line_angled2 = doc.add_primitive(line_angled2)

    # Coincident at the start
    doc.add_constraint(Coincident(
        PointRef(id_line_angled1, PointType.START),
        PointRef(id_line_angled2, PointType.START),
        id="C5"
    ))

    # Angle constraint (60 degrees between the lines)
    doc.add_constraint(Angle(id_line_angled1, id_line_angled2, 60.0, id="ANG1"))

    # Distance constraints
    doc.add_constraint(Distance(
        PointRef(id_line_angled1, PointType.START),
        PointRef(id_line_angled1, PointType.END),
        25.0,
        id="DIST1"
    ))

    # DistanceX from rectangle to angle lines
    doc.add_constraint(DistanceX(
        PointRef(id_rect_bottom, PointType.END),
        70.0,
        PointRef(id_line_angled1, PointType.START),
        id="DX1"
    ))

    # DistanceY (vertical offset)
    doc.add_constraint(DistanceY(
        PointRef(id_rect_bottom, PointType.START),
        0.0,
        PointRef(id_line_angled1, PointType.START),
        id="DY1"
    ))

    # =========================================================================
    # Region 4: Spline curve (top)
    # Demonstrates: Spline with control points
    # =========================================================================

    spline_control_points = [
        Point2D(0, 40),
        Point2D(20, 55),
        Point2D(50, 35),
        Point2D(80, 50),
        Point2D(110, 40),
        Point2D(135, 45),
    ]

    spline = Spline.create_uniform_bspline(
        control_points=spline_control_points,
        degree=3,
    )
    doc.add_primitive(spline)  # Demonstrates B-spline

    # =========================================================================
    # Region 5: Ellipse and elliptical arc (bottom)
    # Demonstrates: Ellipse, EllipticalArc
    # =========================================================================

    # Full ellipse (rotated 15 degrees)
    ellipse = Ellipse(
        center=Point2D(30, -25),
        major_radius=18,
        minor_radius=10,
        rotation=math.radians(15),
    )
    doc.add_primitive(ellipse)  # Demonstrates rotated ellipse

    # Elliptical arc
    elliptical_arc = EllipticalArc(
        center=Point2D(85, -25),
        major_radius=15,
        minor_radius=8,
        rotation=math.radians(-10),
        start_param=math.radians(30),
        end_param=math.radians(240),
        ccw=True,
    )
    doc.add_primitive(elliptical_arc)  # Demonstrates elliptical arc

    # =========================================================================
    # Region 6: Construction geometry and symmetry (center-left)
    # Demonstrates: construction=True, Symmetric, Midpoint, Fixed, Point
    # =========================================================================

    # Construction line (symmetry axis)
    symmetry_axis = Line(
        start=Point2D(20, -5),
        end=Point2D(20, -45),
        construction=True,
    )
    id_symmetry_axis = doc.add_primitive(symmetry_axis)

    # Vertical constraint on symmetry axis
    doc.add_constraint(Vertical(id_symmetry_axis, id="V3"))

    # Two symmetric points
    point_left = Point(position=Point2D(5, -15))
    point_right = Point(position=Point2D(35, -15))
    id_point_left = doc.add_primitive(point_left)
    id_point_right = doc.add_primitive(point_right)

    # Symmetric constraint
    doc.add_constraint(Symmetric(
        PointRef(id_point_left, PointType.CENTER),
        PointRef(id_point_right, PointType.CENTER),
        id_symmetry_axis,
        id="SYM1"
    ))

    # Another point at the midpoint of a line
    # First create a line for the midpoint constraint
    midpoint_line = Line(
        start=Point2D(55, -15),
        end=Point2D(75, -15),
    )
    id_midpoint_line = doc.add_primitive(midpoint_line)

    midpoint_point = Point(position=Point2D(65, -15))
    id_midpoint_point = doc.add_primitive(midpoint_point)

    # Midpoint constraint
    doc.add_constraint(MidpointConstraint(
        PointRef(id_midpoint_point, PointType.CENTER),
        id_midpoint_line,
        id="MID1"
    ))

    # Horizontal constraint on the midpoint line
    doc.add_constraint(Horizontal(id_midpoint_line, id="H3"))

    # Length constraint on midpoint line
    doc.add_constraint(Length(id_midpoint_line, 20.0, id="LEN3"))

    # =========================================================================
    # Region 7: Parallel, Perpendicular, Equal (bottom right)
    # Demonstrates these constraints without redundancy using diagonal lines
    # =========================================================================

    # Two parallel diagonal lines
    diag_line1 = Line(
        start=Point2D(100, -20),
        end=Point2D(120, -35),
    )
    diag_line2 = Line(
        start=Point2D(100, -30),
        end=Point2D(120, -45),
    )
    id_diag1 = doc.add_primitive(diag_line1)
    id_diag2 = doc.add_primitive(diag_line2)

    # Parallel constraint (not redundant - lines are diagonal)
    doc.add_constraint(Parallel(id_diag1, id_diag2, id="PAR1"))

    # Equal length constraint (not redundant - no length constraints on these lines)
    doc.add_constraint(Equal(id_diag1, id_diag2, id="EQ1"))

    # Two perpendicular lines (forming an L shape)
    perp_line1 = Line(
        start=Point2D(130, -20),
        end=Point2D(145, -35),
    )
    perp_line2 = Line(
        start=Point2D(145, -35),
        end=Point2D(130, -50),
    )
    id_perp1 = doc.add_primitive(perp_line1)
    id_perp2 = doc.add_primitive(perp_line2)

    # Coincident at the corner
    doc.add_constraint(Coincident(
        PointRef(id_perp1, PointType.END),
        PointRef(id_perp2, PointType.START),
        id="C6"
    ))

    # Perpendicular constraint (not redundant - lines are diagonal)
    doc.add_constraint(Perpendicular(id_perp1, id_perp2, id="PERP1"))

    return doc


def get_demo_sketch_info() -> dict:
    """
    Get information about the demo sketch contents.

    Returns:
        Dictionary with counts of primitives and constraints by type.
    """
    doc = create_demo_sketch()

    primitive_counts = {}
    for prim in doc.primitives.values():
        ptype = type(prim).__name__
        primitive_counts[ptype] = primitive_counts.get(ptype, 0) + 1

    constraint_counts = {}
    for const in doc.constraints:
        ctype = const.constraint_type.value
        constraint_counts[ctype] = constraint_counts.get(ctype, 0) + 1

    return {
        "name": doc.name,
        "primitive_counts": primitive_counts,
        "constraint_counts": constraint_counts,
        "total_primitives": len(doc.primitives),
        "total_constraints": len(doc.constraints),
    }


if __name__ == "__main__":
    # Print demo sketch information
    info = get_demo_sketch_info()
    print(f"Demo Sketch: {info['name']}")
    print(f"\nPrimitives ({info['total_primitives']} total):")
    for ptype, count in sorted(info['primitive_counts'].items()):
        print(f"  {ptype}: {count}")
    print(f"\nConstraints ({info['total_constraints']} total):")
    for ctype, count in sorted(info['constraint_counts'].items()):
        print(f"  {ctype}: {count}")
