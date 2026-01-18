"""CAD connection manager for SketchBridge."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QObject, QTimer, Signal

from .clients import (
    CADClient,
    FreeCADClientWrapper,
    FusionClientWrapper,
    InventorClientWrapper,
    SolidWorksClientWrapper,
)

if TYPE_CHECKING:
    from morphe import SketchDocument


class CADSystem(Enum):
    """Supported CAD systems."""

    FREECAD = auto()
    INVENTOR = auto()
    SOLIDWORKS = auto()
    FUSION = auto()


# Mapping from enum to display name
CAD_NAMES = {
    CADSystem.FREECAD: "FreeCAD",
    CADSystem.INVENTOR: "Inventor",
    CADSystem.SOLIDWORKS: "SolidWorks",
    CADSystem.FUSION: "Fusion 360",
}


class CADManager(QObject):
    """Manages connections to multiple CAD systems.

    Signals:
        connection_changed(CADSystem, bool): Emitted when connection status changes
        status_updated(CADSystem, dict): Emitted when status is updated
    """

    connection_changed = Signal(object, bool)  # CADSystem, connected
    status_updated = Signal(object, dict)  # CADSystem, status_dict

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create clients for all systems
        self._clients: dict[CADSystem, CADClient] = {
            CADSystem.FREECAD: FreeCADClientWrapper(),
            CADSystem.INVENTOR: InventorClientWrapper(),
            CADSystem.SOLIDWORKS: SolidWorksClientWrapper(),
            CADSystem.FUSION: FusionClientWrapper(),
        }

        # Track connection status
        self._connected: dict[CADSystem, bool] = dict.fromkeys(CADSystem, False)

        # Status cache
        self._status: dict[CADSystem, dict] = {system: {} for system in CADSystem}

        # Thread pool for background connection checking
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._check_in_progress = False

        # Timer for periodic status checks
        self._check_timer = QTimer(self)
        self._check_timer.timeout.connect(self._check_connections)
        self._check_interval = 5000  # 5 seconds

    def start_monitoring(self) -> None:
        """Start periodic connection monitoring."""
        self._check_connections()
        self._check_timer.start(self._check_interval)

    def stop_monitoring(self) -> None:
        """Stop periodic connection monitoring."""
        self._check_timer.stop()
        self._executor.shutdown(wait=False)

    def _check_connections(self) -> None:
        """Check all CAD system connections in background threads."""
        if self._check_in_progress:
            return  # Skip if previous check is still running

        self._check_in_progress = True

        # Submit all checks to thread pool
        futures = []
        for system in CADSystem:
            future = self._executor.submit(self._check_system_thread, system)
            futures.append((system, future))

        # Schedule result collection on main thread
        QTimer.singleShot(0, lambda: self._collect_results(futures))

    def _check_system_thread(self, system: CADSystem) -> tuple[bool, dict]:
        """Check connection to a CAD system (runs in background thread).

        Returns:
            Tuple of (connected, status_dict)
        """
        client = self._clients[system]

        try:
            # Try to connect if not already connected
            connected = client.connect(timeout=1.0) if not client.is_connected() else True

            if connected:
                status = client.get_status()
                return (True, status)
            else:
                return (False, {})
        except Exception:
            return (False, {})

    def _collect_results(self, futures: list) -> None:
        """Collect results from background checks (runs on main thread)."""
        all_done = True

        for system, future in futures:
            if future.done():
                try:
                    connected, status = future.result(timeout=0)
                    was_connected = self._connected[system]

                    self._connected[system] = connected
                    self._status[system] = status

                    if connected and status:
                        self.status_updated.emit(system, status)

                    if connected != was_connected:
                        self.connection_changed.emit(system, connected)
                except Exception:
                    pass
            else:
                all_done = False

        if all_done:
            self._check_in_progress = False
        else:
            # Check again in 100ms
            QTimer.singleShot(100, lambda: self._collect_results(futures))

    def is_connected(self, system: CADSystem) -> bool:
        """Check if a CAD system is connected."""
        return self._connected.get(system, False)

    def get_status(self, system: CADSystem) -> dict[str, Any]:
        """Get cached status for a CAD system."""
        return self._status.get(system, {})

    def get_client(self, system: CADSystem) -> CADClient:
        """Get the client for a CAD system."""
        return self._clients[system]

    def list_sketches(self, system: CADSystem) -> list[dict[str, Any]]:
        """List sketches from a CAD system.

        Returns:
            List of sketch info dicts, or empty list if not connected
        """
        if not self._connected.get(system, False):
            return []

        try:
            return self._clients[system].list_sketches()
        except Exception:
            return []

    def export_sketch(self, system: CADSystem, sketch_name: str) -> SketchDocument | None:
        """Export a sketch from a CAD system.

        Returns:
            SketchDocument, or None if export failed
        """
        if not self._connected.get(system, False):
            return None

        try:
            return self._clients[system].export_sketch(sketch_name)
        except Exception:
            return None

    def import_sketch(
        self,
        system: CADSystem,
        doc: SketchDocument,
        name: str | None = None,
        plane: str | None = None,
    ) -> str | None:
        """Import a sketch into a CAD system.

        Args:
            system: Target CAD system
            doc: SketchDocument to import
            name: Optional name override
            plane: Optional plane ID for sketch creation

        Returns:
            Name of created sketch, or None if import failed
        """
        if not self._connected.get(system, False):
            return None

        try:
            import contextlib

            created_name = self._clients[system].import_sketch(doc, name, plane)
            # Try to open it in the CAD UI
            with contextlib.suppress(Exception):
                self._clients[system].open_sketch(created_name)
            return created_name
        except Exception:
            return None

    def connect(self, system: CADSystem, timeout: float = 5.0) -> bool:
        """Manually connect to a CAD system."""
        client = self._clients[system]
        try:
            connected = client.connect(timeout)
            self._connected[system] = connected
            if connected:
                self._status[system] = client.get_status()
            self.connection_changed.emit(system, connected)
            return connected
        except Exception:
            self._connected[system] = False
            self.connection_changed.emit(system, False)
            return False

    def disconnect(self, system: CADSystem) -> None:
        """Disconnect from a CAD system."""
        client = self._clients[system]
        client.disconnect()
        self._connected[system] = False
        self._status[system] = {}
        self.connection_changed.emit(system, False)

    @staticmethod
    def get_system_name(system: CADSystem) -> str:
        """Get the display name for a CAD system."""
        return CAD_NAMES.get(system, str(system))

    @staticmethod
    def get_all_systems() -> list[CADSystem]:
        """Get list of all supported CAD systems."""
        return list(CADSystem)
