"""Prove a notices-only rebuild retained the tested executable's embedded code."""
import hashlib
import json
import sys
from pathlib import Path
from PyInstaller.archive.readers import CArchiveReader


def digest(value):return hashlib.sha256(value).hexdigest()


def run(before, after, out):
    first=CArchiveReader(str(before/'MediaDownloader.exe'));last=CArchiveReader(str(after/'MediaDownloader.exe'))
    assert first.toc.keys()==last.toc.keys()
    members={name:first.extract(name)==last.extract(name) for name in first.toc}
    assert all(members.values())
    files={}
    for path in (after/'bin').rglob('*'):
        if path.is_file():
            relative=path.relative_to(after);files[str(relative)]=digest(path.read_bytes())
            assert path.read_bytes()==(before/relative).read_bytes()
    result={'embedded_members_identical':members,'native_runtime_sha256':files,
            'tested_exe_sha256':digest((before/'MediaDownloader.exe').read_bytes()),
            'release_exe_sha256':digest((after/'MediaDownloader.exe').read_bytes())}
    out.write_text(json.dumps(result,indent=2),encoding='utf-8');print('Embedded code and bundled native runtimes identical')


if __name__=='__main__':run(*(Path(arg) for arg in sys.argv[1:4]))
