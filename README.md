# SketchBridge

A desktop application for transferring 2D sketches between different CAD systems.

SketchBridge provides a unified interface for collecting sketches from one CAD application and exporting them to another, using the [canonical sketch format](https://github.com/CodeReclaimers/canonical_sketch) as an intermediate representation.

## Features

- **Multi-CAD Support**: Connect to FreeCAD, Autodesk Inventor, SolidWorks, and Fusion 360
- **Live Connection Monitoring**: Automatically detects when CAD systems are available
- **Sketch Preview**: Visual preview of sketches before export
- **Transform on Export**: Apply translation and rotation when exporting sketches
- **Plane Selection**: Choose the target plane (XY, XZ, YZ, or model faces) for sketch creation
- **File I/O**: Load and save sketches as JSON files

## Supported CAD Systems

| CAD System | Port | Adapter Package |
|------------|------|-----------------|
| FreeCAD | 9876 | `sketch_adapter_freecad` |
| Autodesk Inventor | 9877 | `sketch_adapter_inventor` |
| SolidWorks | 9878 | `sketch_adapter_solidworks` |
| Fusion 360 | 9879 | `sketch_adapter_fusion` |

## Installation

```bash
pip install sketch_bridge
```

Or install from source:

```bash
git clone https://github.com/your-org/sketch_bridge.git
cd sketch_bridge
pip install -e .
```

### Dependencies

- Python 3.10+
- PySide6
- `sketch_canonical` (canonical sketch format library)
- CAD adapter packages for each system you want to connect to

## Usage

### Starting SketchBridge

```bash
sketch-bridge
```

Or run as a module:

```bash
python -m sketch_bridge
```

### Setting Up CAD Connections

Each CAD system requires its RPC server to be running. The server runs inside the CAD application and exposes sketch functionality over the network.

#### FreeCAD

In FreeCAD's Python console:

```python
from sketch_adapter_freecad.server import start_server
start_server()
```

#### Other CAD Systems

Similar setup is required for Inventor, SolidWorks, and Fusion 360. Refer to each adapter's documentation for specific instructions.

### Workflow

1. **Start SketchBridge** - The application will automatically detect running CAD servers
2. **Collect Sketches** - Click "Collect" on a connected CAD system to import all its sketches
3. **Preview** - Select a sketch to see it in the preview panel
4. **Export** - Click "Export" to send the selected sketch to another CAD system

### Export Options

When exporting a sketch, you can configure:

- **Target Plane**: XY, XZ, YZ, or a planar face from the model
- **Translation**: Offset the sketch by (dx, dy) in millimeters
- **Rotation**: Rotate the sketch by a specified angle (degrees)
- **Strip Constraints**: Remove geometric constraints (recommended when applying rotation)

> **Note**: When applying rotation, the "Strip constraints" option is automatically enabled. This prevents the CAD solver from distorting the transformed geometry by trying to satisfy constraints that may conflict with the rotation.

### File Operations

- **Load File**: Import a sketch from a JSON file
- **Save File**: Export the selected sketch to a JSON file

## Architecture

```
sketch_bridge/
├── app.py              # Application entry point
├── transform.py        # Sketch transformation utilities
├── cad/
│   ├── manager.py      # CAD connection manager
│   └── clients.py      # CAD client wrappers
└── ui/
    ├── main_window.py  # Main application window
    ├── sketch_list.py  # Sketch list widget
    ├── preview.py      # Sketch preview widget
    ├── cad_status.py   # CAD connection status widget
    └── export_dialog.py # Export options dialog
```

## Development

### Setup

```bash
git clone https://github.com/your-org/sketch_bridge.git
cd sketch_bridge
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Style

This project uses [Ruff](https://github.com/astral-sh/ruff) for linting:

```bash
ruff check .
ruff format .
```

## Building Standalone Executables

SketchBridge can be packaged as a standalone Windows executable using PyInstaller. This allows users to run SketchBridge without installing Python.

### Prerequisites

- Python 3.10 or later
- All SketchBridge dependencies installed
- PyInstaller (installed automatically by the build script if missing)

### Building on Windows

Using PowerShell:

```powershell
.\build_windows.ps1
```

Or using Command Prompt:

```cmd
build_windows.bat
```

### Build Output

The build creates a folder-based distribution at:

```
dist/SketchBridge/
├── SketchBridge.exe    # Main executable
├── *.dll               # Required DLLs
└── ...                 # Other dependencies
```

To distribute SketchBridge, copy the entire `dist/SketchBridge` folder to the target machine.

### Build Configuration

The build is configured via `sketch_bridge.spec`. Key settings:

- **Hidden imports**: CAD adapter packages and PySide6 modules
- **Excludes**: Unnecessary packages (numpy, matplotlib, etc.) to reduce size
- **Console mode**: Disabled (windowed application)

To add a custom icon, edit `sketch_bridge.spec` and set the `icon` parameter:

```python
exe = EXE(
    ...
    icon='assets/icon.ico',  # Windows icon file
)
```

## Related Projects

- [canonical_sketch](https://github.com/CodeReclaimers/canonical_sketch) - The canonical sketch format library
- [sketch_adapter_freecad](https://github.com/CodeReclaimers/canonical_sketch) - FreeCAD adapter
- [sketch_adapter_inventor](https://github.com/CodeReclaimers/canonical_sketch) - Inventor adapter
- [sketch_adapter_solidworks](https://github.com/CodeReclaimers/canonical_sketch) - SolidWorks adapter
- [sketch_adapter_fusion](https://github.com/CodeReclaimers/canonical_sketch) - Fusion 360 adapter

## License

MIT License - see [LICENSE](LICENSE) for details.
