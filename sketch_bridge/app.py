"""SketchBridge application class."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from .ui.main_window import MainWindow


class SketchBridgeApp:
    """Main application class for SketchBridge."""

    def __init__(self, args: list[str] | None = None):
        """Initialize the application.

        Args:
            args: Command line arguments (uses sys.argv if None)
        """
        if args is None:
            args = sys.argv

        self._app = QApplication(args)
        self._app.setApplicationName("SketchBridge")
        self._app.setOrganizationName("SketchBridge")
        self._app.setApplicationVersion("0.1.0")

        self._window = MainWindow()

    def run(self) -> int:
        """Run the application.

        Returns:
            Exit code
        """
        self._window.show()
        return self._app.exec()


def main(args: list[str] | None = None) -> int:
    """Main entry point for SketchBridge.

    Args:
        args: Command line arguments (uses sys.argv if None)

    Returns:
        Exit code
    """
    app = SketchBridgeApp(args)
    return app.run()
