"""Collapsible log viewer widget."""

import logging
from gui.widgets.presentation import EmptyStateWidget
from core.credentials import redact
from i18n import tr,bind

from PySide6.QtWidgets import QGroupBox, QPlainTextEdit, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QApplication
from PySide6.QtCore import QObject, Signal, Qt, QUrl
from PySide6.QtGui import QDesktopServices
from pathlib import Path
from app.paths import PATHS


class LogBridge(QObject):
    message = Signal(str)


class QTextEditHandler(logging.Handler):
    """Logging handler that appends to a QPlainTextEdit."""

    def __init__(self, text_edit: QPlainTextEdit):
        super().__init__()
        self._bridge = LogBridge(text_edit)
        self._bridge.message.connect(text_edit.appendPlainText, Qt.QueuedConnection)

    def emit(self, record):
        msg = redact(self.format(record))
        self._bridge.message.emit(msg)


class LogViewerWidget(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent);bind(self,"nav.logs","setTitle")
        self.setCheckable(False)
        self.setChecked(True)
        layout = QVBoxLayout(self);layout.setContentsMargins(16,16,16,16);layout.setSpacing(12)
        self.empty=EmptyStateWidget("logs_empty","logs_description","logs");layout.addWidget(self.empty,1)

        self._text_edit = QPlainTextEdit()
        self._text_edit.setObjectName("log_viewer")
        self._text_edit.setReadOnly(True)
        self._text_edit.setMaximumBlockCount(2000)
        bind(self._text_edit,'logs_empty','setPlaceholderText')
        layout.addWidget(self._text_edit,1)
        self._text_edit.textChanged.connect(lambda:self._sync_empty());self._sync_empty()
        self.legend=bind(QLabel(),'log_time');layout.addWidget(self.legend)
        buttons = QHBoxLayout()
        for label, callback in [('Clear View', self._text_edit.clear), ('Copy Selected', self.copy_logs),
                                ('Open Log Folder', self.open_log_folder)]:
            button = bind(QPushButton(),{'Clear View':'clear_view','Copy Selected':'copy','Open Log Folder':'open_logs'}[label]); button.clicked.connect(callback); buttons.addWidget(button)
        layout.insertLayout(0,buttons)

        self.toggled.connect(self._on_toggle)

        # Install logging handler
        self._handler = QTextEditHandler(self._text_edit)
        self._handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        logging.getLogger().addHandler(self._handler)
        logging.getLogger('desktop').propagate = False
        logging.getLogger('desktop').addHandler(self._handler)

    def _sync_empty(self):
        empty=not self._text_edit.toPlainText();self.empty.setVisible(empty);self._text_edit.setVisible(not empty)

    def retranslate(self):
        self.legend.setText(' · '.join(tr(k) for k in ('log_time','log_level','log_message')))

    def _on_toggle(self, checked: bool):
        self._text_edit.setVisible(checked)

    def append(self, text: str):
        self._text_edit.appendPlainText(redact(text))

    def copy_logs(self):
        text=self._text_edit.textCursor().selectedText() or self._text_edit.toPlainText()
        QApplication.clipboard().setText(redact(text))

    def detach(self):
        logging.getLogger().removeHandler(self._handler)
        logging.getLogger('desktop').removeHandler(self._handler)
        self._handler.close()

    def open_log_folder(self):
        path = PATHS.logs_dir
        path.mkdir(exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
