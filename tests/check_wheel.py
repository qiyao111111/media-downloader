"""Check that installed entry point and UI resources ship in the wheel."""
from pathlib import Path
from zipfile import ZipFile

if __name__ == '__main__':
    wheel = max(Path('dist').glob('*.whl'), key=lambda p: p.stat().st_mtime)
    with ZipFile(wheel) as archive:
        names = set(archive.namelist())
        for resource in ('main.py', 'i18n/en_US.json', 'i18n/zh_CN.json',
                         'configs/yt-dlp.yml', 'gui/styles/base.qss'):
            assert resource in names, f'Missing wheel resource: {resource}'
    print(f'Wheel resources verified: {wheel.name}')
