import argparse
import logging
import os
import sys
import threading
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox, QProgressDialog

from infrastructure.parser import parse_signals
from ui.app import SignalsViewerApp


def validate_django_project(project_root: str) -> bool:
    """Basic Django project validation"""
    path = Path(project_root)
    return (path / "manage.py").exists()


def main() -> None:
    """
    Entry point for Django Signals UI.
    Simplified version that works with your existing SignalsViewerApp.
    """
    parser = argparse.ArgumentParser(description="Django Signals UI")
    parser.add_argument("--project-root", type=str, required=False, help="Root directory of your Django project")
    args = parser.parse_args()

    project_root = args.project_root

    app = QApplication(sys.argv)

    # Get project root
    if not project_root:
        project_root = QFileDialog.getExistingDirectory(None, "Select your Django project root directory")
        if not project_root:
            sys.exit(0)

    # Validate project
    if not os.path.isdir(project_root):
        QMessageBox.critical(None, "Error", f"Directory '{project_root}' is not valid.")
        sys.exit(1)

    if not validate_django_project(project_root):
        QMessageBox.critical(None, "Error", "The selected directory is not a valid Django project.")
        sys.exit(1)

    # Analyze signals with progress dialog
    signals_result = {}

    def worker():
        signals_result["signals"] = parse_signals(project_root)

    thread = threading.Thread(target=worker)
    thread.start()

    progress = QProgressDialog("Analyzing project signals...", None, 0, 0)
    progress.setWindowTitle("Loading")
    progress.setWindowModality(Qt.WindowModality.ApplicationModal)
    progress.setMinimumDuration(0)
    progress.show()

    while thread.is_alive():
        app.processEvents()

    progress.close()

    # Launch viewer using its existing run method
    signals = signals_result["signals"]
    viewer = SignalsViewerApp(signals)
    viewer.run()


if __name__ == "__main__":
    main()
