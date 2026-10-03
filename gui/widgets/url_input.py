"""URL input widget – multi-line text area with paste/import/format buttons."""

from PySide6.QtCore import Signal, QEvent, Qt
from i18n import tr,bind
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QProgressBar,
)


class UrlInputWidget(QGroupBox):

    format_requested = Signal()  # emitted when user wants to preview formats

    def __init__(self, parent=None):
        super().__init__(parent)
        bind(self,"url","setTitle")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 16)
        layout.setSpacing(8)

        self._text_edit = QPlainTextEdit()
        self._text_edit.setPlaceholderText(
            tr("url_placeholder")
        )
        bind(self._text_edit,"url_placeholder","setPlaceholderText")
        self._text_edit.setFixedHeight(44)
        self._text_edit.textChanged.connect(lambda:self._text_edit.setFixedHeight(64 if len(self.get_urls())>1 else 44))
        self._text_edit.installEventFilter(self)
        input_row=QHBoxLayout();input_row.addWidget(self._text_edit,1);layout.addLayout(input_row)
        self.spinner=QProgressBar();self.spinner.setRange(0,0);self.spinner.setTextVisible(False);self.spinner.setFixedHeight(8);self.spinner.hide();layout.addWidget(self.spinner)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self._btn_paste = bind(QPushButton(),"paste")
        self._btn_paste.clicked.connect(self._paste_clipboard)

        self._btn_import = bind(QPushButton(),"import")
        self._btn_import.clicked.connect(self._import_batch)

        self._btn_formats = bind(QPushButton(),"analyze")
        self._btn_formats.setObjectName('btn_analyze');self._btn_formats.setMinimumHeight(44)
        bind(self._btn_formats,"analyze_tooltip","setToolTip")
        self._btn_formats.clicked.connect(self.format_requested.emit)

        self._btn_clear = bind(QPushButton(),"clear")
        self._btn_clear.clicked.connect(self._text_edit.clear)

        btn_layout.addWidget(self._btn_paste)
        btn_layout.addWidget(self._btn_import)
        btn_layout.addStretch()
        input_row.addWidget(self._btn_formats)
        btn_layout.addWidget(self._btn_clear)
        layout.addLayout(btn_layout)

    def eventFilter(self,watched,event):
        if watched is self._text_edit and event.type()==QEvent.KeyPress and event.key() in (Qt.Key_Return,Qt.Key_Enter):
            if not event.modifiers() and len(self.get_urls())==1:
                if self._btn_formats.isEnabled(): self.format_requested.emit()
                return True
        return super().eventFilter(watched,event)

    def get_urls(self) -> list[str]:
        text = self._text_edit.toPlainText().strip()
        if not text:
            return []
        urls = []
        seen = set()
        for line in text.splitlines():
            line = line.strip()
            if line and not line.startswith("#") and line not in seen:
                urls.append(line)
                seen.add(line)
        return urls

    def get_first_url(self) -> str:
        urls = self.get_urls()
        return urls[0] if urls else ""

    def clear(self):
        self._text_edit.clear()

    def _paste_clipboard(self):
        text = QApplication.clipboard().text()
        if text:
            current = self._text_edit.toPlainText()
            if current and not current.endswith("\n"):
                current += "\n"
            self._text_edit.setPlainText(current + text)

    def _import_batch(self):
        path, _ = QFileDialog.getOpenFileName(
            self, tr("import"), "", tr("text_files")
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.read()
            current = self._text_edit.toPlainText()
            if current and not current.endswith("\n"):
                current += "\n"
            self._text_edit.setPlainText(current + lines)
        except OSError as e:
            from gui.error_mapper import show_error
            show_error(self,e,'error.read_file')
