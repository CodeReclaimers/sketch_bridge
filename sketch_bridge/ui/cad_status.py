"""CAD connection status widget for SketchBridge."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import (
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from ..cad.manager import CADManager, CADSystem


class StatusIndicator(QFrame):
    """A colored indicator showing connection status."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(12, 12)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self._connected = False
        self._update_color()

    def set_connected(self, connected: bool) -> None:
        """Set the connection status."""
        self._connected = connected
        self._update_color()

    def _update_color(self) -> None:
        """Update the indicator color."""
        color = QColor(80, 180, 80) if self._connected else QColor(180, 80, 80)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, color)
        self.setPalette(palette)
        self.setAutoFillBackground(True)


class CADStatusRow(QWidget):
    """Status row for a single CAD system."""

    connect_requested = Signal(object)  # CADSystem
    collect_requested = Signal(object)  # CADSystem
    export_requested = Signal(object)  # CADSystem

    def __init__(self, system: CADSystem, name: str, parent=None):
        super().__init__(parent)
        self._system = system
        self._connected = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)

        # Status indicator
        self._indicator = StatusIndicator()
        layout.addWidget(self._indicator)

        # Name label
        self._name_label = QLabel(name)
        self._name_label.setMinimumWidth(80)
        layout.addWidget(self._name_label)

        # Status text
        self._status_label = QLabel("Disconnected")
        self._status_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(self._status_label, 1)

        # Collect button
        self._collect_btn = QPushButton("Collect")
        self._collect_btn.setEnabled(False)
        self._collect_btn.setToolTip(f"Collect sketches from {name}")
        self._collect_btn.clicked.connect(lambda: self.collect_requested.emit(self._system))
        layout.addWidget(self._collect_btn)

        # Export button
        self._export_btn = QPushButton("Export")
        self._export_btn.setEnabled(False)
        self._export_btn.setToolTip(f"Export selected sketch to {name}")
        self._export_btn.clicked.connect(lambda: self.export_requested.emit(self._system))
        layout.addWidget(self._export_btn)

    def set_connected(self, connected: bool) -> None:
        """Set the connection status."""
        self._connected = connected
        self._indicator.set_connected(connected)
        self._collect_btn.setEnabled(connected)
        # Export button state also depends on having a selected sketch
        # This is managed externally

        if connected:
            self._status_label.setText("Connected")
            self._status_label.setStyleSheet("color: green; font-size: 10px;")
        else:
            self._status_label.setText("Disconnected")
            self._status_label.setStyleSheet("color: gray; font-size: 10px;")

    def set_status_text(self, text: str) -> None:
        """Set custom status text."""
        self._status_label.setText(text)

    def set_export_enabled(self, enabled: bool) -> None:
        """Enable/disable export button."""
        self._export_btn.setEnabled(enabled and self._connected)

    @property
    def system(self) -> CADSystem:
        """Get the CAD system for this row."""
        return self._system


class CADStatusWidget(QWidget):
    """Widget showing connection status for all CAD systems.

    Signals:
        collect_requested(CADSystem): User wants to collect from a CAD system
        export_requested(CADSystem): User wants to export to a CAD system
    """

    collect_requested = Signal(object)  # CADSystem
    export_requested = Signal(object)  # CADSystem

    def __init__(self, cad_manager: CADManager, parent=None):
        super().__init__(parent)
        self._manager = cad_manager
        self._rows: dict[CADSystem, CADStatusRow] = {}

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Set up the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Group box
        group = QGroupBox("CAD Systems")
        group_layout = QVBoxLayout(group)

        # Import here to avoid circular imports
        from ..cad.manager import CAD_NAMES, CADSystem

        # Create a row for each CAD system
        for system in CADSystem:
            name = CAD_NAMES.get(system, str(system))
            row = CADStatusRow(system, name)
            row.collect_requested.connect(self.collect_requested.emit)
            row.export_requested.connect(self.export_requested.emit)
            self._rows[system] = row
            group_layout.addWidget(row)

        group_layout.addStretch()
        layout.addWidget(group)

    def _connect_signals(self) -> None:
        """Connect to CAD manager signals."""
        self._manager.connection_changed.connect(self._on_connection_changed)
        self._manager.status_updated.connect(self._on_status_updated)

    def _on_connection_changed(self, system: CADSystem, connected: bool) -> None:
        """Handle connection status change."""
        if system in self._rows:
            self._rows[system].set_connected(connected)

    def _on_status_updated(self, system: CADSystem, status: dict) -> None:
        """Handle status update."""
        if system not in self._rows:
            return

        row = self._rows[system]

        # Format status text
        parts = []
        if "active_document" in status and status["active_document"]:
            parts.append(status["active_document"])
        if "sketch_count" in status:
            parts.append(f"{status['sketch_count']} sketches")

        if parts:
            row.set_status_text(" | ".join(parts))
        else:
            row.set_status_text("Connected")

    def set_export_enabled(self, enabled: bool) -> None:
        """Enable/disable export buttons for all systems."""
        for row in self._rows.values():
            row.set_export_enabled(enabled)

    def update_status(self) -> None:
        """Update status from the CAD manager."""
        from ..cad.manager import CADSystem

        for system in CADSystem:
            connected = self._manager.is_connected(system)
            status = self._manager.get_status(system)
            self._on_connection_changed(system, connected)
            if status:
                self._on_status_updated(system, status)
