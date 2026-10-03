"""Downloader controls; B2 profiles are display data, never parsed from labels."""
from pathlib import Path
from PySide6.QtCore import Qt,QUrl,Signal
from PySide6.QtGui import QPixmap
from PySide6.QtNetwork import QNetworkAccessManager,QNetworkRequest
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QGridLayout,QFormLayout,QLabel,QComboBox,QCheckBox,QLineEdit,QPushButton,QFileDialog,QPlainTextEdit,QTableWidget,QTableWidgetItem,QHeaderView
from i18n import tr,bind,combo_labels
from gui.widgets.presentation import page_layout,page_header,card,QualityChip,InfoChip,TwoLineLabel,refresh,ElidedLabel,ThumbnailLabel
from gui.design_tokens import CONTROL
from gui.widgets.url_input import UrlInputWidget
from gui.widgets.collapsible_section import CollapsibleSection


def display_label(profile):
    return profile.label.replace('H264', 'H.264').replace('H265', 'H.265').replace('OPUS', 'Opus')


class DownloaderPage(QWidget):
    selection_changed=Signal()
    def __init__(self,parent=None):
        super().__init__(parent)
        self.info=None;self.url='';self.analyzing=False;self.selection=None;self._reply=None;self.custom_mode=False
        layout=page_layout(self)
        page_header(layout,"download_title","download_subtitle")
        self.urls=UrlInputWidget()
        bind(self.urls,'url','setTitle')
        layout.addWidget(self.urls)
        self.message=bind(QLabel(),'analyze_hint');self.message.setWordWrap(True)
        self.message.setTextFormat(Qt.PlainText);layout.addWidget(self.message)
        video,video_layout=card();layout.addWidget(video)
        row=QHBoxLayout();self.thumbnail=bind(ThumbnailLabel(),'no_thumbnail');self.thumbnail.setFixedSize(240,135);self.thumbnail.setObjectName('thumbnail')
        self.thumbnail.setAlignment(Qt.AlignCenter);row.addWidget(self.thumbnail)
        self.metadata=bind(QLabel(),'no_info');self.metadata.setTextFormat(Qt.PlainText)
        self.metadata.hide()
        information=QVBoxLayout();self.title=TwoLineLabel();self.title.setProperty('role','section');bind(self.title,'no_info');information.addWidget(self.title)
        self.byline=ElidedLabel();self.byline.setProperty('role','secondary');information.addWidget(self.byline)
        self.chips=QGridLayout();self.chips.setSpacing(8);information.addLayout(self.chips);information.addStretch();row.addLayout(information,1);video_layout.addLayout(row)
        config,config_layout=card();layout.addWidget(config);heading=bind(QLabel(),'configuration');heading.setProperty('role','section');config_layout.addWidget(heading)
        form=QFormLayout();form.setVerticalSpacing(8);self.quality=QComboBox();self.quality.setMinimumWidth(0)
        self.quality.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon);self.quality.setMinimumContentsLength(12)
        self.quality.addItem(tr('best_quality'),'best');quality_row=QHBoxLayout();quality_row.addWidget(self.quality,1);self.recommended=bind(InfoChip(),'recommended');quality_row.addWidget(self.recommended);form.addRow(bind(QLabel(),'quality'),quality_row)
        bind(self.quality,'tooltip.codec','setToolTip')
        self.container=QComboBox()
        for label,value in [(tr('auto'),''),('MP4','mp4'),('MKV','mkv'),('WebM','webm')]:self.container.addItem(label,value)
        form.addRow(bind(QLabel(),'container'),self.container)
        bind(self.container,'tooltip.container','setToolTip')
        self.audio_only=bind(QCheckBox(),'audio_only');self.audio_format=QComboBox()
        for label,value in [(tr('best_audio'),'best'),('MP3','mp3'),('M4A','m4a'),('Opus','opus'),('FLAC','flac'),('WAV','wav')]:self.audio_format.addItem(label,value)
        audio=QHBoxLayout();audio.addWidget(self.audio_only);audio.addWidget(self.audio_format,1);form.addRow(audio)
        path=QHBoxLayout();self.path=QLineEdit();browse=bind(QPushButton(),'browse');browse.clicked.connect(self._browse)
        path.addWidget(self.path,1);path.addWidget(browse);form.addRow(bind(QLabel(),'save_to'),path);config_layout.addLayout(form)
        self.details=CollapsibleSection('');bind(self.details._toggle_btn,'advanced_details')
        self.details_text=QPlainTextEdit();self.details_text.setReadOnly(True);self.details_text.setMaximumHeight(110)
        self.details.add_widget(self.details_text)
        self.raw=QTableWidget(0,8);self.raw.setHorizontalHeaderLabels(['ID','Dimensions','FPS','Range','Video codec','Audio codec','Container','Size'])
        self.raw.setEditTriggers(QTableWidget.NoEditTriggers);self.raw.setMaximumHeight(180)
        self.raw.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.details.add_widget(self.raw);layout.addWidget(self.details)
        self.download=bind(QPushButton(),'download');self.download.setObjectName('btn_download');self.download.setMinimumHeight(CONTROL["large"]);self.download.setMaximumWidth(240);layout.addWidget(self.download)
        layout.addStretch()
        self.network=QNetworkAccessManager(self)
        for signal in (self.quality.currentIndexChanged,self.container.currentIndexChanged,self.audio_only.toggled,self.audio_format.currentIndexChanged,self.path.textChanged):
            signal.connect(lambda *_: self.selection_changed.emit())
        self.urls._text_edit.textChanged.connect(self.invalidate)
        self.retranslate();self.update_buttons()

    def retranslate(self):
        combo_labels(self.quality,['best_quality']+[None]*(self.quality.count()-1))
        combo_labels(self.container,['auto',None,None,None])
        combo_labels(self.audio_format,['best_audio',None,None,None,None,None])
        self.raw.setHorizontalHeaderLabels([tr(k) for k in ('id','dimensions','fps','range','video_codec','audio_codec','container','size')])
        bind(self.raw,'tooltip.hdr','setToolTip')
        if self.info:self._render_metadata(self.info,self._best)
        self.update_buttons()

    def invalidate(self):
        self.info=None;self.selection=None;self.url=''
        self.quality.clear();self.quality.addItem(tr('best_quality'),'best')
        bind(self.metadata,'no_info');bind(self.thumbnail,'no_thumbnail');self.raw.setRowCount(0)
        bind(self.title,'no_info');self.byline.clear();self._clear_chips();self.set_error(False)
        self.details_text.clear();bind(self.message,'analyze_hint')
        if self._reply:self._reply.abort()
        self.update_buttons()

    def update_buttons(self,duplicate=False):
        self.urls._btn_formats.setEnabled(bool(self.urls.get_urls()) and not self.analyzing)
        self.recommended.setVisible(self.quality.currentData()=='best' and not self.audio_only.isChecked())
        self.urls.spinner.setVisible(self.analyzing)
        bind(self.urls._btn_formats,'analyzing' if self.analyzing else 'retry' if self.urls._text_edit.property('invalid') else 'analyze')
        self.quality.setEnabled(bool(self.info) and not self.audio_only.isChecked() and not self.custom_mode and self.info.get('_type')!='playlist')
        self.audio_format.setEnabled(self.audio_only.isChecked())
        self.container.setEnabled(not self.audio_only.isChecked())
        path=Path(self.path.text())
        self.download.setEnabled(bool(self.info) and not self.analyzing and (self.selection is not None or self.custom_mode or self.info.get('_type')=='playlist') and bool(self.path.text()) and path.is_dir() and not duplicate)
        bind(self.download,'download_all' if self.info and self.info.get('_type')=='playlist' else 'download')
        bind(self.path,'path_missing' if self.path.text() and not path.is_dir() else 'save_to','setToolTip')

    def set_info(self,url,info,options,best,raw_formats=None):
        self.info=info;self.url=url;self.analyzing=False;self._best=best
        self.quality.blockSignals(True);self.quality.clear();self.quality.addItem(tr('best_quality'),'best')
        for profile in options:self.quality.addItem(display_label(profile),profile)
        self.quality.blockSignals(False)
        self.set_error(False);self._render_metadata(info,best)
        bind(self.message,'playlist_ready' if info.get('_type')=='playlist' else 'ready_hint')
        bind(self.thumbnail,'no_thumbnail')
        raw_formats = raw_formats if raw_formats is not None else options
        self.raw.setRowCount(len(raw_formats))
        for row,p in enumerate(raw_formats):
            for col,value in enumerate((p.format_id,p.resolution,p.fps,p.dynamic_range,p.video_codec,p.audio_codec,p.container,p.filesize or p.filesize_approx)):
                self.raw.setItem(row,col,QTableWidgetItem(str(value) if value is not None else '--'))
        if info.get('thumbnail'):self._load_thumbnail(info['thumbnail'])
        self.selection=best;self.update_buttons()

    def _render_metadata(self,info,best):
        self.metadata.setProperty('i18n_bindings',{})
        title=str(info.get('title') or '--');channel=str(info.get('channel') or info.get('uploader') or '--')
        if info.get('_type')=='playlist':
            count=info.get('playlist_count') or len(info.get('entries') or [])
            self.metadata.setText(f'{title[:240]}\n{channel}\n'+tr('playlist_metadata',count=count));self.metadata.setToolTip(title)
        else:
            self.metadata.setText(f'{title[:240]}\n{channel}\n'+tr('duration')+': '+str(info.get("duration_string") or info.get("duration") or "--")+'\n'+tr('highest')+': '+(display_label(best.video or best.muxed) if best and (best.video or best.muxed) else "--"))
            self.metadata.setToolTip(title)
        self.title.setProperty('i18n_bindings',{});self.title.setText(title);self.title.setToolTip(title)
        self.byline.setText(channel+' · '+str(info.get('duration_string') or info.get('duration') or '--'));self.byline.setToolTip(self.byline.text())
        self._clear_chips()
        profile=(best.video or best.muxed) if best else None
        if profile:
            for value in display_label(profile).split(' · '):
                if value not in ('mp4','webm','mkv'):
                    index=self.chips.count();self.chips.addWidget(QualityChip(value),index//3,index%3,Qt.AlignLeft)

    def _clear_chips(self):
        while self.chips.count():
            item=self.chips.takeAt(0)
            if item.widget():item.widget().hide();item.widget().deleteLater()

    def set_error(self,invalid):
        self.urls._text_edit.setProperty('invalid',invalid);refresh(self.urls._text_edit)
        self.message.setProperty('role','error' if invalid else 'secondary');refresh(self.message)

    def _load_thumbnail(self,url):
        if self._reply:self._reply.abort()
        self.thumbnail.clear();bind(self.thumbnail,'thumbnail_loading')
        req=QNetworkRequest(QUrl(url));req.setTransferTimeout(10000)
        reply=self.network.get(req);self._reply=reply
        def finished():
            if reply is self._reply:
                pix=QPixmap();pix.loadFromData(reply.readAll())
                if not pix.isNull():
                    self.thumbnail.setProperty('i18n_bindings',{});self.thumbnail.setPixmap(pix.scaled(self.thumbnail.size(),Qt.KeepAspectRatio,Qt.SmoothTransformation))
                else:bind(self.thumbnail,'no_thumbnail')
                self._reply=None
            reply.deleteLater()
        reply.finished.connect(finished)

    def _browse(self):
        path=QFileDialog.getExistingDirectory(self,tr('save_to'),self.path.text())
        if path:self.path.setText(path)

    def close_thumbnail(self):
        if self._reply:self._reply.abort()
