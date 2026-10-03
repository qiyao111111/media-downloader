"""Display-only widgets. Callers own quality data and task states."""
from PySide6.QtCore import Qt, QSize, QRectF, QRect
from PySide6.QtGui import QPainter, QTextLayout, QTextOption, QIcon, QPixmap, QPainterPath
from PySide6.QtWidgets import QWidget, QLabel, QFrame, QVBoxLayout, QHBoxLayout, QSizePolicy, QPushButton, QProgressBar, QStyleOptionProgressBar, QStyle
from gui.design_tokens import CARD, GAP, PAGE_X, PAGE_Y, CONTROL
from i18n import bind, status_label, runtime_label


def refresh(widget):
    widget.style().unpolish(widget); widget.style().polish(widget); widget.update()


def page_header(layout, key, subtitle=None):
    title=bind(QLabel(),key); title.setProperty('role','page'); layout.addWidget(title)
    if subtitle:
        label=bind(QLabel(),subtitle); label.setProperty('role','secondary'); label.setWordWrap(True); layout.addWidget(label)
    return title


def page_layout(widget):
    layout=QVBoxLayout(widget); layout.setContentsMargins(PAGE_X,PAGE_Y,PAGE_X,PAGE_Y); layout.setSpacing(GAP)
    return layout


def card():
    widget=QFrame(); widget.setProperty('role','card'); layout=QVBoxLayout(widget)
    layout.setContentsMargins(CARD,CARD,CARD,CARD); layout.setSpacing(GAP)
    return widget,layout


class PrimaryButton(QPushButton):
    def __init__(self,key,parent=None):
        super().__init__(parent); bind(self,key); self.setProperty('variant','primary'); self.setMinimumHeight(CONTROL['large'])


class SecondaryButton(QPushButton):
    def __init__(self,key,parent=None):
        super().__init__(parent); bind(self,key)


class InfoChip(QLabel):
    def __init__(self,text='',tone='info',parent=None):
        super().__init__(text,parent); self.setProperty('role','badge'); self.setProperty('tone',tone)
        self.setFixedHeight(24); self.setSizePolicy(QSizePolicy.Maximum,QSizePolicy.Fixed)


class QualityChip(InfoChip):
    pass


class StatusBadge(InfoChip):
    def set_status(self,status):
        self.setText(status_label(status))
        self.setProperty('tone',{'completed':'success','failed':'danger','cancelled':'neutral','queued':'neutral','postprocessing':'warning'}.get(status,'info')); refresh(self)


class EmptyStateWidget(QWidget):
    def __init__(self,title,description,icon=None,action=None,parent=None):
        super().__init__(parent); layout=QVBoxLayout(self); layout.setContentsMargins(24,32,24,32); layout.setSpacing(8)
        layout.addStretch()
        self.title=bind(QLabel(),title); self.title.setProperty('role','section'); self.title.setAlignment(Qt.AlignCenter); layout.addWidget(self.title)
        self.description=bind(QLabel(),description); self.description.setProperty('role','secondary'); self.description.setAlignment(Qt.AlignCenter); self.description.setWordWrap(True); layout.addWidget(self.description)
        self.icon=QLabel(); self.icon_name=icon or 'download'; self.icon.setAlignment(Qt.AlignCenter); layout.insertWidget(1,self.icon); self.update_icon()
        for label in (self.icon,self.title,self.description):label.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Fixed)
        if action: layout.addWidget(action)
        layout.addStretch()


    def update_icon(self):
        self.icon.setPixmap(line_icon(self.icon_name).pixmap(24,24))

class InfoBanner(QLabel):
    def __init__(self,key,tone='info',parent=None):
        super().__init__(parent);bind(self,key);self.setProperty('role','banner');self.setProperty('tone',tone);self.setWordWrap(True)

class TaskProgressBar(QProgressBar):
    """Keep the existing value/range API; paint an 8px track and separate text."""
    def paintEvent(self,event):
        painter=QPainter(self);option=QStyleOptionProgressBar();self.initStyleOption(option)
        text=option.text;option.textVisible=False;option.rect=QRect(8,self.height()-16,max(0,self.width()-16),8)
        self.style().drawControl(QStyle.CE_ProgressBar,option,painter,self)
        painter.setPen(self.palette().windowText().color());painter.drawText(QRect(0,0,self.width(),self.height()-20),Qt.AlignCenter,text)

class RuntimeStatusRow(QWidget):
    def __init__(self,component,version,status,parent=None):
        super().__init__(parent); layout=QHBoxLayout(self); layout.setContentsMargins(0,4,0,4)
        layout.addWidget(QLabel(component)); value=QLabel(str(version)); value.setProperty('role','secondary'); layout.addWidget(value,1)
        dot=QLabel();dot.setFixedSize(8,8);dot.setProperty('role','status_dot');dot.setProperty('tone','success' if status=='READY' else 'danger' if status=='NOT_INSTALLED' else 'warning');layout.addWidget(dot)
        self.badge=InfoChip(runtime_label(status),'success' if status=='READY' else 'danger' if status=='NOT_INSTALLED' else 'warning'); layout.addWidget(self.badge)


class ThumbnailLabel(QLabel):
    def setPixmap(self,pixmap):
        rounded=QPixmap(pixmap.size());rounded.fill(Qt.transparent);painter=QPainter(rounded);painter.setRenderHint(QPainter.Antialiasing)
        clip=QPainterPath();clip.addRoundedRect(QRectF(rounded.rect()),8,8);painter.setClipPath(clip);painter.drawPixmap(0,0,pixmap);painter.end();super().setPixmap(rounded)

class ElidedLabel(QLabel):
    def __init__(self,text='',parent=None):
        super().__init__(text,parent);self.setMinimumWidth(0);self.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Fixed)
    def paintEvent(self,event):
        painter=QPainter(self);painter.setPen(self.palette().windowText().color());painter.drawText(self.rect(),Qt.AlignVCenter,self.fontMetrics().elidedText(self.text(),Qt.ElideRight,self.width()))

class TwoLineLabel(QLabel):
    """Retain source text while painting at most two elided lines."""
    def __init__(self,parent=None):
        super().__init__(parent); self.setMinimumWidth(0); self.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Fixed)

    def sizeHint(self):
        return QSize(300,self.fontMetrics().height()*2+4)

    def paintEvent(self,event):
        painter=QPainter(self); painter.setPen(self.palette().color(self.foregroundRole()))
        text=self.text(); option=QTextOption(); option.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        layout=QTextLayout(text,self.font()); layout.setTextOption(option); layout.beginLayout(); y=0
        for index in range(2):
            line=layout.createLine()
            if not line.isValid(): break
            line.setLineWidth(self.width()); start=line.textStart(); length=line.textLength()
            display=text[start:start+length] if index==0 else self.fontMetrics().elidedText(text[start:],Qt.ElideRight,self.width())
            painter.drawText(0,int(y+self.fontMetrics().ascent()),display); y+=line.height()
        layout.endLayout()


# One local SVG source; no icon dependency or emoji.
ICON_PATHS = {
    'download':'M10 2v11m-4-4 4 4 4-4M3 14v4h14v-4',
    'queue':'M4 5h12M4 10h12M4 15h12',
    'history':'M3 9a7 7 0 1 1 2 6M3 3v6h6M10 6v5l3 2',
    'settings':'M10 2v3m0 10v3M2 10h3m10 0h3M4 4l2 2m8 8 2 2M4 16l2-2m8-8 2-2M10 6a4 4 0 1 0 0 8 4 4 0 0 0 0-8',
    'logs':'M4 2h12v16H4zM7 6h6M7 10h6M7 14h4',
}


def line_icon(name):
    from PySide6.QtSvg import QSvgRenderer
    from PySide6.QtWidgets import QApplication
    color=QApplication.palette().windowText().color().name()
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20"><path d="{ICON_PATHS[name]}" fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    pix=QPixmap(40,40); pix.setDevicePixelRatio(2); pix.fill(Qt.transparent)
    painter=QPainter(pix); QSvgRenderer(svg.encode()).render(painter,QRectF(0,0,20,20)); painter.end()
    return QIcon(pix)
