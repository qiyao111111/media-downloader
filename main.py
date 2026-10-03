#!/usr/bin/env python3
"""Media Downloader desktop entry point."""

import sys
import multiprocessing

from PySide6.QtWidgets import QApplication

from services.settings_service import SettingsService as AppSettings
from gui.main_window import MainWindow
from gui.theme_manager import apply_theme
from pathlib import Path
from services.logging_service import configure_logging
from app.paths import PATHS
from app.version import PRODUCT,VERSION
from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon


def main():
    PATHS.initialize()
    configure_logging(PATHS.logs_dir/'desktop.log')
    import logging
    logging.getLogger('desktop').info('%s %s',PRODUCT,VERSION)
    if len(sys.argv)==3 and sys.argv[1]=='--diagnostics':
        import json
        from core.runtime_manager import health
        Path(sys.argv[2]).write_text(json.dumps(health(),indent=2),encoding='utf-8')
        return
    if len(sys.argv)==3 and sys.argv[1]=='--validate-release':
        from app.release_validation import run
        sys.exit(run(sys.argv[2]))
    app = QApplication(sys.argv)
    if (PATHS.resources_dir/'app.ico').is_file():app.setWindowIcon(QIcon(str(PATHS.resources_dir/'app.ico')))

    # Load saved theme preference
    settings = AppSettings()
    theme = settings.get("theme", "light")
    apply_theme(app, theme)

    window = MainWindow()
    import traceback
    from core.credentials import redact
    from gui.error_mapper import show_error
    def ui_exception(kind,error,tb):
        logging.getLogger('desktop').error('%s',redact(''.join(traceback.format_exception(kind,error,tb))))
        show_error(window,error)
    sys.excepthook=ui_exception
    app.styleHints().colorSchemeChanged.connect(lambda *_:apply_theme(app,'system') if window._settings_panel.theme_combo.currentData()=='system' else None)
    window.show()
    QTimer.singleShot(0,window.show_welcome)
    sys.exit(app.exec())


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
