"""Terminal history is separate from the current-session queue."""
from pathlib import Path
from PySide6.QtCore import Signal,QUrl,Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QTableWidget,QTableWidgetItem,QHeaderView,QPushButton,QApplication
from gui.widgets.presentation import page_layout,page_header,EmptyStateWidget,StatusBadge
from models.download import TaskStatus
from i18n import tr,bind,status_label


class HistoryPage(QWidget):
    retry_requested=Signal(str,str)
    remove_requested=Signal(str)
    def __init__(self,parent=None):
        super().__init__(parent);layout=page_layout(self);page_header(layout,'nav.history');self.empty=EmptyStateWidget('history_empty','history_description','history');layout.addWidget(self.empty)
        self.table=QTableWidget(0,6);self.table.setHorizontalHeaderLabels(['Title','URL','Quality','Status','Date','Output Path'])
        self.table.setColumnHidden(1,True);self.table.setShowGrid(False);self.table.verticalHeader().hide();self.table.verticalHeader().setDefaultSectionSize(44)
        self.table.setTextElideMode(Qt.ElideRight)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers);self.table.setSelectionBehavior(QTableWidget.SelectRows);self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch);layout.addWidget(self.table)
        self.records=[];row=QHBoxLayout();self.buttons={}
        for label in ('Open File','Open Folder','Copy URL','Retry','Remove History'):
            btn=bind(QPushButton(),{'Open File':'open_file','Open Folder':'open_folder','Copy URL':'copy_url','Retry':'redownload','Remove History':'remove_history'}[label]);btn.clicked.connect(lambda checked=False,name=label:self.action(name));row.addWidget(btn);self.buttons[label]=btn
        layout.addLayout(row);self.table.itemSelectionChanged.connect(self.update_buttons);self.retranslate();self.update_buttons()

    def retranslate(self):
        self.table.setHorizontalHeaderLabels([tr(k) for k in ('title','url','quality','status','date','output_path')])
        self.render(self.records)

    def render(self,records):
        selected=self.selected();selected_id=selected.get('task_id') if selected else None
        self.records=[r for r in records if TaskStatus.normalize(r['status']).terminal]
        self.table.setRowCount(len(self.records))
        for row,r in enumerate(self.records):
            for col,k in enumerate(('title','url','quality','status','date','output_path')):
                item=QTableWidgetItem(status_label(r['status']) if k=='status' else str(r.get(k,'') or '--'));item.setToolTip(item.text());self.table.setItem(row,col,item)
            badge=self.table.cellWidget(row,3)
            if badge is None:
                badge=StatusBadge();self.table.setCellWidget(row,3,badge)
            badge.set_status(r['status'])
            self.table.item(row,3).setForeground(Qt.transparent)
            if r['task_id']==selected_id:self.table.selectRow(row)
        self.empty.setVisible(not self.records);self.table.setVisible(bool(self.records));self.update_buttons()

    def selected(self):
        row=self.table.currentRow()
        return self.records[row] if 0<=row<len(self.records) else None

    def update_buttons(self):
        r=self.selected()
        for label,btn in self.buttons.items():
            valid=bool(r)
            if label in ('Open File','Open Folder'):valid=bool(r and r.get('output_path') and Path(r['output_path']).exists())
            if label=='Retry':valid=bool(r and TaskStatus.normalize(r['status']).terminal)
            btn.setEnabled(valid);btn.setVisible(bool(r))

    def action(self,label):
        r=self.selected()
        if not r:return
        if label=='Copy URL':QApplication.clipboard().setText(r['url'])
        elif label=='Retry':self.retry_requested.emit(r['task_id'],r['url'])
        elif label=='Remove History':self.remove_requested.emit(r['task_id'])
        elif r.get('output_path'):
            path=Path(r['output_path']).resolve()
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path.parent if label=='Open Folder' else path)))
