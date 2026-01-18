"""Export options dialog for SketchBridge."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
)

if TYPE_CHECKING:
    from morphe import SketchDocument

    from ..cad.clients import CADClient


class ExportOptionsDialog(QDialog):
    """Dialog for configuring sketch export options.

    Allows the user to select:
    - Target plane for sketch creation
    - Translation (dx, dy)
    - Rotation angle and center
    """

    def __init__(
        self,
        client: CADClient,
        sketch: SketchDocument,
        parent=None,
    ):
        super().__init__(parent)
        self._client = client
        self._sketch = sketch
        self._planes: list[dict] = []

        self.setWindowTitle(f"Export to {client.name}")
        self.setMinimumWidth(400)

        self._setup_ui()
        self._load_planes()

    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)

        # Sketch info
        info_label = QLabel(f"Sketch: <b>{self._sketch.name}</b>")
        layout.addWidget(info_label)

        # Plane selection
        plane_group = QGroupBox("Target Plane")
        plane_layout = QFormLayout(plane_group)

        self._plane_combo = QComboBox()
        self._plane_combo.addItem("Loading...", None)
        plane_layout.addRow("Plane:", self._plane_combo)

        layout.addWidget(plane_group)

        # Transform options
        transform_group = QGroupBox("Transform")
        transform_layout = QFormLayout(transform_group)

        # Translation
        trans_layout = QHBoxLayout()
        self._dx_spin = QDoubleSpinBox()
        self._dx_spin.setRange(-10000, 10000)
        self._dx_spin.setDecimals(3)
        self._dx_spin.setSuffix(" mm")
        self._dx_spin.setValue(0.0)

        self._dy_spin = QDoubleSpinBox()
        self._dy_spin.setRange(-10000, 10000)
        self._dy_spin.setDecimals(3)
        self._dy_spin.setSuffix(" mm")
        self._dy_spin.setValue(0.0)

        trans_layout.addWidget(QLabel("X:"))
        trans_layout.addWidget(self._dx_spin)
        trans_layout.addWidget(QLabel("Y:"))
        trans_layout.addWidget(self._dy_spin)
        transform_layout.addRow("Translation:", trans_layout)

        # Rotation
        rot_layout = QHBoxLayout()
        self._angle_spin = QDoubleSpinBox()
        self._angle_spin.setRange(-360, 360)
        self._angle_spin.setDecimals(2)
        self._angle_spin.setSuffix(" deg")
        self._angle_spin.setValue(0.0)
        self._angle_spin.valueChanged.connect(self._on_rotation_changed)
        rot_layout.addWidget(self._angle_spin)

        self._centroid_check = QCheckBox("Around centroid")
        self._centroid_check.setChecked(True)
        self._centroid_check.setToolTip(
            "If checked, rotation is around the sketch's centroid.\n"
            "If unchecked, rotation is around the origin (0, 0)."
        )
        rot_layout.addWidget(self._centroid_check)
        transform_layout.addRow("Rotation:", rot_layout)

        # Strip constraints option
        self._strip_constraints_check = QCheckBox("Strip constraints")
        self._strip_constraints_check.setChecked(False)
        self._strip_constraints_check.setToolTip(
            "Remove all constraints from the exported sketch.\n"
            "Recommended when applying rotation, as geometric constraints\n"
            "may conflict with the transform and distort the geometry."
        )
        transform_layout.addRow("", self._strip_constraints_check)

        layout.addWidget(transform_group)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _load_planes(self) -> None:
        """Load available planes from the CAD system."""
        try:
            self._planes = self._client.list_planes()
            self._plane_combo.clear()

            for plane in self._planes:
                display_name = plane.get("name", plane.get("id", "Unknown"))
                plane_type = plane.get("type", "")
                if plane_type:
                    display_name = f"{display_name} ({plane_type})"
                self._plane_combo.addItem(display_name, plane.get("id"))

            # Default to XY plane
            for i in range(self._plane_combo.count()):
                if self._plane_combo.itemData(i) == "XY":
                    self._plane_combo.setCurrentIndex(i)
                    break

        except Exception as e:
            self._plane_combo.clear()
            self._plane_combo.addItem(f"Error loading planes: {e}", None)
            # Add default planes as fallback
            for plane_id, name in [("XY", "XY Plane"), ("XZ", "XZ Plane"), ("YZ", "YZ Plane")]:
                self._plane_combo.addItem(name, plane_id)

    @property
    def selected_plane(self) -> str | None:
        """Get the selected plane ID."""
        return self._plane_combo.currentData()

    @property
    def translation(self) -> tuple[float, float]:
        """Get the translation values (dx, dy)."""
        return (self._dx_spin.value(), self._dy_spin.value())

    @property
    def rotation_angle(self) -> float:
        """Get the rotation angle in degrees."""
        return self._angle_spin.value()

    @property
    def rotate_around_centroid(self) -> bool:
        """Whether to rotate around centroid or origin."""
        return self._centroid_check.isChecked()

    @property
    def strip_constraints(self) -> bool:
        """Whether to strip constraints from the exported sketch."""
        return self._strip_constraints_check.isChecked()

    def _on_rotation_changed(self, value: float) -> None:
        """Handle rotation angle change - suggest stripping constraints."""
        if value != 0.0 and not self._strip_constraints_check.isChecked():
            # Auto-check strip constraints when rotation is applied
            self._strip_constraints_check.setChecked(True)

    def get_transformed_sketch(self) -> SketchDocument:
        """Get the sketch with transform applied.

        Returns:
            New SketchDocument with transforms applied
        """
        from ..transform import transform_sketch

        dx, dy = self.translation
        angle = self.rotation_angle
        strip = self.strip_constraints

        # Apply transform if any values are non-zero or constraints should be stripped
        if dx != 0.0 or dy != 0.0 or angle != 0.0 or strip:
            return transform_sketch(
                self._sketch,
                dx=dx,
                dy=dy,
                angle=angle,
                rotate_around_centroid=self.rotate_around_centroid,
                strip_constraints=strip,
            )
        else:
            return self._sketch
