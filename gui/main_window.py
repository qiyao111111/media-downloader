"""Five desktop pages coordinated through Manager and Qt record signals."""
import logging
from pathlib import Path
from PySide6.QtCore import Qt,Slot
from PySide6.QtWidgets import QApplication,QHBoxLayout,QMainWindow,QMessageBox,QPushButton,QVBoxLayout,QWidget,QListWidget,QStackedWidget,QScrollArea,QLabel
from services.settings_service import SettingsService as AppSettings
from services.history_service import HistoryService as DownloadHistory
from core.manager import DownloadManager
from core.credentials import redact
from models.download import TaskStatus
from app.version import VERSION, PRODUCT
from gui.bridge import DownloadBridge
from gui.theme_manager import apply_theme
from gui.widgets.presentation import page_layout,page_header,line_icon,RuntimeStatusRow
from gui.design_tokens import SIDEBAR
from PySide6.QtCore import QSize
from gui.downloader_page import DownloaderPage
from gui.history_page import HistoryPage
from gui.error_mapper import show_error,error_text,error_key
from gui.product_dialogs import ProductDialog,WelcomeDialog,open_licenses
from gui.widgets.collapsible_section import CollapsibleSection
from i18n import tr,bind,set_language,translate_tree,runtime_label
from gui.widgets.format_preview import FormatPreviewDialog  # legacy extension compatibility
from gui.widgets.log_viewer import LogViewerWidget
from gui.widgets.settings_dialog import SettingsDialog
from gui.widgets.task_table import TaskTableWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__();self.setWindowTitle(PRODUCT)
        self._settings=AppSettings();set_language(self._settings.get('language','en'));self._health_data=None;self._tools_data=None;self._history=DownloadHistory();self._bridge=DownloadBridge(self)
        self._manager=DownloadManager(max_workers=self._settings.get('max_workers',3),on_event=self._bridge.on_event,
                                      on_error=self._bridge.on_error)
        self._preview_generation=0;self._submitted_urls=set();self._retried_ids=set();self._records={};self._closing=False
        self._settings_dialog=SettingsDialog(self)
        screen=QApplication.primaryScreen().availableGeometry()
        self.resize(min(self._settings.get('window_width',1180),screen.width()),min(self._settings.get('window_height',760),screen.height()))
        self.setMinimumSize(720,440)
        self._init_ui();self._connect_signals();self._load_settings();self._load_history();self._update_ffmpeg_status();self._url_input._text_edit.setFocus()

    def _init_ui(self):
        central=QWidget();central.setObjectName('shell');self.setCentralWidget(central);root=QHBoxLayout(central);root.setContentsMargins(12,12,12,12);root.setSpacing(0)
        sidebar=QWidget();sidebar.setFixedWidth(SIDEBAR);side=QVBoxLayout(sidebar);side.setContentsMargins(8,12,8,12);side.setSpacing(16)
        product=QLabel(PRODUCT);side.addWidget(product)
        self.navigation=QListWidget();self.navigation.addItems([tr(k) for k in ('nav.download','nav.queue','nav.history','nav.settings','nav.logs')])
        self.navigation.setIconSize(QSize(20,20))
        for index,name in enumerate(('download','queue','history','settings','logs')):self.navigation.item(index).setIcon(line_icon(name))
        side.addWidget(self.navigation,1);about=QPushButton(VERSION);about.clicked.connect(self._show_about);side.addWidget(about);root.addWidget(sidebar)
        self.pages=QStackedWidget();self.pages.setMaximumWidth(1440);root.addWidget(self.pages,1)
        self._downloader=DownloaderPage();scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setWidget(self._downloader)
        download_page=QWidget();download_layout=QVBoxLayout(download_page);download_layout.setContentsMargins(0,0,24,20);download_layout.addWidget(scroll,1)
        self._downloader.layout().removeWidget(self._downloader.download);download_layout.addWidget(self._downloader.download,0,Qt.AlignRight)
        self.pages.addWidget(download_page)
        self._url_input=self._downloader.urls;self._btn_download=self._downloader.download
        self._task_table=TaskTableWidget();queue=QWidget();q=page_layout(queue);page_header(q,"nav.queue")
        self._btn_cancel_all=bind(QPushButton(),'cancel_all');self._btn_cancel_all.setObjectName('btn_cancel_all');self._btn_cancel_all.setEnabled(False);q.addWidget(self._btn_cancel_all,0,Qt.AlignRight);q.addWidget(self._task_table,1);self.pages.addWidget(queue)
        self._task_table.set_retry_callback(self._retry_url);self._task_table.set_delete_callback(self._delete_task)
        self._history_page=HistoryPage();self.pages.addWidget(self._history_page)
        settings=QWidget();s=page_layout(settings);page_header(s,"nav.settings");self._settings_panel=self._settings_dialog.settings_panel
        # Transfer ownership explicitly; two scroll areas must not retain one widget.
        self._settings_dialog.findChild(QScrollArea).takeWidget()
        self._tools_label=QLabel();self._tools_label.setWordWrap(True)
        tool_details=CollapsibleSection('');bind(tool_details._toggle_btn,'advanced_details');tool_details.add_widget(self._tools_label)
        self._settings_panel.runtime_section.add_widget(tool_details)
        area=QScrollArea();area.setWidgetResizable(True);area.setWidget(self._settings_panel);s.addWidget(area,1)
        self._btn_save_settings=bind(QPushButton(),'save');self._btn_save_settings.setObjectName('btn_save');s.addWidget(self._btn_save_settings,0,Qt.AlignRight)
        self.runtime_rows=QWidget();self.runtime_rows_layout=QVBoxLayout(self.runtime_rows);self.runtime_rows_layout.setContentsMargins(0,0,0,0);self._settings_panel.runtime_section.add_widget(self.runtime_rows)
        self._runtime_label=bind(QLabel(),'checking');self._runtime_label.setWordWrap(True);tool_details.add_widget(self._runtime_label)
        diagnostics=bind(QPushButton(),'diagnostics');diagnostics.clicked.connect(self._run_diagnostics);self._settings_panel.runtime_section.add_widget(diagnostics)
        copy=bind(QPushButton(),'copy_diagnostics');copy.clicked.connect(lambda:QApplication.clipboard().setText(self._runtime_label.text()+'\n'+self._tools_label.text()));self._settings_panel.runtime_section.add_widget(copy)
        self._update_button=bind(QPushButton(),'check_update');self._update_button.clicked.connect(self._check_update);self._settings_panel.runtime_section.add_widget(self._update_button)
        self.pages.addWidget(settings)
        self._log_viewer=LogViewerWidget();logs=QWidget();logs_layout=page_layout(logs);page_header(logs_layout,'nav.logs');logs_layout.addWidget(self._log_viewer,1);self.pages.addWidget(logs)
        self.navigation.currentRowChanged.connect(self.pages.setCurrentIndex);self.navigation.setCurrentRow(0)
        view=self.menuBar().addMenu('');bind(view,'view','setTitle');self._theme_action=bind(view.addAction(''),'toggle_theme');self._theme_action.triggered.connect(self._toggle_theme)
        action=bind(view.addAction(''),'clear_history');action.triggered.connect(self._confirm_clear_history)
        help_menu=self.menuBar().addMenu('');bind(help_menu,'help','setTitle')
        bind(help_menu.addAction(''),'about').triggered.connect(self._show_about)
        bind(help_menu.addAction(''),'help').triggered.connect(self._show_help)
        self._settings_panel.about_button.clicked.connect(self._show_about)
        self._settings_panel.help_button.clicked.connect(self._show_help)
        self._settings_panel.licenses_button.clicked.connect(lambda:open_licenses(self))
        self._btn_settings=bind(QPushButton(),'nav.settings');self._btn_settings.clicked.connect(self._on_open_settings)

    def _connect_signals(self):
        self._btn_download.clicked.connect(self._on_download);self._btn_cancel_all.clicked.connect(self._manager.cancel_all)
        self._url_input.format_requested.connect(self._on_list_formats)
        self._url_input._text_edit.textChanged.connect(self._url_changed)
        self._downloader.selection_changed.connect(self._selection_changed)
        self._bridge.info_extracted.connect(self._on_info_extracted);self._bridge.preview_failed.connect(self._on_info_error)
        self._bridge.task_added.connect(self._task_added)
        self._bridge.task_updated.connect(self._task_updated);self._bridge.task_progress.connect(self._task_progress)
        self._bridge.typed_error.connect(self._on_error);self._bridge.tools_ready.connect(self._tools_ready)
        self._bridge.health_ready.connect(self._health_ready);self._bridge.update_ready.connect(self._update_ready)
        self._btn_save_settings.clicked.connect(self._save_settings)
        self._settings_panel.language_combo.currentIndexChanged.connect(lambda:self._retranslate(self._settings_panel.language_combo.currentData()))
        self._history_page.retry_requested.connect(self._retry_url);self._history_page.remove_requested.connect(self._remove_history)
        # Credential changes invalidate an analyzed context before another download.
        for edit in (self._settings_panel.cookie_file_edit,self._settings_panel.browser_profile_edit,self._settings_panel.proxy_edit,self._settings_panel.geo_proxy_edit,self._settings_panel.username_edit,self._settings_panel.password_edit):
            edit.textChanged.connect(self._auth_changed)
        self._settings_panel.cookie_browser_combo.currentTextChanged.connect(self._auth_changed)
        self._settings_panel.cb_netrc.toggled.connect(self._auth_changed)

    def _load_settings(self):
        self._settings_panel.apply_settings(self._settings.to_dict())
        self._log_viewer._handler.setLevel(logging.DEBUG if self._settings.get('debug_logging') else logging.INFO)
        self._downloader.path.setText(self._settings.get('download_path',''))
        self._sync_download_controls()
        self._apply_navigation_language()

    def _sync_download_controls(self):
        p=self._settings_panel;d=self._downloader
        for control in (d.container,d.audio_only,d.audio_format):control.blockSignals(True)
        d.container.setCurrentIndex(max(0,d.container.findData(p.merge_format_combo.currentData())))
        d.audio_only.setChecked(p.cb_extract_audio.isChecked())
        d.audio_format.setCurrentIndex(max(0,d.audio_format.findData(p.audio_format_combo.currentData() if p.cb_extract_audio.isChecked() else 'best')))
        for control in (d.container,d.audio_only,d.audio_format):control.blockSignals(False)

    def _apply_navigation_language(self):
        self._retranslate(self._settings.get('language','en'))

    def _retranslate(self,language):
        set_language(language);translate_tree(self)
        for i,key in enumerate(('nav.download','nav.queue','nav.history','nav.settings','nav.logs')):self.navigation.item(i).setText(tr(key))
        for page in (self._settings_panel,self._downloader,self._task_table,self._history_page,self._log_viewer):page.retranslate()
        if self._downloader.info:self._selection_changed()
        if self._health_data:self._health_ready(self._health_data)
        if self._tools_data:self._tools_ready(self._tools_data)

    def _show_about(self):
        self._product_dialog=ProductDialog(self);self._product_dialog.open()

    def _show_help(self):
        self._product_dialog=ProductDialog(self,help_mode=True);self._product_dialog.open()

    def show_welcome(self):
        if not self._settings.get('onboarding_complete',False):
            self._welcome_dialog=WelcomeDialog(self);self._welcome_dialog.open()

    def _confirm_clear_history(self):
        if QMessageBox.question(self,tr('clear_history'),tr('confirm_clear'),QMessageBox.Yes|QMessageBox.No,QMessageBox.No)==QMessageBox.Yes:self._clear_history()


    def _save_settings(self):
        try:
            self._manager.build_options(self._settings_panel.collect_opts())
            self._manager.configure_workers(self._settings_panel.workers_spin.value())
            s=self._settings_panel.collect_settings_dict()
            browser=s.get('cookiesfrombrowser')
            if isinstance(browser,(tuple,list)):s['cookiesfrombrowser']=browser[0]
            s.update(window_width=self.width(),window_height=self.height())
            self._settings.update_from(s);self._settings.save()
            apply_theme(QApplication.instance(),s['theme']);self._apply_navigation_language()
            self._downloader.path.setText(s['download_path']);self._sync_download_controls()
            self._auth_changed();self._log_viewer._handler.setLevel(logging.DEBUG if s.get('debug_logging') else logging.INFO);bind(self.statusBar(),'settings_saved','showMessage');self._update_ffmpeg_status()
            return True
        except (ValueError,TypeError,OSError) as exc:
            show_error(self,exc,'error.invalid_settings');return False

    def _load_history(self):
        for r in self._history.list_records():
            if not TaskStatus.normalize(r['status']).terminal:
                self._history.update_record(r['task_id'],status='cancelled',error='Application previously exited before completion')
        self._history_page.render(self._history.list_records())

    def _update_ffmpeg_status(self):
        self._manager.inspect_tools(self._settings_panel.ffmpeg_path_edit.text(),self._bridge.tools_ready.emit)
        self._run_diagnostics()

    def _run_diagnostics(self):
        self._manager.runtime_health(self._settings_panel.ffmpeg_path_edit.text(),self._downloader.path.text(),self._bridge.health_ready.emit)

    @Slot(dict)
    def _health_ready(self,data):
        if self._closing:return
        self._health_data=data;self._runtime_label.setProperty('i18n_bindings',{})
        app=data.get('application',{});lines=[tr('app_version')+': '+app.get('version',VERSION),tr('windows_version')+': '+app.get('os','--'),tr('architecture')+': '+app.get('architecture','--')]
        labels={'quickjs':tr('js_runtime')+' · QuickJS','config':tr('config_path'),'download':tr('download_path'),'temp':tr('temp_path')}
        lines.extend(f'{labels.get(name,name)}: {runtime_label(row["status"])} · {row.get("version",row.get("path","--")) if row["status"]!="NOT_INSTALLED" else "--"}' for name,row in data.items() if name!='application')
        self._runtime_label.setText('\n'.join(lines))
        self._runtime_label.setToolTip('\n'.join(f'{name}: {row}' for name,row in data.items()))
        while self.runtime_rows_layout.count():
            item=self.runtime_rows_layout.takeAt(0);item.widget().hide();item.widget().deleteLater()
        for name in ('yt-dlp','ffmpeg','ffprobe','quickjs'):
            row=data.get(name)
            if row:self.runtime_rows_layout.addWidget(RuntimeStatusRow(name,row.get('version','--'),row['status']))

    def _check_update(self):
        self._update_button.setEnabled(False);self._manager.check_runtime_update(self._bridge.update_ready.emit)

    @Slot(dict)
    def _update_ready(self,data):
        if self._closing:return
        self._update_button.setEnabled(True)
        if data.get('error'):bind(self.statusBar(),error_key(data['error']),'showMessage')
        else:bind(self.statusBar(),'update_check','showMessage',result=str(data.get('installed','--'))+' → '+str(data.get('latest','--')))
        self._log_viewer.append(redact(data))

    @Slot(dict)
    def _tools_ready(self,data):
        if self._closing:return
        self._tools_data=data;self._tools_label.setText('\n'.join(f'{tool}: {data.get(tool) or "--"}\n{data.get(tool+"_version") or "--"}' for tool in ('ffmpeg','ffprobe')))

    def _url_changed(self):
        self._preview_generation+=1;self._downloader.update_buttons()

    def _auth_changed(self):
        self._preview_generation+=1
        if hasattr(self,'_downloader'):self._downloader.invalidate()

    def _build_ydl_opts(self):
        return self._manager.build_options(self._settings_panel.collect_opts())

    def _on_list_formats(self):
        d=self._downloader;url=self._url_input.get_first_url()
        if not url or d.analyzing:return
        try:opts=self._build_ydl_opts()
        except (ValueError,TypeError) as exc:show_error(self,exc,'error.invalid_settings');return
        self._preview_generation+=1;generation=self._preview_generation
        d.info=None;d.selection=None;d.analyzing=True;bind(d.message,'analyzing');d.update_buttons()
        self._submitted_urls.difference_update(self._url_input.get_urls());self._sync_download_controls()
        def ready(link,info):self._bridge.on_info_result(link,{**info,'_ui_request':generation})
        def failed(link,error):self._bridge.preview_failed.emit(link,(generation,error))
        self._manager.extract_info(url,on_result=ready,on_error=failed,ydl_opts=opts)

    @Slot(str,dict)
    def _on_info_extracted(self,url,info):
        if self._closing:return
        d=self._downloader;d.analyzing=False
        if info.get('_ui_request',self._preview_generation)!=self._preview_generation or url!=self._url_input.get_first_url():d.update_buttons();return
        try:
            playlist=info.get('_type')=='playlist'
            best=None
            if not playlist:
                try:best=self._manager.selection(info)
                except Exception:
                    if not self._settings_panel.format_combo.currentText():raise
            d.custom_mode=bool(self._settings_panel.format_combo.currentText())
            d.set_info(url,info,self._manager.quality_options(info),best,self._manager.preview_formats(info))
            self._selection_changed()
        except Exception as exc:self._on_info_error(url,exc)

    @Slot(str,object)
    def _on_info_error(self,url,error):
        if self._closing:return
        d=self._downloader;d.analyzing=False
        if isinstance(error,tuple):
            generation,error=error
            if generation!=self._preview_generation:d.update_buttons();return
        d.info=None;d.selection=None;bind(d.message,'error.analyze_hint');d.set_error(True);d.update_buttons()
        bind(d.message,'analyze_error_inline',reason=error_text(error)[0])
        show_error(self,error,'error.analyze');self._log_viewer.append(redact(error))

    def _inputs(self):
        inputs=self._settings_panel.collect_opts();d=self._downloader
        inputs['download_path']=d.path.text();inputs['merge_output_format']=d.container.currentData()
        if d.audio_only.isChecked():
            inputs['format']='';inputs.pop('quality_target',None)
            inputs['extract_audio']=d.audio_format.currentData()!='best';inputs['audio_format']=d.audio_format.currentData()
        else:inputs['extract_audio']=False
        return inputs

    def _selection_changed(self):
        d=self._downloader
        if not d.info:d.update_buttons();return
        try:
            target='audio' if d.audio_only.isChecked() else d.quality.currentData()
            custom=bool(self._inputs().get('format'));d.custom_mode=custom
            d.selection=None if d.info.get('_type')=='playlist' or custom else self._manager.selection(d.info,target)
            if d.selection:
                s=d.selection;v=s.video or s.muxed;a=s.audio or s.muxed
                d.details_text.setPlainText('\n'.join([tr('video_id')+': '+(v.format_id if v else '--'),tr('audio_id')+': '+(a.format_id if a else '--'),tr('video_codec')+': '+(v.label if v else '--'),tr('audio_codec')+': '+(a.audio_codec if a else '--'),tr('estimated')+': '+str(s.estimated_size or '--'),tr('recommended_container',container=s.final_container)]))
                container=d.container.currentData()
                d.message.setProperty('i18n_bindings',{})
                d.message.setText((tr('container_override') if container and container!=s.final_container else tr('recommended_container',container=s.final_container))+ (' '+tr('codec_warning' if target=='best' else 'codec_compatibility') if (v and v.video_codec_family in ('AV1','VP9')) or (a and a.audio_codec_family=='OPUS') else ''))
            elif custom:bind(d.message,'custom_warning')
            else:bind(d.message,'playlist_ready')
        except Exception as exc:
            d.selection=None;d.message.setProperty('i18n_bindings',{});d.message.setText(error_text(exc)[0]);self._log_viewer.append(redact(exc))
        duplicate=bool(self._url_input.get_urls()) and all(url in self._submitted_urls for url in self._url_input.get_urls())
        d.update_buttons(duplicate)

    def _on_download(self):
        d=self._downloader
        if not d.download.isEnabled() or not d.info:return
        try:
            inputs=self._inputs();target='audio' if d.audio_only.isChecked() else d.quality.currentData()
            options,selection=self._manager.prepare_download(inputs,d.info,target)
            for url in self._url_input.get_urls():
                if url in self._submitted_urls:continue
                if url==d.url:
                    self._manager.add_task(url,options,selection=selection,title=d.info.get('title') or '')
                else:
                    other=dict(inputs);other.pop('quality_target',None)
                    if not other.get('format'):other['quality_target']='audio' if d.audio_only.isChecked() else 'best'
                    self._manager.add_task(url,self._manager.build_options(other))
                self._submitted_urls.add(url)
            self._selection_changed();self.navigation.setCurrentRow(1)
        except Exception as exc:show_error(self,exc,'error.queue')

    @Slot(dict)
    def _task_added(self,record):
        if self._closing:return
        tid=record['id'];self._records[tid]=record
        self._task_table.add_task(tid,record['url'],self._manager.cancel_task);self._task_table.update_record(record)
        self._history.add(tid,record['url'],record.get('title',''));self._btn_cancel_all.setEnabled(True)

    @Slot(dict)
    def _task_progress(self,record):
        if self._closing:return
        self._records[record['id']]=record;self._task_table.update_record(record)

    @Slot(dict)
    def _task_updated(self,record):
        if self._closing:return
        self._task_progress(record);status=TaskStatus.normalize(record['status'])
        if status.terminal:
            self._history.update_record(record['id'],status=status.value,title=record.get('title',''),quality=record.get('quality',''),output_path=record.get('output_path',''),error=record.get('error',''))
            self._history_page.render(self._history.list_records())
            logging.getLogger('desktop').info('Task %s %s',record['id'],status.value)
        count=sum(not TaskStatus.normalize(r['status']).terminal for r in self._records.values())
        self._btn_cancel_all.setEnabled(bool(count));bind(self.statusBar(),'active_tasks','showMessage',count=count)

    @Slot(str,object)
    def _on_error(self,tid,error):
        if self._closing:return
        logging.getLogger('desktop').error('Task %s: %s',tid,redact(error));show_error(self,error,'error.download')

    def _retry_url(self,old_id,url):
        if old_id in self._retried_ids:return False
        self._retried_ids.add(old_id)
        try:
            old=self._manager.get_task(old_id)
            if old:self._manager.retry_task(old_id)
            else:self._manager.add_task(url,self._build_ydl_opts())
            return True
        except Exception as exc:
            self._retried_ids.discard(old_id);show_error(self,exc,'error.retry');return False

    def _delete_task(self,tid):
        task=self._manager.get_task(tid)
        if task and not task.status.terminal:self._manager.cancel_task(tid);return False
        self._manager.remove_task(tid);self._records.pop(tid,None);return True

    def _remove_history(self,tid):self._history.delete(tid);self._history_page.render(self._history.list_records())
    def _clear_history(self):self._history.clear_completed();self._history_page.render(self._history.list_records())
    def _on_open_settings(self):self.navigation.setCurrentRow(3)
    def _on_cancel_all(self):self._manager.cancel_all()
    def _on_preset_selected(self,preset):self._settings_panel.apply_preset(preset);self._sync_download_controls();self._auth_changed()
    def _toggle_theme(self):
        theme='dark' if self._settings_panel.theme_combo.currentData()=='light' else 'light'
        self._settings_panel.theme_combo.setCurrentIndex(self._settings_panel.theme_combo.findData(theme));apply_theme(QApplication.instance(),theme)

    def closeEvent(self,event):
        active=any(not t.status.terminal for t in self._manager.get_all_tasks())
        if active and QMessageBox.question(self,tr('active_title'),tr('active_exit'),QMessageBox.Yes|QMessageBox.No,QMessageBox.No)!=QMessageBox.Yes:
            event.ignore();return
        self._closing=True
        # Persist previously saved settings plus geometry; unsaved credentials are not written.
        self._settings.set('window_width',self.width());self._settings.set('window_height',self.height())
        try:self._settings.save()
        except OSError as exc:logging.getLogger('desktop').error('Settings save failed: %s',redact(exc))
        for r in self._history.list_records():
            if not TaskStatus.normalize(r['status']).terminal:self._history.update_record(r['task_id'],status='cancelled',error='Application closed while task was active')
        self._downloader.close_thumbnail();self._manager.shutdown(wait=False);self._log_viewer.detach();event.accept()
