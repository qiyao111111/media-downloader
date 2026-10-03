# onedir; native tools are copied into the sibling bin directory by the build.
from pathlib import Path
from PyInstaller.utils.hooks import collect_all, copy_metadata
import PySide6
root = Path(SPECPATH).parent
datas = [(str(root/'configs/yt-dlp.yml'), 'configs'), (str(root/'gui/styles'), 'gui/styles'), (str(root/'build/app.ico'), '.')]
datas += [(str(root/'i18n/en_US.json'),'i18n'),(str(root/'i18n/zh_CN.json'),'i18n'),
          (str(Path(PySide6.__file__).parent/'translations/qtbase_zh_CN.qm'),'PySide6/translations')]
hiddenimports = []
for package in ('yt_dlp', 'yt_dlp_ejs'):
    package_datas, package_binaries, package_hidden = collect_all(package)
    datas += package_datas
    hiddenimports += package_hidden
# yt-dlp's build-time hook imports GPL PyInstaller analysis code. It is not an
# application dependency; retain only the bootloader and standalone runtime hooks.
hiddenimports = [name for name in hiddenimports if not name.startswith('yt_dlp.__pyinstaller')]
datas = [entry for entry in datas if '__pyinstaller' not in Path(entry[0]).parts]
datas += copy_metadata('yt-dlp') + copy_metadata('yt-dlp-ejs')
a = Analysis([str(root/'main.py')], pathex=[str(root)], binaries=[], datas=datas,
             hiddenimports=hiddenimports, runtime_hooks=[str(root/'build/runtime_hook.py')], excludes=['PyInstaller', 'yt_dlp.__pyinstaller', 'tkinter', 'PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets', 'PySide6.QtPdf', 'PySide6.QtVirtualKeyboard', 'PySide6.QtQml', 'PySide6.QtQuick'])
# QtGui's broad plugin hook otherwise pulls unused GPL-only PDF/virtual keyboard
# plugins and their QML/Quick libraries. These capabilities are outside this app.
def needed(entry):
    name = Path(entry[0]).name.lower()
    # This QWidget/raster application creates no OpenGL widgets or contexts.
    # The optional Mesa renderer is not an application dependency.
    return (not name.endswith('.qm') or name=='qtbase_zh_cn.qm') and name not in ('opengl32sw.dll', 'qpdf.dll', 'qtvirtualkeyboardplugin.dll', 'icuuc.dll', 'icuin.dll') and not name.startswith(('qt6pdf','qt6virtualkeyboard','qt6qml','qt6quick','icudt'))
a.binaries = [entry for entry in a.binaries if needed(entry)]
a.datas = [entry for entry in a.datas if needed(entry)]
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='MediaDownloader',
          console=False, icon=str(root/'build/app.ico'), version=str(root/'build/version.txt'))
coll = COLLECT(exe, a.binaries, a.datas, name='MediaDownloader')
