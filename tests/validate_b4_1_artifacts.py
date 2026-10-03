"""Actual ZIP/installed-file comparison; never substitutes for clean Windows."""
import hashlib,json,sys,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from release_licenses import inspect_bundle,sha


def run(installed,out):
    root=Path(__file__).resolve().parents[1];bundle=root/'dist/MediaDownloader';release=root/'dist/release'
    inventory=inspect_bundle(bundle)
    assert not any(n=='PyInstaller' or n.startswith(('PyInstaller.','yt_dlp.__pyinstaller')) for n in inventory['embedded_modules'])
    translations=sorted(p.relative_to(bundle).as_posix() for p in bundle.rglob('*.qm'))
    assert translations in ([],['_internal/PySide6/translations/qtbase_zh_CN.qm'])
    paths=[p for p in bundle.rglob('*') if p.is_file()]
    with zipfile.ZipFile(release/'MediaDownloader-Portable.zip') as archive:
        for path in paths:
            relative=path.relative_to(bundle).as_posix()
            assert hashlib.sha256(archive.read('MediaDownloader-Portable/'+relative)).hexdigest()==sha(path),relative
            assert sha(installed/relative)==sha(path),relative
        assert 'MediaDownloader-Portable/portable.flag' in archive.namelist()
    verified=[]
    for item in json.loads((bundle/'licenses/source-provenance.json').read_text()):
        file=bundle/'licenses'/('source-code' if item.get('source_archive') else '')/item['name']
        assert sha(file)==item['sha256'];verified.append(item['name'])
    checksums={}
    for line in (release/'checksums.txt').read_text().splitlines():
        digest,name=line.split('  ',1);assert sha(release/name)==digest;checksums[name]=digest
    assert (installed/'source-offer/README.txt').is_file()
    assert (installed/'licenses/Apache-2.0.txt').is_file()
    hooks=list((installed/'licenses/PyInstaller-runtime').rglob('*.py'))
    assert hooks and all('Copyright' in p.read_text() for p in hooks)
    notices=(installed/'THIRD_PARTY_NOTICES.txt').read_text(encoding='utf-8')
    assert not any(word in notices for word in ('TBD','TODO','unknown'))
    result={'scope':'local installed bundle and actual Portable ZIP; clean Windows NOT TESTED',
            'payload_files_identical':len(paths),'embedded_modules':len(inventory['embedded_modules']),
            'GPL_analysis_modules_absent':True,'compiled_translations':translations,
            'verified_source_files':verified,'runtime_hook_copyright_files':len(hooks),
            'checksums':checksums,'maximum_bundle_relative_path':max(len(str(p.relative_to(bundle))) for p in paths)}
    out.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))


if __name__=='__main__':run(Path(sys.argv[1]),Path(sys.argv[2]))
