"""Actual payload files; source-only materials are separate from runtime code."""
import hashlib
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from release_licenses import inspect_bundle

ROOT=Path(__file__).resolve().parents[1]


def run():
    bundle=ROOT/'dist/MediaDownloader';evidence=ROOT/'docs/evidence'
    previous=json.loads((evidence/'b4_2-distribution-files.json').read_text())
    old={r['file']:r for r in previous['files']};rows=[]
    for path in sorted(bundle.rglob('*')):
        if not path.is_file():continue
        relative=path.relative_to(bundle).as_posix()
        with path.open('rb') as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
        row={'file':relative,'bytes':path.stat().st_size,'sha256':digest};before=old.get(relative)
        if relative.startswith('bin/'):
            row.update(component='QuickJS-NG + compiler runtime' if path.name=='qjs.exe' else 'FFmpeg + pinned static libraries + compiler runtime',origin='Own pinned source build; SOURCES/receipt.json')
        elif relative.startswith('SOURCES/'):
            row.update(component='Native source/build/relink provision (not executable runtime)',origin='Own build inputs; build/native-runtime-lock.json')
        elif before and digest==before['sha256']:
            row.update({k:before[k] for k in ('component','origin','version_info') if k in before})
        elif relative.startswith('licenses/') or relative in ('THIRD_PARTY_NOTICES.txt','source-offer/README.txt'):
            row.update(component='License/notices/source provision',origin='release_licenses.py + exact installed source grants')
        elif relative=='MediaDownloader.exe':
            row.update(component='Application + embedded Python/PyInstaller bootloader',origin='PyInstaller 6.22.3; runtime discovery/diagnostics changes only')
        else:
            row.update(component=before['component'] if before else 'Application resources',origin=before['origin'] if before else 'Project/build resources')
        rows.append(row)
    inventory={'scope':'Actual final onedir files; ZIP/installed equality validated separately','files':rows,
               'embedded_modules':inspect_bundle(bundle)['embedded_modules'],'installer_only_files':['unins000.exe','unins000.dat'],
               'portable_only_files':['portable.flag'],'transitive_binary_SBOM_complete':False,'native_direct_sources_pinned':9}
    (evidence/'b4_3-distribution-files.json').write_text(json.dumps(inventory,indent=2),encoding='utf-8')
    def stats(files):
        return {'files':len(files),'native_files':sum(Path(r['file']).suffix.lower() in ('.exe','.dll','.pyd') for r in files),
                'license_files':sum(r['file'].startswith('licenses/') for r in files),'total_bytes':sum(r['bytes'] for r in files),
                'bin_bytes':sum(r['bytes'] for r in files if r['file'].startswith('bin/'))}
    comparison={'b4_2':stats(previous['files']),'b4_3':stats(rows),
                'unchanged_native_origins':[r['file'] for r in rows if Path(r['file']).suffix.lower() in ('.exe','.dll','.pyd') and old.get(r['file'],{}).get('sha256')==r['sha256']]}
    (evidence/'b4_3-distribution-comparison.json').write_text(json.dumps(comparison,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in comparison.items() if k!='unchanged_native_origins'}))


if __name__=='__main__':run()
