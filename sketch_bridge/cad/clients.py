"""CAD client wrappers for unified access."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from morphe import SketchDocument


class CADClient(ABC):
    """Abstract base class for CAD system clients."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the display name of this CAD system."""
        ...

    @property
    @abstractmethod
    def default_port(self) -> int:
        """Return the default RPC port for this CAD system."""
        ...

    @abstractmethod
    def connect(self, timeout: float = 5.0) -> bool:
        """Connect to the CAD system's RPC server."""
        ...

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the CAD system."""
        ...

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected to the CAD system."""
        ...

    @abstractmethod
    def get_status(self) -> dict[str, Any]:
        """Get status information from the CAD system."""
        ...

    @abstractmethod
    def list_sketches(self) -> list[dict[str, Any]]:
        """List all sketches in the active document."""
        ...

    @abstractmethod
    def list_planes(self) -> list[dict[str, Any]]:
        """List available planes for sketch creation."""
        ...

    @abstractmethod
    def export_sketch(self, name: str) -> SketchDocument:
        """Export a sketch from the CAD system."""
        ...

    @abstractmethod
    def import_sketch(
        self, doc: SketchDocument, name: str | None = None, plane: str | None = None
    ) -> str:
        """Import a sketch into the CAD system."""
        ...

    @abstractmethod
    def open_sketch(self, name: str) -> bool:
        """Open a sketch for editing in the CAD UI."""
        ...


class FreeCADClientWrapper(CADClient):
    """Wrapper for FreeCAD RPC client."""

    def __init__(self, host: str = "localhost", port: int = 9876):
        self._host = host
        self._port = port
        self._client = None

    @property
    def name(self) -> str:
        return "FreeCAD"

    @property
    def default_port(self) -> int:
        return 9876

    def _get_client(self):
        """Lazy import and create client."""
        if self._client is None:
            from morphe.adapters.freecad import FreeCADClient

            self._client = FreeCADClient(self._host, self._port)
        return self._client

    def connect(self, timeout: float = 5.0) -> bool:
        return self._get_client().connect(timeout)

    def disconnect(self) -> None:
        if self._client:
            self._client.disconnect()

    def is_connected(self) -> bool:
        if self._client is None:
            return False
        return self._client.is_connected()

    def get_status(self) -> dict[str, Any]:
        return self._get_client().get_status()

    def list_sketches(self) -> list[dict[str, Any]]:
        return self._get_client().list_sketches()

    def list_planes(self) -> list[dict[str, Any]]:
        return self._get_client().list_planes()

    def export_sketch(self, name: str) -> SketchDocument:
        return self._get_client().export_sketch(name)

    def import_sketch(
        self, doc: SketchDocument, name: str | None = None, plane: str | None = None
    ) -> str:
        return self._get_client().import_sketch(doc, name, plane)

    def open_sketch(self, name: str) -> bool:
        return self._get_client().open_sketch(name)


class InventorClientWrapper(CADClient):
    """Wrapper for Inventor RPC client."""

    def __init__(self, host: str = "localhost", port: int = 9877):
        self._host = host
        self._port = port
        self._client = None

    @property
    def name(self) -> str:
        return "Inventor"

    @property
    def default_port(self) -> int:
        return 9877

    def _get_client(self):
        """Lazy import and create client."""
        if self._client is None:
            from morphe.adapters.inventor import InventorClient

            self._client = InventorClient(self._host, self._port)
        return self._client

    def connect(self, timeout: float = 5.0) -> bool:
        return self._get_client().connect(timeout)

    def disconnect(self) -> None:
        if self._client:
            self._client.disconnect()

    def is_connected(self) -> bool:
        if self._client is None:
            return False
        return self._client.is_connected()

    def get_status(self) -> dict[str, Any]:
        return self._get_client().get_status()

    def list_sketches(self) -> list[dict[str, Any]]:
        return self._get_client().list_sketches()

    def list_planes(self) -> list[dict[str, Any]]:
        return self._get_client().list_planes()

    def export_sketch(self, name: str) -> SketchDocument:
        return self._get_client().export_sketch(name)

    def import_sketch(
        self, doc: SketchDocument, name: str | None = None, plane: str | None = None
    ) -> str:
        return self._get_client().import_sketch(doc, name, plane)

    def open_sketch(self, name: str) -> bool:
        return self._get_client().open_sketch(name)


class SolidWorksClientWrapper(CADClient):
    """Wrapper for SolidWorks RPC client."""

    def __init__(self, host: str = "localhost", port: int = 9878):
        self._host = host
        self._port = port
        self._client = None

    @property
    def name(self) -> str:
        return "SolidWorks"

    @property
    def default_port(self) -> int:
        return 9878

    def _get_client(self):
        """Lazy import and create client."""
        if self._client is None:
            from morphe.adapters.solidworks import SolidWorksClient

            self._client = SolidWorksClient(self._host, self._port)
        return self._client

    def connect(self, timeout: float = 5.0) -> bool:
        return self._get_client().connect(timeout)

    def disconnect(self) -> None:
        if self._client:
            self._client.disconnect()

    def is_connected(self) -> bool:
        if self._client is None:
            return False
        return self._client.is_connected()

    def get_status(self) -> dict[str, Any]:
        return self._get_client().get_status()

    def list_sketches(self) -> list[dict[str, Any]]:
        return self._get_client().list_sketches()

    def list_planes(self) -> list[dict[str, Any]]:
        return self._get_client().list_planes()

    def export_sketch(self, name: str) -> SketchDocument:
        return self._get_client().export_sketch(name)

    def import_sketch(
        self, doc: SketchDocument, name: str | None = None, plane: str | None = None
    ) -> str:
        return self._get_client().import_sketch(doc, name, plane)

    def open_sketch(self, name: str) -> bool:
        return self._get_client().open_sketch(name)


class FusionClientWrapper(CADClient):
    """Wrapper for Fusion 360 RPC client."""

    def __init__(self, host: str = "localhost", port: int = 9879):
        self._host = host
        self._port = port
        self._client = None

    @property
    def name(self) -> str:
        return "Fusion 360"

    @property
    def default_port(self) -> int:
        return 9879

    def _get_client(self):
        """Lazy import and create client."""
        if self._client is None:
            from morphe.adapters.fusion import FusionClient

            self._client = FusionClient(self._host, self._port)
        return self._client

    def connect(self, timeout: float = 5.0) -> bool:
        return self._get_client().connect(timeout)

    def disconnect(self) -> None:
        if self._client:
            self._client.disconnect()

    def is_connected(self) -> bool:
        if self._client is None:
            return False
        return self._client.is_connected()

    def get_status(self) -> dict[str, Any]:
        return self._get_client().get_status()

    def list_sketches(self) -> list[dict[str, Any]]:
        return self._get_client().list_sketches()

    def list_planes(self) -> list[dict[str, Any]]:
        return self._get_client().list_planes()

    def export_sketch(self, name: str) -> SketchDocument:
        return self._get_client().export_sketch(name)

    def import_sketch(
        self, doc: SketchDocument, name: str | None = None, plane: str | None = None
    ) -> str:
        return self._get_client().import_sketch(doc, name, plane)

    def open_sketch(self, name: str) -> bool:
        return self._get_client().open_sketch(name)


def get_client_for_system(system: str, host: str = "localhost") -> CADClient:
    """Get a client for a specific CAD system.

    Args:
        system: One of 'freecad', 'inventor', 'solidworks', 'fusion'
        host: Server host (default: localhost)

    Returns:
        CADClient instance for the specified system
    """
    system = system.lower()
    if system == "freecad":
        return FreeCADClientWrapper(host)
    elif system == "inventor":
        return InventorClientWrapper(host)
    elif system == "solidworks":
        return SolidWorksClientWrapper(host)
    elif system in ("fusion", "fusion360", "fusion 360"):
        return FusionClientWrapper(host)
    else:
        raise ValueError(f"Unknown CAD system: {system}")
