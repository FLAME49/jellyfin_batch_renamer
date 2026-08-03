"""Application entry point."""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from ui import MainWindow


def main() -> int:
    """Create the Qt application and show the main window."""
    app = QApplication(sys.argv)
    app.setApplicationName("Jellyfin Batch Renamer")
    app.setOrganizationName("Jellyfin Tools")
    icon_path = Path(__file__).resolve().parent / "assets" / "app_icon.png"
    app.setWindowIcon(QIcon(str(icon_path)))
    window = MainWindow()
    window.setWindowIcon(QIcon(str(icon_path)))
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
