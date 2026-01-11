"""Sketch preview widget using QGraphicsScene."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPen, QWheelEvent
from PySide6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsLineItem,
    QGraphicsPathItem,
    QGraphicsScene,
    QGraphicsView,
)

if TYPE_CHECKING:
    from sketch_canonical import SketchDocument

# Colors for rendering
COLOR_GEOMETRY = QColor(30, 120, 200)  # Blue
COLOR_CONSTRUCTION = QColor(128, 128, 128)  # Gray
COLOR_POINT = QColor(200, 80, 80)  # Red
COLOR_BACKGROUND = QColor(250, 250, 250)  # Light gray
COLOR_GRID = QColor(230, 230, 230)  # Lighter gray

# Line widths (in pixels when using cosmetic pen)
LINE_WIDTH = 1.5
POINT_RADIUS = 3.0


class SketchPreviewWidget(QGraphicsView):
    """Widget for previewing sketch geometry."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create scene
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        # Configure view
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setBackgroundBrush(QBrush(COLOR_BACKGROUND))

        # Enable drag mode for panning
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

        # Current document
        self._document: SketchDocument | None = None

        # Track zoom level
        self._zoom = 1.0

    def load_sketch(self, doc: SketchDocument) -> None:
        """Load a sketch document for preview."""
        self._document = doc
        self._rebuild_scene()
        self.fit_to_view()

    def clear_sketch(self) -> None:
        """Clear the current sketch."""
        self._document = None
        self._scene.clear()

    def _rebuild_scene(self) -> None:
        """Rebuild the scene from the current document."""
        self._scene.clear()

        if self._document is None:
            return

        # Import here to avoid circular imports
        from sketch_canonical.primitives import Arc, Circle, Line, Point, Spline

        # Draw primitives
        for prim in self._document.primitives.values():
            if isinstance(prim, Line):
                self._draw_line(prim)
            elif isinstance(prim, Circle):
                self._draw_circle(prim)
            elif isinstance(prim, Arc):
                self._draw_arc(prim)
            elif isinstance(prim, Point):
                self._draw_point(prim)
            elif isinstance(prim, Spline):
                self._draw_spline(prim)

    def _get_pen(self, construction: bool = False) -> QPen:
        """Get a pen for drawing geometry."""
        color = COLOR_CONSTRUCTION if construction else COLOR_GEOMETRY
        pen = QPen(color)
        pen.setWidthF(LINE_WIDTH)
        pen.setCosmetic(True)  # Width is in pixels, not scene units
        if construction:
            pen.setStyle(Qt.PenStyle.DashLine)
        return pen

    def _draw_line(self, line) -> None:
        """Draw a line primitive."""
        pen = self._get_pen(line.construction)

        # Note: Y is flipped for screen coordinates
        item = QGraphicsLineItem(
            line.start.x, -line.start.y, line.end.x, -line.end.y
        )
        item.setPen(pen)
        item.setData(0, line.id)
        self._scene.addItem(item)

    def _draw_circle(self, circle) -> None:
        """Draw a circle primitive."""
        pen = self._get_pen(circle.construction)

        # QGraphicsEllipseItem takes bounding rect
        x = circle.center.x - circle.radius
        y = -circle.center.y - circle.radius  # Y flipped
        size = circle.radius * 2

        item = QGraphicsEllipseItem(x, y, size, size)
        item.setPen(pen)
        item.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        item.setData(0, circle.id)
        self._scene.addItem(item)

    def _draw_arc(self, arc) -> None:
        """Draw an arc primitive using polyline approximation."""
        from PySide6.QtGui import QPainterPath

        pen = self._get_pen(arc.construction)

        # Draw arc as polyline using the arc's actual geometry
        # This avoids any confusion with Qt's angle conventions
        path = QPainterPath()

        # Number of segments for smooth arc
        num_segments = 50
        sweep = arc.sweep_angle
        start = arc.start_angle
        radius = arc.radius
        cx, cy = arc.center.x, arc.center.y

        # Generate points along the arc
        for i in range(num_segments + 1):
            t = i / num_segments
            angle = start + t * sweep
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)

            # Flip Y for screen coordinates
            screen_y = -y

            if i == 0:
                path.moveTo(x, screen_y)
            else:
                path.lineTo(x, screen_y)

        item = QGraphicsPathItem(path)
        item.setPen(pen)
        item.setData(0, arc.id)
        self._scene.addItem(item)

    def _draw_point(self, point) -> None:
        """Draw a point primitive."""
        pen = QPen(COLOR_POINT)
        pen.setWidthF(1.0)
        brush = QBrush(COLOR_POINT)

        x = point.position.x - POINT_RADIUS
        y = -point.position.y - POINT_RADIUS  # Y flipped
        size = POINT_RADIUS * 2

        item = QGraphicsEllipseItem(x, y, size, size)
        item.setPen(pen)
        item.setBrush(brush)
        item.setData(0, point.id)
        self._scene.addItem(item)

    def _draw_spline(self, spline) -> None:
        """Draw a spline primitive."""
        from PySide6.QtGui import QPainterPath

        pen = self._get_pen(spline.construction)

        if len(spline.control_points) < 2:
            return

        # For now, draw as polyline through evaluated points
        # A proper implementation would use QPainterPath with cubic curves
        path = QPainterPath()

        # Evaluate spline at multiple points
        num_points = max(50, len(spline.control_points) * 10)
        points = self._evaluate_spline(spline, num_points)

        if points:
            path.moveTo(points[0][0], -points[0][1])  # Y flipped
            for x, y in points[1:]:
                path.lineTo(x, -y)  # Y flipped

        item = QGraphicsPathItem(path)
        item.setPen(pen)
        item.setData(0, spline.id)
        self._scene.addItem(item)

    def _evaluate_spline(self, spline, num_points: int) -> list[tuple[float, float]]:
        """Evaluate a spline at multiple parameter values."""
        # Simple B-spline evaluation
        # For a proper implementation, use scipy or a dedicated library
        points = []

        if len(spline.knots) < 2:
            return points

        t_min = spline.knots[spline.degree]
        t_max = spline.knots[-(spline.degree + 1)]

        for i in range(num_points):
            t = t_min + (t_max - t_min) * i / (num_points - 1)
            pt = self._evaluate_bspline_point(spline, t)
            if pt:
                points.append(pt)

        return points

    def _evaluate_bspline_point(
        self, spline, t: float
    ) -> tuple[float, float] | None:
        """Evaluate B-spline at parameter t using de Boor's algorithm."""
        n = len(spline.control_points)
        k = spline.degree + 1
        knots = spline.knots

        if n == 0 or len(knots) < n + k:
            return None

        # Find knot span
        span = k - 1
        for i in range(k - 1, n):
            if knots[i] <= t < knots[i + 1]:
                span = i
                break
        else:
            span = n - 1

        # de Boor's algorithm
        d = []
        for i in range(k):
            idx = span - k + 1 + i
            if 0 <= idx < n:
                cp = spline.control_points[idx]
                d.append([cp.x, cp.y])
            else:
                return None

        for r in range(1, k):
            for j in range(k - 1, r - 1, -1):
                idx = span - k + 1 + j
                denom = knots[idx + k - r] - knots[idx]
                alpha = 0 if abs(denom) < 1e-10 else (t - knots[idx]) / denom
                d[j][0] = (1 - alpha) * d[j - 1][0] + alpha * d[j][0]
                d[j][1] = (1 - alpha) * d[j - 1][1] + alpha * d[j][1]

        return (d[k - 1][0], d[k - 1][1])

    def fit_to_view(self) -> None:
        """Fit the sketch to the view with some padding."""
        if self._scene.itemsBoundingRect().isNull():
            return

        # Add padding
        rect = self._scene.itemsBoundingRect()
        padding = max(rect.width(), rect.height()) * 0.1
        rect.adjust(-padding, -padding, padding, padding)

        self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
        self._zoom = self.transform().m11()

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Handle mouse wheel for zooming."""
        factor = 1.15
        if event.angleDelta().y() < 0:
            factor = 1.0 / factor

        self._zoom *= factor
        self.scale(factor, factor)

    def reset_view(self) -> None:
        """Reset view to default zoom and position."""
        self.resetTransform()
        self._zoom = 1.0
        self.fit_to_view()
