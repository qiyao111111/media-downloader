"""Small, local-only product dialogs. No account, telemetry or runtime changes."""
from pathlib import Path
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices,QIcon
from PySide6.QtWidgets import QDialog,QVBoxLayout,QLabel,QPushButton,QHBoxLayout,QLineEdit,QComboBox,QFileDialog,QScrollArea,QWidget
from gui.widgets.presentation import PrimaryButton,SecondaryButton,line_icon
from PySide6.QtWidgets import QApplication
from app.version import PRODUCT,VERSION
from app.paths import PATHS
from i18n import tr,bind,combo_labels,translate_tree


def open_licenses(parent):
    candidates=(PATHS.application_dir/'THIRD_PARTY_NOTICES.txt',PATHS.application_dir/'redistribution/THIRD_PARTY_NOTICES.txt')
    path=next((p for p in candidates if p.is_file()),None)
    if path:QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
    else:
        from gui.error_mapper import show_error
        show_error(parent,FileNotFoundError('THIRD_PARTY_NOTICES.txt'))


class ProductDialog(QDialog):
    def __init__(self,parent=None,help_mode=False):
        super().__init__(parent);bind(self,'help' if help_mode else 'about','setWindowTitle')
        height=min(620,parent.height()-24 if parent else QApplication.primaryScreen().availableGeometry().height()-40)
        self.resize(560,height);outer=QVBoxLayout(self);outer.setContentsMargins(24,24,24,24);outer.setSpacing(16)
        content=QWidget();layout=QVBoxLayout(content);layout.setContentsMargins(0,0,0,0);layout.setSpacing(16)
        area=QScrollArea();area.setWidgetResizable(True);area.setWidget(content);outer.addWidget(area,1)
        product_icon=QIcon(str(PATHS.resources_dir/'app.ico') if (PATHS.resources_dir/'app.ico').is_file() else str(PATHS.resources_dir/'build/app.ico'))
        if product_icon.isNull():product_icon=line_icon('download')
        icon=QLabel();icon.setPixmap(product_icon.pixmap(32,32));layout.addWidget(icon)
        self.version_label=QLabel(PRODUCT+' · '+VERSION);self.version_label.setObjectName('product_version');layout.addWidget(self.version_label)
        for key in ('rc','about_description','help_steps' if help_mode else 'powered_by','codec_compatibility','cookies_security','rights','local_privacy'):
            label=bind(QLabel(),key);label.setWordWrap(True);layout.addWidget(label)
        licenses=bind(QPushButton(),'third_party');licenses.clicked.connect(lambda:open_licenses(self));layout.addWidget(licenses)
        if parent and hasattr(parent,'_log_viewer'):
            logs=SecondaryButton('open_logs');logs.clicked.connect(parent._log_viewer.open_log_folder);layout.addWidget(logs)
            copy=SecondaryButton('copy_diagnostics');copy.clicked.connect(lambda:QApplication.clipboard().setText(parent._runtime_label.text()+'\n'+parent._tools_label.text()));layout.addWidget(copy)
        layout.addStretch();close=PrimaryButton('close');close.clicked.connect(self.accept);outer.addWidget(close)


class WelcomeDialog(QDialog):
    def __init__(self,window):
        super().__init__(window);self.window=window;bind(self,'welcome','setWindowTitle');self.resize(500,300)
        layout=QVBoxLayout(self);layout.setSpacing(14)
        for key in ('welcome','welcome_description'):
            label=bind(QLabel(),key);label.setWordWrap(True);layout.addWidget(label)
        self.language=QComboBox();self.language.addItem('English','en');self.language.addItem('简体中文','zh')
        self.language.setCurrentIndex(max(0,self.language.findData(window._settings_panel.language_combo.currentData())))
        layout.addWidget(bind(QLabel(),'language'));layout.addWidget(self.language)
        layout.addWidget(bind(QLabel(),'default_folder'));row=QHBoxLayout();self.path=QLineEdit(window._downloader.path.text());row.addWidget(self.path,1)
        browse=bind(QPushButton(),'browse');row.addWidget(browse);layout.addLayout(row)
        def pick():
            folder=QFileDialog.getExistingDirectory(self,tr('default_folder'),self.path.text())
            if folder:self.path.setText(folder)
        browse.clicked.connect(pick)
        def language_changed():
            combo=window._settings_panel.language_combo
            combo.setCurrentIndex(combo.findData(self.language.currentData()));translate_tree(self)
        self.language.currentIndexChanged.connect(language_changed)
        start=bind(QPushButton(),'get_started');start.setDefault(True);start.clicked.connect(self.save);layout.addWidget(start)

    def save(self):
        if not Path(self.path.text()).is_dir():
            from gui.error_mapper import show_error
            show_error(self,ValueError(tr('path_missing')));return
        self.window._settings_panel.path_edit.setText(self.path.text())
        if self.window._save_settings():
            self.window._settings.set('onboarding_complete',True);self.window._settings.save();self.accept()
