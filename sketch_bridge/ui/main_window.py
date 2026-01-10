"""Main window for SketchBridge."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from ..cad.manager import CADManager, CADSystem
from .cad_status import CADStatusWidget
from .export_dialog import ExportOptionsDialog
from .preview import SketchPreviewWidget
from .sketch_list import SketchListWidget
from .sketch_selection_dialog import SketchSelectionDialog

if TYPE_CHECKING:
    from sketch_canonical import SketchDocument


class MainWindow(QMainWindow):
    """Main application window for SketchBridge."""

    def __init__(self):
        super().__init__()

        self._sketches: dict[str, SketchDocument] = {}
        self._sketch_counter = 0

        # Create CAD manager
        self._cad_manager = CADManager(self)

        self._setup_ui()
        self._connect_signals()

        # Start monitoring CAD connections
        self._cad_manager.start_monitoring()

    def _setup_ui(self) -> None:
        """Set up the main window UI."""
        self.setWindowTitle("SketchBridge")
        self.setMinimumSize(1000, 600)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)

        # Main layout
        main_layout = QVBoxLayout(central)

        # Create splitter for main content
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel: Sketch list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        sketch_group = QGroupBox("Sketches")
        sketch_layout = QVBoxLayout(sketch_group)
        self._sketch_list = SketchListWidget()
        sketch_layout.addWidget(self._sketch_list)
        left_layout.addWidget(sketch_group)

        splitter.addWidget(left_panel)

        # Center panel: Preview
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(0, 0, 0, 0)

        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)

        self._preview = SketchPreviewWidget()
        preview_layout.addWidget(self._preview)

        # Preview info bar
        self._preview_info = QLabel("No sketch selected")
        self._preview_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(self._preview_info)

        center_layout.addWidget(preview_group)

        splitter.addWidget(center_panel)

        # Right panel: CAD status
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self._cad_status = CADStatusWidget(self._cad_manager)
        right_layout.addWidget(self._cad_status)

        splitter.addWidget(right_panel)

        # Set splitter sizes
        splitter.setSizes([200, 500, 250])

        main_layout.addWidget(splitter, 1)

        # Bottom button bar
        button_layout = QHBoxLayout()

        self._load_btn = QPushButton("Load File...")
        self._load_btn.clicked.connect(self._on_load_file)
        button_layout.addWidget(self._load_btn)

        self._save_btn = QPushButton("Save File...")
        self._save_btn.setEnabled(False)
        self._save_btn.clicked.connect(self._on_save_file)
        button_layout.addWidget(self._save_btn)

        button_layout.addStretch()

        self._fit_view_btn = QPushButton("Fit View")
        self._fit_view_btn.clicked.connect(self._preview.fit_to_view)
        button_layout.addWidget(self._fit_view_btn)

        main_layout.addLayout(button_layout)

        # Status bar
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_bar.showMessage("Ready")

    def _connect_signals(self) -> None:
        """Connect widget signals."""
        # Sketch list signals
        self._sketch_list.sketch_selected.connect(self._on_sketch_selected)
        self._sketch_list.sketch_removed.connect(self._on_sketch_removed)

        # CAD status signals
        self._cad_status.collect_requested.connect(self._on_collect_requested)
        self._cad_status.export_requested.connect(self._on_export_requested)

    def _on_sketch_selected(self, key: str) -> None:
        """Handle sketch selection."""
        doc = self._sketch_list.get_sketch(key)
        if doc:
            self._preview.load_sketch(doc)
            self._update_preview_info(doc)
            self._save_btn.setEnabled(True)
            self._cad_status.set_export_enabled(True)
        else:
            self._preview.clear_sketch()
            self._preview_info.setText("No sketch selected")
            self._save_btn.setEnabled(False)
            self._cad_status.set_export_enabled(False)

    def _on_sketch_removed(self, key: str) -> None:
        """Handle sketch removal."""
        if key in self._sketches:
            del self._sketches[key]

        # Check if we still have a selection
        if not self._sketch_list.get_selected_key():
            self._preview.clear_sketch()
            self._preview_info.setText("No sketch selected")
            self._save_btn.setEnabled(False)
            self._cad_status.set_export_enabled(False)

    def _update_preview_info(self, doc: SketchDocument) -> None:
        """Update the preview info label."""
        prim_count = len(doc.primitives)
        const_count = len(doc.constraints)
        info = f"{doc.name} | {prim_count} primitives | {const_count} constraints"

        if doc.solver_status:
            info += f" | {doc.solver_status.name}"
            if doc.degrees_of_freedom is not None:
                info += f" (DOF: {doc.degrees_of_freedom})"

        self._preview_info.setText(info)

    def _on_load_file(self) -> None:
        """Handle load file button."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Sketch",
            "",
            "JSON Files (*.json);;All Files (*)",
        )

        if not file_path:
            return

        try:
            self._load_sketch_from_file(Path(file_path))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load sketch:\n{e}")

    def _load_sketch_from_file(self, path: Path) -> None:
        """Load a sketch from a JSON file."""
        from sketch_canonical import sketch_from_json

        with open(path) as f:
            json_str = f.read()

        doc = sketch_from_json(json_str)

        # Generate unique key
        self._sketch_counter += 1
        key = f"file_{self._sketch_counter}_{doc.name}"

        self._sketches[key] = doc
        self._sketch_list.add_sketch(key, doc, source="File")
        self._sketch_list.select_sketch(key)

        self._status_bar.showMessage(f"Loaded: {path.name}")

    def _on_save_file(self) -> None:
        """Handle save file button."""
        doc = self._sketch_list.get_selected_sketch()
        if not doc:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Sketch",
            f"{doc.name}.json",
            "JSON Files (*.json);;All Files (*)",
        )

        if not file_path:
            return

        try:
            self._save_sketch_to_file(doc, Path(file_path))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save sketch:\n{e}")

    def _save_sketch_to_file(self, doc: SketchDocument, path: Path) -> None:
        """Save a sketch to a JSON file."""
        from sketch_canonical import sketch_to_json

        json_str = sketch_to_json(doc)

        with open(path, "w") as f:
            f.write(json_str)

        self._status_bar.showMessage(f"Saved: {path.name}")

    def _on_collect_requested(self, system: CADSystem) -> None:
        """Handle collect from CAD request."""
        system_name = self._cad_manager.get_system_name(system)

        try:
            sketches = self._cad_manager.list_sketches(system)

            if not sketches:
                QMessageBox.information(
                    self,
                    "No Sketches",
                    f"No sketches found in {system_name}.",
                )
                return

            # If only one sketch, collect it directly
            # If multiple, show selection dialog
            if len(sketches) == 1:
                sketches_to_collect = sketches
            else:
                dialog = SketchSelectionDialog(sketches, system_name, self)
                if dialog.exec() != QDialog.DialogCode.Accepted:
                    return
                sketches_to_collect = dialog.get_selected_sketches()

                if not sketches_to_collect:
                    self._status_bar.showMessage("No sketches selected")
                    return

            # Collect selected sketches
            collected = 0
            for sketch_info in sketches_to_collect:
                sketch_name = sketch_info.get("name", "Unknown")
                doc = self._cad_manager.export_sketch(system, sketch_name)

                if doc:
                    self._sketch_counter += 1
                    key = f"{system.name.lower()}_{self._sketch_counter}_{doc.name}"
                    self._sketches[key] = doc
                    self._sketch_list.add_sketch(key, doc, source=system_name)
                    collected += 1

            if collected > 0:
                self._status_bar.showMessage(
                    f"Collected {collected} sketch(es) from {system_name}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Collection Failed",
                    f"Could not collect sketches from {system_name}.",
                )

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to collect from {system_name}:\n{e}"
            )

    def _on_export_requested(self, system: CADSystem) -> None:
        """Handle export to CAD request."""
        doc = self._sketch_list.get_selected_sketch()
        if not doc:
            QMessageBox.warning(
                self, "No Selection", "Please select a sketch to export."
            )
            return

        system_name = self._cad_manager.get_system_name(system)
        client = self._cad_manager.get_client(system)

        # Show export options dialog
        dialog = ExportOptionsDialog(client, doc, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        try:
            # Get the transformed sketch and export options
            transformed_doc = dialog.get_transformed_sketch()
            plane = dialog.selected_plane

            created_name = self._cad_manager.import_sketch(
                system, transformed_doc, plane=plane
            )

            if created_name:
                self._status_bar.showMessage(
                    f"Exported '{doc.name}' to {system_name} as '{created_name}'"
                )
                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"Sketch exported to {system_name} as '{created_name}'.",
                )
            else:
                QMessageBox.warning(
                    self,
                    "Export Failed",
                    f"Could not export sketch to {system_name}.",
                )

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to export to {system_name}:\n{e}"
            )

    def closeEvent(self, event) -> None:
        """Handle window close."""
        self._cad_manager.stop_monitoring()
        super().closeEvent(event)
