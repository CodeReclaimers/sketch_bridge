"""Sketch list widget for SketchBridge."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from sketch_canonical import SketchDocument


class SketchListWidget(QWidget):
    """Widget for displaying and managing loaded sketches.

    Signals:
        sketch_selected(str): Emitted when a sketch is selected (sketch key)
        sketch_removed(str): Emitted when user requests sketch removal
    """

    sketch_selected = Signal(str)
    sketch_removed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._sketches: dict[str, SketchDocument] = {}
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Sketch list
        self._list = QListWidget()
        self._list.setAlternatingRowColors(True)
        self._list.currentItemChanged.connect(self._on_selection_changed)
        layout.addWidget(self._list)

        # Buttons
        button_layout = QHBoxLayout()

        self._remove_btn = QPushButton("Remove")
        self._remove_btn.setEnabled(False)
        self._remove_btn.clicked.connect(self._on_remove_clicked)
        button_layout.addWidget(self._remove_btn)

        self._clear_btn = QPushButton("Clear All")
        self._clear_btn.setEnabled(False)
        self._clear_btn.clicked.connect(self._on_clear_clicked)
        button_layout.addWidget(self._clear_btn)

        layout.addLayout(button_layout)

    def add_sketch(self, key: str, doc: SketchDocument, source: str = "") -> None:
        """Add a sketch to the list.

        Args:
            key: Unique key for the sketch
            doc: The SketchDocument
            source: Source description (e.g., "File", "FreeCAD")
        """
        self._sketches[key] = doc

        # Create list item
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, key)

        # Format display text
        prim_count = len(doc.primitives)
        const_count = len(doc.constraints)
        display_text = f"{doc.name}"
        if source:
            display_text = f"[{source}] {display_text}"
        item.setText(display_text)
        item.setToolTip(
            f"Name: {doc.name}\n"
            f"Primitives: {prim_count}\n"
            f"Constraints: {const_count}"
        )

        self._list.addItem(item)
        self._update_buttons()

    def remove_sketch(self, key: str) -> None:
        """Remove a sketch from the list."""
        if key not in self._sketches:
            return

        del self._sketches[key]

        # Find and remove list item
        for i in range(self._list.count()):
            item = self._list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == key:
                self._list.takeItem(i)
                break

        self._update_buttons()

    def clear(self) -> None:
        """Clear all sketches."""
        self._sketches.clear()
        self._list.clear()
        self._update_buttons()

    def get_sketch(self, key: str) -> SketchDocument | None:
        """Get a sketch by key."""
        return self._sketches.get(key)

    def get_all_sketches(self) -> dict[str, SketchDocument]:
        """Get all sketches."""
        return self._sketches.copy()

    def get_selected_key(self) -> str | None:
        """Get the currently selected sketch key."""
        item = self._list.currentItem()
        if item:
            return item.data(Qt.ItemDataRole.UserRole)
        return None

    def get_selected_sketch(self) -> SketchDocument | None:
        """Get the currently selected sketch."""
        key = self.get_selected_key()
        if key:
            return self._sketches.get(key)
        return None

    def select_sketch(self, key: str) -> None:
        """Select a sketch by key."""
        for i in range(self._list.count()):
            item = self._list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == key:
                self._list.setCurrentItem(item)
                break

    def _update_buttons(self) -> None:
        """Update button enabled states."""
        has_items = self._list.count() > 0
        has_selection = self._list.currentItem() is not None

        self._remove_btn.setEnabled(has_selection)
        self._clear_btn.setEnabled(has_items)

    def _on_selection_changed(self, current: QListWidgetItem | None, previous: QListWidgetItem | None) -> None:
        """Handle selection change."""
        self._update_buttons()

        if current:
            key = current.data(Qt.ItemDataRole.UserRole)
            self.sketch_selected.emit(key)

    def _on_remove_clicked(self) -> None:
        """Handle remove button click."""
        key = self.get_selected_key()
        if key:
            self.sketch_removed.emit(key)
            self.remove_sketch(key)

    def _on_clear_clicked(self) -> None:
        """Handle clear button click."""
        keys = list(self._sketches.keys())
        for key in keys:
            self.sketch_removed.emit(key)
        self.clear()
