"""Sketch selection dialog for importing from CAD systems."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class SketchSelectionDialog(QDialog):
    """Dialog for selecting which sketches to import from a CAD system.

    Shows a list of available sketches with checkboxes, allowing the user
    to choose which ones to collect.
    """

    def __init__(
        self,
        sketches: list[dict],
        cad_name: str,
        parent=None,
    ):
        """Initialize the dialog.

        Args:
            sketches: List of sketch info dicts from CAD system.
                      Each dict should have 'name', 'label', 'geometry_count',
                      'constraint_count' keys.
            cad_name: Display name of the CAD system (e.g., "FreeCAD")
            parent: Parent widget
        """
        super().__init__(parent)
        self._sketches = sketches
        self._cad_name = cad_name
        self._checkboxes: list[QCheckBox] = []

        self.setWindowTitle(f"Select Sketches from {cad_name}")
        self.setMinimumWidth(450)
        self.setMinimumHeight(300)

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel(
            f"Found <b>{len(self._sketches)}</b> sketch(es) in {self._cad_name}.\n"
            "Select the sketches you want to import:"
        )
        header.setWordWrap(True)
        layout.addWidget(header)

        # Selection buttons
        button_row = QHBoxLayout()

        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self._select_all)
        button_row.addWidget(select_all_btn)

        select_none_btn = QPushButton("Select None")
        select_none_btn.clicked.connect(self._select_none)
        button_row.addWidget(select_none_btn)

        button_row.addStretch()
        layout.addLayout(button_row)

        # Scrollable area for sketch list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(4, 4, 4, 4)

        # Create checkbox for each sketch
        for sketch_info in self._sketches:
            checkbox = self._create_sketch_checkbox(sketch_info)
            self._checkboxes.append(checkbox)
            scroll_layout.addWidget(checkbox)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll, 1)

        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Start with all selected
        self._select_all()

    def _create_sketch_checkbox(self, sketch_info: dict) -> QCheckBox:
        """Create a checkbox widget for a sketch.

        Args:
            sketch_info: Dict with sketch information

        Returns:
            QCheckBox configured for the sketch
        """
        name = sketch_info.get("name", "Unknown")
        label = sketch_info.get("label", name)
        geo_count = sketch_info.get("geometry_count", 0)
        const_count = sketch_info.get("constraint_count", 0)

        # Build display text
        display = f"{label} ({name})" if label != name else name
        display += f"  —  {geo_count} geometries, {const_count} constraints"

        checkbox = QCheckBox(display)
        checkbox.setProperty("sketch_name", name)
        return checkbox

    def _select_all(self) -> None:
        """Select all sketches."""
        for checkbox in self._checkboxes:
            checkbox.setChecked(True)

    def _select_none(self) -> None:
        """Deselect all sketches."""
        for checkbox in self._checkboxes:
            checkbox.setChecked(False)

    def get_selected_sketches(self) -> list[dict]:
        """Get the list of selected sketch info dicts.

        Returns:
            List of sketch info dicts for selected sketches
        """
        selected = []
        for checkbox, sketch_info in zip(self._checkboxes, self._sketches, strict=True):
            if checkbox.isChecked():
                selected.append(sketch_info)
        return selected

    def get_selected_names(self) -> list[str]:
        """Get the names of selected sketches.

        Returns:
            List of sketch names that were selected
        """
        return [s.get("name", "") for s in self.get_selected_sketches()]
