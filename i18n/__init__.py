"""UI-only translations; technical values and core records are never translated."""
import json
import logging
from pathlib import Path
from PySide6.QtCore import QObject,QCoreApplication,QTranslator
import PySide6

CATALOGS = {name: json.loads((Path(__file__).parent/(name+'.json')).read_text(encoding='utf-8')) for name in ('en_US','zh_CN')}
_language = 'en_US'
MISSING_KEYS = set()
_qt_translator = None


def set_language(language):
    global _language, _qt_translator
    _language = {'en':'en_US','zh':'zh_CN'}.get(language, language)
    if _language not in CATALOGS: _language = 'en_US'
    app = QCoreApplication.instance()
    if app:
        if _qt_translator:app.removeTranslator(_qt_translator)
        if _language=='zh_CN':
            if _qt_translator is None:
                _qt_translator=QTranslator(app)
                _qt_translator.load(str(Path(PySide6.__file__).parent/'translations/qtbase_zh_CN.qm'))
            app.installTranslator(_qt_translator)


def tr(key, **values):
    text = CATALOGS[_language].get(key) or CATALOGS['en_US'].get(key)
    if not text:
        MISSING_KEYS.add(key)
        logging.getLogger('desktop').warning('Missing translation: %s', key)
        text = CATALOGS[_language]['error.generic']
    return text.format(**values)


def bind(widget, key, method='setText', **values):
    bindings = widget.property('i18n_bindings') or {}
    bindings[method] = (key, values)
    widget.setProperty('i18n_bindings', bindings)
    getattr(widget, method)(tr(key, **values))
    return widget


def translate_tree(root):
    for widget in [root, *root.findChildren(QObject)]:
        for method, (key, values) in (widget.property('i18n_bindings') or {}).items():
            getattr(widget, method)(tr(key, **values))


def combo_labels(combo, keys):
    combo.blockSignals(True)
    for index, key in enumerate(keys):
        if key: combo.setItemText(index, tr(key))
    combo.blockSignals(False)


def status_label(status):
    return tr('status.'+status)


def runtime_label(status):
    return tr('runtime.ready' if status=='READY' else 'runtime.missing' if status=='NOT_INSTALLED' else 'runtime.warning')
