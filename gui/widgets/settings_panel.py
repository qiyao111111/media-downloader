"""Product settings presentation; existing option collection remains independent of wording."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox,QComboBox,QFileDialog,QFormLayout,QHBoxLayout,QLabel,QLineEdit,QPushButton,QSlider,QSpinBox,QVBoxLayout,QWidget,QListWidget,QStackedWidget
from gui.widgets.presentation import InfoChip,refresh,InfoBanner
from gui.widgets.collapsible_section import CollapsibleSection
from app.version import PRODUCT,VERSION
from i18n import tr,bind,combo_labels


class SettingsPanel(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        layout=QHBoxLayout(self);layout.setContentsMargins(0,0,0,0);layout.setSpacing(16)
        self.categories=QListWidget();self.categories.setFixedWidth(160);layout.addWidget(self.categories)
        self.category_pages=QStackedWidget();layout.addWidget(self.category_pages,1)
        # Existing persisted controls remain available to presets and the option
        # collector. Only the product-facing subset is placed in visible layouts.
        for name in ('path_edit','format_sort_edit','sub_langs_edit','ffmpeg_path_edit','browser_profile_edit',
                     'cookie_file_edit','username_edit','password_edit','outtmpl_edit','proxy_edit','geo_proxy_edit',
                     'ratelimit_edit','archive_edit','playlist_items_edit','min_filesize_edit','max_filesize_edit',
                     'date_start_edit','date_end_edit','match_filter_edit'):
            widget=QLineEdit(self);widget.hide();setattr(self,name,widget)
        for name in ('password_edit','proxy_edit','geo_proxy_edit'):
            getattr(self,name).setEchoMode(QLineEdit.Password)
        choices={'language_combo':['en','zh'],'theme_combo':['system','light','dark'],
                 'format_combo':['','b','bv*+ba/b','bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]','bv*[height<=720]+ba/b[height<=720]','bv*[height<=1080]+ba/b[height<=1080]','bv','ba'],
                 'merge_format_combo':['','mp4','mkv','webm','avi'],
                 'audio_format_combo':['mp3','m4a','opus','flac','wav','best'],
                 'remux_combo':['','mp4','mkv','webm','avi','mov','flv'],'recode_combo':['','mp4','mkv','webm','avi','flv'],
                 'sub_format_combo':['best','vtt','srt','ass','lrc'],'convert_subs_combo':['','srt','vtt','ass','lrc'],
                 'convert_thumb_combo':['','jpg','png','webp'],'cookie_browser_combo':['None','chrome','firefox','edge'],
                 'ext_downloader_combo':['','aria2c','axel','curl'],'default_quality_combo':['best']}
        for name,values in choices.items():
            widget=QComboBox(self);widget.hide()
            for value in values:
                if name=='format_combo':widget.addItem(value)
                else:widget.addItem(value,value)
            setattr(self,name,widget)
        self.format_combo.setEditable(True)
        for name in ('cb_subtitles','cb_auto_subs','cb_embed_subs','cb_embed_metadata','cb_embed_chapters',
                     'cb_embed_thumbnail','cb_extract_audio','cb_keep_video','cb_netrc','cb_noplaylist','debug_logging'):
            widget=QCheckBox(self);widget.hide();setattr(self,name,widget)
        self.cb_embed_metadata.setChecked(True);self.cb_embed_chapters.setChecked(True)
        for name,low,high,value in [('workers_spin',1,10,3),('retries_spin',0,100,10),
                                    ('fragment_retries_spin',0,100,10),('fragment_spin',1,16,1),
                                    ('sleep_spin',0,60,0),('max_downloads_spin',0,9999,0)]:
            widget=QSpinBox(self);widget.hide();widget.setRange(low,high);widget.setValue(value);setattr(self,name,widget)
        self.audio_quality_slider=QSlider(Qt.Horizontal,self);self.audio_quality_slider.hide()
        self.audio_quality_slider.setRange(0,10);self.audio_quality_slider.setValue(5)
        self.audio_quality_label=QLabel('5',self);self.audio_quality_label.hide()
        self.sections={}
        def section(key,expanded=False):
            result=CollapsibleSection('',expanded=True);bind(result._toggle_btn,key);result._toggle_btn.hide()
            self.sections[key]=result;self.categories.addItem(tr(key));page=QWidget();page_layout=QVBoxLayout(page);page_layout.setContentsMargins(0,0,0,0);heading=bind(QLabel(),key);heading.setProperty('role','section');page_layout.addWidget(heading);page_layout.addWidget(result);page_layout.addStretch();self.category_pages.addWidget(page);return result
        def form(section):
            result=QFormLayout();result.setRowWrapPolicy(QFormLayout.WrapLongRows)
            result.setHorizontalSpacing(16);result.setVerticalSpacing(16);section.add_layout(result);return result
        def row(form,key,widget,tooltip=None):
            label=bind(QLabel(),key);label.setWordWrap(True)
            if key in ('theme','language'):
                labels=QWidget();texts=QVBoxLayout(labels);texts.setContentsMargins(0,0,0,0);texts.setSpacing(4);texts.addWidget(label);description=bind(QLabel(),key+'_description');description.setProperty('role','secondary');description.setWordWrap(True);texts.addWidget(description);label=labels
            form.addRow(label,widget);widget.show()
            if tooltip:bind(widget,tooltip,'setToolTip')
        def note(section,key):
            label=InfoBanner(key,'warning') if key=='cookies_security' else bind(QLabel(),key);label.setWordWrap(True);label.setProperty('role','banner' if key=='cookies_security' else 'secondary');section.add_widget(label)
        def browse(form,key,edit,callback,tooltip=None):
            controls=QWidget();h=QHBoxLayout(controls);h.setContentsMargins(0,0,0,0);edit.show();h.addWidget(edit,1)
            button=bind(QPushButton(),'browse' if key=='default_folder' else 'browse_file');button.clicked.connect(callback);h.addWidget(button)
            row(form,key,controls)
            if tooltip:bind(edit,tooltip,'setToolTip')
        general=section('general',True);f=form(general)
        row(f,'language',self.language_combo);row(f,'theme',self.theme_combo)
        browse(f,'default_folder',self.path_edit,self._browse_path)
        downloads=section('downloads');f=form(downloads)
        row(f,'default_quality',self.default_quality_combo);row(f,'default_container',self.merge_format_combo,'tooltip.container')
        row(f,'audio_only',self.cb_extract_audio);row(f,'audio_format',self.audio_format_combo)
        row(f,'workers',self.workers_spin)
        cookies=section('cookies');note(cookies,'cookies_hint');note(cookies,'cookies_security');f=form(cookies)
        browse(f,'cookies_file',self.cookie_file_edit,self._browse_cookie_file,'tooltip.cookies')
        self.cookie_file_status=QLabel();f.addRow(self.cookie_file_status)
        row(f,'browser_cookies',self.cookie_browser_combo)
        self.cookie_support=QLabel();self.cookie_support.setWordWrap(True);f.addRow(self.cookie_support)
        self.cookie_badge=InfoChip();f.addRow(self.cookie_badge)
        self.file_badge=bind(InfoChip(),'recommended');f.itemAt(0,QFormLayout.FieldRole).widget().layout().addWidget(self.file_badge)
        self.cookie_support.hide()
        row(f,'browser_profile',self.browser_profile_edit)
        bind(self.browser_profile_edit,'browser_default','setPlaceholderText')
        self.cookie_file_edit.textChanged.connect(self._cookie_status)
        self.cookie_browser_combo.currentIndexChanged.connect(self._cookie_status)
        proxy=section('proxy');note(proxy,'proxy_hint');f=form(proxy)
        row(f,'proxy_url',self.proxy_edit,'tooltip.proxy');row(f,'proxy_geo',self.geo_proxy_edit,'tooltip.proxy')
        self.proxy_edit.setPlaceholderText('http://127.0.0.1:7890')
        self.runtime_section=section('runtime');note(self.runtime_section,'bundled_tools');f=form(self.runtime_section)
        browse(f,'ffmpeg_path',self.ffmpeg_path_edit,self._browse_ffmpeg)
        advanced=section('advanced');note(advanced,'advanced_description');note(advanced,'custom_warning');f=form(advanced)
        row(f,'format_expression',self.format_combo,'custom_warning')
        row(f,'fragments',self.fragment_spin,'tooltip.fragments');row(f,'retries',self.retries_spin)
        row(f,'fragment_retries',self.fragment_retries_spin);row(f,'filename_template',self.outtmpl_edit)
        self.outtmpl_edit.setPlaceholderText('%(title)s [%(id)s].%(ext)s')
        row(f,'debug_logging',self.debug_logging,'debug_hint')
        about=section('about')
        self.about_summary=QLabel(PRODUCT+' · '+VERSION);about.add_widget(self.about_summary)
        note(about,'rc');note(about,'about_description')
        self.about_button=bind(QPushButton(),'about');about.add_widget(self.about_button)
        self.help_button=bind(QPushButton(),'help');about.add_widget(self.help_button)
        self.licenses_button=bind(QPushButton(),'third_party');about.add_widget(self.licenses_button)
        self.categories.currentRowChanged.connect(self.category_pages.setCurrentIndex);self.categories.setCurrentRow(0);self.retranslate()

    def _cookie_status(self,*_):
        bind(self.cookie_file_status,'configured' if self.cookie_file_edit.text() else 'not_configured')
        browser=self.cookie_browser_combo.currentData()
        bind(self.cookie_support,'browser.'+('none' if browser=='None' else browser))
        bind(self.cookie_badge,'experimental' if browser in ('chrome','edge') else 'best_effort');self.cookie_badge.setProperty('tone','warning' if browser in ('chrome','edge') else 'neutral');refresh(self.cookie_badge);self.cookie_badge.setVisible(browser!='None')

    def retranslate(self):
        for index,key in enumerate(self.sections):self.categories.item(index).setText(tr(key))
        combo_labels(self.language_combo,[None,None])
        self.language_combo.setItemText(0,'English');self.language_combo.setItemText(1,'简体中文')
        combo_labels(self.theme_combo,['theme.system','theme.light','theme.dark'])
        combo_labels(self.default_quality_combo,['best_quality'])
        combo_labels(self.merge_format_combo,['auto',None,None,None,None])
        combo_labels(self.audio_format_combo,[None,None,None,None,None,'best_audio'])
        for combo in (self.merge_format_combo,self.audio_format_combo):
            for index in range(combo.count()):
                value=combo.itemData(index)
                if value and value!='best':combo.setItemText(index,{'webm':'WebM','opus':'Opus'}.get(value,value.upper()))
        combo_labels(self.cookie_browser_combo,['browser.none',None,None,None])
        for index,name in enumerate(('Chrome','Firefox','Edge'),1):self.cookie_browser_combo.setItemText(index,name)
        bind(self.format_combo.lineEdit(),'best_quality','setPlaceholderText')
        self._cookie_status()

    # ── Browse helpers ──────────────────────────────────────────────────────

    def _browse_path(self):
        path = QFileDialog.getExistingDirectory(self, tr('default_folder'))
        if path:
            self.path_edit.setText(path)

    def _browse_ffmpeg(self):
        path, _ = QFileDialog.getOpenFileName(self, tr('ffmpeg_path'))
        if path:
            self.ffmpeg_path_edit.setText(path)

    def _browse_cookie_file(self):
        path, _ = QFileDialog.getOpenFileName(self, tr('cookies_file'), "", tr('text_files'))
        if path:
            self.cookie_file_edit.setText(path)

    def _browse_archive(self):
        path, _ = QFileDialog.getSaveFileName(self, tr('filename_template'), "", tr('text_files'))
        if path:
            self.archive_edit.setText(path)

    # ── Collect / Apply ─────────────────────────────────────────────────────

    def collect_opts(self) -> dict:
        """Return user input; core.option_builder owns yt-dlp mapping."""
        return self.collect_settings_dict()

    def collect_settings_dict(self) -> dict:
        """Collect current UI state as app_settings keys (for persistence)."""
        s: dict = {}
        s['theme'] = self.theme_combo.currentData(); s['language'] = self.language_combo.currentData()
        s['browser_profile'] = self.browser_profile_edit.text().strip()
        s['retries'] = self.retries_spin.value(); s['fragment_retries'] = self.fragment_retries_spin.value()
        s["format"] = self.format_combo.currentText().strip()
        if self.format_combo.currentData() and self.format_combo.currentText() == self.format_combo.itemText(self.format_combo.currentIndex()):
            s['quality_target'] = self.format_combo.currentData()
            s['quality_label'] = s['format']
            s['format'] = ''
        s["format_sort"] = self.format_sort_edit.text().strip()
        s["merge_output_format"] = self.merge_format_combo.currentData()
        s["audio_format"] = self.audio_format_combo.currentData()
        s["audio_quality"] = self.audio_quality_slider.value()
        s["remux_video"] = self.remux_combo.currentText()
        s["recode_video"] = self.recode_combo.currentText()
        s["writesubtitles"] = self.cb_subtitles.isChecked()
        s["write_auto_subs"] = self.cb_auto_subs.isChecked()
        s["subtitleslangs"] = self.sub_langs_edit.text().strip()
        s["sub_format"] = self.sub_format_combo.currentText()
        s["convert_subs"] = self.convert_subs_combo.currentText()
        s["embed_subs"] = self.cb_embed_subs.isChecked()
        s["embed_metadata"] = self.cb_embed_metadata.isChecked()
        s["embed_chapters"] = self.cb_embed_chapters.isChecked()
        s["embedthumbnail"] = self.cb_embed_thumbnail.isChecked()
        s["extract_audio"] = self.cb_extract_audio.isChecked()
        s["keep_video"] = self.cb_keep_video.isChecked()
        s["split_chapters"] = False
        s["convert_thumbnails"] = self.convert_thumb_combo.currentText()
        s["sponsorblock_mark"] = ""
        s["sponsorblock_remove"] = ""
        s["ffmpeg_location"] = self.ffmpeg_path_edit.text().strip()
        s["cookiesfrombrowser"] = self.cookie_browser_combo.currentData()
        if s['cookiesfrombrowser'] != 'None' and s['browser_profile']:
            s['cookiesfrombrowser'] = (s['cookiesfrombrowser'], s['browser_profile'])
        s["cookiefile"] = self.cookie_file_edit.text().strip()
        s["username"] = self.username_edit.text().strip()
        s["password"] = self.password_edit.text()
        s["netrc"] = self.cb_netrc.isChecked()
        s["download_path"] = self.path_edit.text().strip()
        s["outtmpl"] = self.outtmpl_edit.text().strip()
        s["proxy"] = self.proxy_edit.text().strip()
        s["geo_verification_proxy"] = self.geo_proxy_edit.text().strip()
        s["ratelimit"] = self.ratelimit_edit.text().strip()
        s["max_workers"] = self.workers_spin.value()
        s["concurrent_fragment_downloads"] = self.fragment_spin.value()
        s["external_downloader"] = self.ext_downloader_combo.currentText()
        s["sleep_interval"] = self.sleep_spin.value()
        s["download_archive"] = self.archive_edit.text().strip()
        s["noplaylist"] = self.cb_noplaylist.isChecked()
        s["playlist_items"] = self.playlist_items_edit.text().strip()
        s["min_filesize"] = self.min_filesize_edit.text().strip()
        s["max_filesize"] = self.max_filesize_edit.text().strip()
        s["date_range_start"] = self.date_start_edit.text().strip()
        s["date_range_end"] = self.date_end_edit.text().strip()
        s["match_filter"] = self.match_filter_edit.text().strip()
        s["max_downloads"] = self.max_downloads_spin.value()
        return s

    def apply_settings(self, settings: dict):
        """Populate UI from a settings dict."""
        def _set_combo(combo, val):
            idx = combo.findData(val)
            if idx < 0: idx = combo.findText(val)
            if idx >= 0:
                combo.setCurrentIndex(idx)
            elif combo.isEditable():
                combo.setEditText(val)

        _set_combo(self.theme_combo, settings.get('theme','light'))
        _set_combo(self.language_combo, settings.get('language','en'))
        self.debug_logging.setChecked(settings.get('debug_logging',False))
        self.browser_profile_edit.setText(settings.get('browser_profile',''))
        self.retries_spin.setValue(settings.get('retries',10)); self.fragment_retries_spin.setValue(settings.get('fragment_retries',10))
        _set_combo(self.format_combo, settings.get("format", ""))
        if settings.get('quality_target'):
            self.format_combo.addItem(settings.get('quality_label', 'Selected source quality'), settings['quality_target'])
            self.format_combo.setCurrentIndex(self.format_combo.count() - 1)
        self.format_sort_edit.setText(settings.get("format_sort", ""))
        _set_combo(self.merge_format_combo, settings.get("merge_output_format", ""))
        _set_combo(self.audio_format_combo, settings.get("audio_format", "mp3"))
        self.audio_quality_slider.setValue(settings.get("audio_quality", 5))
        _set_combo(self.remux_combo, settings.get("remux_video", ""))
        _set_combo(self.recode_combo, settings.get("recode_video", ""))
        self.cb_subtitles.setChecked(settings.get("writesubtitles", False))
        self.cb_auto_subs.setChecked(settings.get("write_auto_subs", False))
        self.sub_langs_edit.setText(settings.get("subtitleslangs", ""))
        _set_combo(self.sub_format_combo, settings.get("sub_format", "best"))
        _set_combo(self.convert_subs_combo, settings.get("convert_subs", ""))
        self.cb_embed_subs.setChecked(settings.get("embed_subs", False))
        self.cb_embed_metadata.setChecked(settings.get("embed_metadata", True))
        self.cb_embed_chapters.setChecked(settings.get("embed_chapters", True))
        self.cb_embed_thumbnail.setChecked(settings.get("embedthumbnail", False))
        self.cb_extract_audio.setChecked(settings.get("extract_audio", False))
        self.cb_keep_video.setChecked(settings.get("keep_video", False))
        _set_combo(self.convert_thumb_combo, settings.get("convert_thumbnails", ""))
        self.ffmpeg_path_edit.setText(settings.get("ffmpeg_location", ""))
        browser = settings.get('cookiesfrombrowser','None')
        if isinstance(browser, (list,tuple)):
            self.browser_profile_edit.setText(browser[1] or '' if len(browser)>1 else '')
            browser = browser[0]
        _set_combo(self.cookie_browser_combo, browser)
        self.cookie_file_edit.setText(settings.get("cookiefile", ""))
        self.username_edit.setText(settings.get("username", ""))
        self.password_edit.setText(settings.get("password", ""))
        self.cb_netrc.setChecked(settings.get("netrc", False))
        self.path_edit.setText(settings.get("download_path", ""))
        self.outtmpl_edit.setText(settings.get("outtmpl", ""))
        self.proxy_edit.setText(settings.get("proxy", ""))
        self.geo_proxy_edit.setText(settings.get("geo_verification_proxy", ""))
        self.ratelimit_edit.setText(settings.get("ratelimit", ""))
        self.workers_spin.setValue(settings.get("max_workers", 3))
        self.fragment_spin.setValue(settings.get("concurrent_fragment_downloads", 1))
        _set_combo(self.ext_downloader_combo, settings.get("external_downloader", ""))
        self.sleep_spin.setValue(settings.get("sleep_interval", 0))
        self.archive_edit.setText(settings.get("download_archive", ""))
        self.cb_noplaylist.setChecked(settings.get("noplaylist", False))
        self.playlist_items_edit.setText(settings.get("playlist_items", ""))
        self.min_filesize_edit.setText(settings.get("min_filesize", ""))
        self.max_filesize_edit.setText(settings.get("max_filesize", ""))
        self.date_start_edit.setText(settings.get("date_range_start", ""))
        self.date_end_edit.setText(settings.get("date_range_end", ""))
        self.match_filter_edit.setText(settings.get("match_filter", ""))
        self.max_downloads_spin.setValue(settings.get("max_downloads", 0))

    def apply_preset(self, preset: dict):
        """Apply a preset dict on top of current settings."""
        from services.settings_service import merge_preset
        settings = merge_preset(self.collect_settings_dict(), preset)
        self.apply_settings(settings)
