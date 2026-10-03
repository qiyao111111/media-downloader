"""Semantic styles and matching native palette."""
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor,QPalette
from PySide6.QtWidgets import QApplication
from gui.design_tokens import PALETTES, CONTROL

def apply_theme(app: QApplication, theme_name: str):
    if theme_name=='system':theme_name='dark' if app.styleHints().colorScheme()==Qt.ColorScheme.Dark else 'light'
    colors=PALETTES.get(theme_name)
    if colors is None:return
    palette=QPalette()
    for role,key in [(QPalette.Window,'background'),(QPalette.WindowText,'text'),(QPalette.Base,'surface'),(QPalette.AlternateBase,'hover'),(QPalette.Text,'text'),(QPalette.Button,'surface'),(QPalette.ButtonText,'text'),(QPalette.Highlight,'selected'),(QPalette.HighlightedText,'text'),(QPalette.ToolTipBase,'surface'),(QPalette.ToolTipText,'text')]:palette.setColor(role,QColor(colors[key]))
    for role in (QPalette.Text,QPalette.ButtonText,QPalette.WindowText):palette.setColor(QPalette.Disabled,role,QColor(colors['disabled']))
    app.setPalette(palette)
    text=(Path(__file__).parent/'styles/base.qss').read_text(encoding='utf-8')
    text=text.replace('@large_inner',str(CONTROL['large']-14))
    for key in sorted(colors,key=len,reverse=True):text=text.replace('@'+key,colors[key])
    app.setStyleSheet(text);app.setProperty('theme',theme_name)
    from gui.widgets.presentation import line_icon,EmptyStateWidget
    for widget in app.topLevelWidgets():
        if hasattr(widget,'navigation'):
            for index,name in enumerate(('download','queue','history','settings','logs')):widget.navigation.item(index).setIcon(line_icon(name))

    for widget in app.allWidgets():
        if isinstance(widget,EmptyStateWidget):widget.update_icon()

def available_themes() -> list[str]:return ['system',*PALETTES]
