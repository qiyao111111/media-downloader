"""One path model for source, portable and installed Windows runs."""
import os
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RuntimePaths:
    mode: str
    application_dir: Path
    resources_dir: Path
    runtime_dir: Path
    config_dir: Path
    data_dir: Path
    logs_dir: Path
    download_dir: Path
    temp_dir: Path

    @classmethod
    def resolve(cls, *, frozen=None, executable=None, resources=None, source=None, local_appdata=None):
        frozen = getattr(sys, 'frozen', False) if frozen is None else frozen
        source = Path(source or Path(__file__).resolve().parents[1])
        application = Path(executable or sys.executable).resolve().parent if frozen else source
        assets = Path(resources or getattr(sys, '_MEIPASS', source)) if frozen else source
        mode = 'portable' if frozen and (application/'portable.flag').is_file() else 'installed' if frozen else 'source'
        root = application if mode != 'installed' else Path(local_appdata or os.environ.get('LOCALAPPDATA', Path.home()/'AppData/Local'))/'MediaDownloader'
        return cls(mode, application, assets, application/'bin', root/('configs' if mode=='source' else 'config'),
                   root/'data', root/'logs', source/'video' if mode=='source' else Path.home()/'Downloads/MediaDownloader', root/'temp')

    def initialize(self):
        for path in (self.config_dir, self.data_dir, self.logs_dir, self.download_dir, self.temp_dir):
            path.mkdir(parents=True, exist_ok=True)


PATHS = RuntimePaths.resolve()
