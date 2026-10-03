"""Current-session queue, rendered exclusively from DownloadRecord snapshots."""
from pathlib import Path
from PySide6.QtCore import Qt,QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QGroupBox,QVBoxLayout,QTableWidget,QTableWidgetItem,QHeaderView,QProgressBar,QPushButton,QMenu,QApplication,QLabel
from gui.widgets.presentation import EmptyStateWidget,StatusBadge,refresh,TaskProgressBar
from models.download import TaskStatus
from core.credentials import redact
from i18n import tr,bind,status_label


def size(value):
    if value is None:return '--'
    value=value or 0
    for unit in ('B','KB','MB','GB','TB'):
        if value<1024 or unit=='TB': return f'{value:.1f} {unit}'
        value/=1024


def eta(value):
    if value is None:return '--'
    seconds=max(0,int(value));h,rest=divmod(seconds,3600);m,s=divmod(rest,60)
    return f'{h:02}:{m:02}:{s:02}' if h else f'{m:02}:{s:02}'


class TaskTableWidget(QGroupBox):
    def __init__(self,parent=None):
        super().__init__(parent);bind(self,'nav.queue','setTitle')
        layout=QVBoxLayout(self);self.empty=EmptyStateWidget('queue_empty','queue_description','queue');layout.addWidget(self.empty,1)
        self._table=QTableWidget(0,9);self._table.setHorizontalHeaderLabels(['ID','Title / URL','Status','Progress','Speed','ETA','Action','Quality','Downloaded / Total'])
        self._table.setEditTriggers(QTableWidget.NoEditTriggers);self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setTextElideMode(Qt.ElideRight);self._table.setColumnHidden(0,True)
        self._table.setWordWrap(False)
        self._table.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch)
        for visual,logical in enumerate((1,7,3,4,5,2,6,8,0)):self._table.horizontalHeader().moveSection(self._table.horizontalHeader().visualIndex(logical),visual)
        self._table.setShowGrid(False);self._table.verticalHeader().hide();self._table.verticalHeader().setDefaultSectionSize(56)
        for col,width in ((2,110),(3,110),(4,90),(5,70),(6,120),(7,180),(8,140)):self._table.setColumnWidth(col,width)
        self._table.setColumnHidden(7,True);layout.addWidget(self._table,1);self._table.hide()
        self._row_map={};self._urls={};self._cancel_callbacks={};self.records={};self._retry_callback=None;self._delete_callback=None
        self._table.setContextMenuPolicy(Qt.CustomContextMenu);self._table.customContextMenuRequested.connect(self._show_context_menu);self.retranslate()

    def resizeEvent(self,event):
        self._table.setColumnHidden(8,self.width()<1000)
        widths=(105,80,80,55,110) if self.width()<800 else (110,110,90,70,120)
        for column,width in zip((2,3,4,5,6),widths):self._table.setColumnWidth(column,width)
        super().resizeEvent(event)

    def retranslate(self):
        self._table.setHorizontalHeaderLabels([tr(k) for k in ('id','title','status','progress','speed','eta','actions','quality','downloaded_total')])
        for record in list(self.records.values()):self.update_record(record)

    def set_retry_callback(self,cb):self._retry_callback=cb
    def set_delete_callback(self,cb):self._delete_callback=cb

    def add_task(self,task_id,url,cancel_cb):
        if task_id in self._row_map:return
        row=self._table.rowCount();self._table.insertRow(row);self._row_map[task_id]=row
        self._urls[task_id]=url;self._cancel_callbacks[task_id]=cancel_cb
        for col in (0,1,2,4,5,7,8):self._table.setItem(row,col,QTableWidgetItem(task_id if col==0 else ''))
        self._table.item(row,2).setForeground(Qt.transparent)
        badge=StatusBadge();self._table.setCellWidget(row,2,badge)
        p=TaskProgressBar();p.setRange(0,100);self._table.setCellWidget(row,3,p)
        button=bind(QPushButton(),'cancel');self._table.setCellWidget(row,6,button);button.clicked.connect(lambda:self._action(task_id))
        self.empty.hide();self._table.show()
        self.update_record({'id':task_id,'url':url,'status':'queued'})

    def update_record(self,record):
        tid=record['id']
        if tid not in self._row_map:return
        data={**self.records.get(tid,{}),**record};self.records[tid]=data;row=self._row_map[tid]
        status=TaskStatus.normalize(data['status']);label=status_label(status.value)
        title=data.get('title') or data.get('url','')
        self._table.item(row,1).setText(title);self._table.item(row,1).setToolTip(title)
        self._table.item(row,2).setText(label);self._table.item(row,2).setToolTip(redact(data.get('error','')))
        quality=(data.get('quality') or '--').replace('H264','H.264').replace('OPUS','Opus')
        self._table.item(row,1).setText(title+'\n'+quality);self._table.item(row,1).setToolTip(title+'\n'+quality)
        self._table.item(row,7).setText(quality);self._table.item(row,7).setToolTip(quality)
        active=status==TaskStatus.DOWNLOADING
        self._table.item(row,4).setText(size(data['speed'])+'/s' if active and data.get('speed') is not None else '--')
        self._table.item(row,5).setText(eta(data.get('eta')) if active else '--')
        self._table.item(row,8).setText(size(data.get('downloaded_bytes'))+' / '+(size(data['total_bytes']) if data.get('total_bytes') else '--'))
        if status==TaskStatus.COMPLETED:
            try:final_size=size(Path(data['output_path']).stat().st_size)
            except (KeyError,OSError):final_size='--'
            self._table.item(row,8).setText(final_size)
        p=self._table.cellWidget(row,3)
        if status==TaskStatus.POSTPROCESSING or (active and not data.get('total_bytes')):p.setRange(0,0)
        else:
            p.setRange(0,100);p.setValue(100 if status==TaskStatus.COMPLETED else int(max(0,min(100,data.get('progress') or 0))))
        p.setProperty('state',status.value);refresh(p);self._table.cellWidget(row,2).set_status(status.value)
        p.setFormat(tr('merging') if status==TaskStatus.POSTPROCESSING else '%p%')
        p.setToolTip((tr('merging') if status==TaskStatus.POSTPROCESSING else tr('progress'))+' · '+self._table.item(row,8).text())
        button=self._table.cellWidget(row,6)
        bind(button,'open_folder' if status==TaskStatus.COMPLETED else 'retry' if status.terminal else 'cancel')
        button.setEnabled(status!=TaskStatus.COMPLETED or bool(data.get('output_path')))

    def update_status(self,tid,status):self.update_record({'id':tid,'status':status})

    def _action(self,tid):
        status=TaskStatus.normalize(self.records[tid]['status'])
        if status==TaskStatus.COMPLETED:self.open_folder(tid)
        elif status.terminal:self._on_retry(tid)
        else:self._on_cancel(tid)

    def _on_cancel(self,tid):
        cb=self._cancel_callbacks.get(tid)
        if cb:cb(tid)

    def _on_retry(self,tid):
        if not TaskStatus.normalize(self.records[tid]['status']).terminal:return
        button=self._table.cellWidget(self._row_map[tid],6);button.setEnabled(False)
        if self._retry_callback and self._retry_callback(tid,self._urls[tid]):self.delete_task_row(tid)
        else:button.setEnabled(True)

    def delete_task_row(self,tid):
        if tid not in self._row_map:return
        self._table.removeRow(self._row_map.pop(tid));self.records.pop(tid,None);self._urls.pop(tid,None);self._cancel_callbacks.pop(tid,None)
        self._row_map={self._table.item(r,0).text():r for r in range(self._table.rowCount())};self.empty.setVisible(not self._row_map);self._table.setVisible(bool(self._row_map))

    def _on_delete(self,tid):
        if not self._delete_callback or self._delete_callback(tid):self.delete_task_row(tid)

    def open_folder(self,tid):
        path=self.records[tid].get('output_path')
        if path:QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(path).resolve().parent)))

    def _show_context_menu(self,pos):
        row=self._table.rowAt(pos.y())
        if row<0:return
        tid=self._table.item(row,0).text();menu=QMenu(self)
        for label,fn in [('Copy URL',lambda:QApplication.clipboard().setText(self._urls[tid])),('Cancel',lambda:self._on_cancel(tid)),('Retry',lambda:self._on_retry(tid)),('Remove',lambda:self._on_delete(tid)),('Open Folder',lambda:self.open_folder(tid)),('Open File',lambda:QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(self.records[tid]['output_path']).resolve()))))]:
            action=menu.addAction(tr({'Copy URL':'copy_url','Cancel':'cancel','Retry':'retry','Remove':'remove','Open Folder':'open_folder','Open File':'open_file'}[label]));action.triggered.connect(fn)
            status=TaskStatus.normalize(self.records[tid]['status'])
            if label=='Cancel':action.setEnabled(not status.terminal)
            if label=='Retry':action.setEnabled(status in (TaskStatus.FAILED,TaskStatus.CANCELLED))
            if label in ('Open Folder','Open File'):action.setEnabled(bool(self.records[tid].get('output_path')))
        menu.exec(self._table.viewport().mapToGlobal(pos))
