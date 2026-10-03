"""One-command pinned onedir + Portable ZIP + Inno Setup build (Windows x64)."""
import hashlib
import importlib.metadata as metadata
import json
import os
import shutil
import struct
import subprocess
import sys
import urllib.request
from datetime import datetime,timezone
from pathlib import Path
from app.version import VERSION, WINDOWS_VERSION, PRODUCT, PUBLISHER

ROOT = Path(__file__).resolve().parent
CACHE = ROOT/'.tools'


def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def download(component):
    path = CACHE/component['url'].rsplit('/',1)[-1]
    if not path.is_file() or sha(path)!=component['sha256']:
        temporary=path.with_suffix(path.suffix+'.tmp')
        try:
            with urllib.request.urlopen(component['url'],timeout=60) as source, temporary.open('wb') as target:shutil.copyfileobj(source,target)
            if sha(temporary)!=component['sha256']:raise ValueError('Runtime download checksum mismatch: '+path.name)
            temporary.replace(path)
        finally:temporary.unlink(missing_ok=True)
    return path


def clean(path):
    target=path.resolve()
    if target in (ROOT.resolve(), CACHE.resolve()) or not target.is_relative_to(ROOT.resolve()):raise ValueError('Unsafe clean target')
    if target.is_dir():shutil.rmtree(target)


def metadata_files():
    from PySide6.QtCore import QBuffer, QIODevice, QPoint
    from PySide6.QtGui import QImage,QPainter,QColor,QPolygon
    images=[]
    for size in (16,32,48,256):
        image=QImage(size,size,QImage.Format_ARGB32);image.fill(QColor('#296da8'))
        p=QPainter(image);p.setPen(QColor('white'));p.setBrush(QColor('white'))
        p.drawRect(size*3//8,size//5,size//4,size*2//5)
        p.drawPolygon(QPolygon([QPoint(size//4,size//2),QPoint(size*3//4,size//2),QPoint(size//2,size*3//4)]));p.end()
        b=QBuffer();b.open(QIODevice.WriteOnly);image.save(b,'PNG');images.append((size,bytes(b.data())))
    offset=6+16*len(images);header=struct.pack('<HHH',0,1,len(images));body=b''
    for size,data in images:
        header+=struct.pack('<BBBBHHII',size%256,size%256,0,0,1,32,len(data),offset);body+=data;offset+=len(data)
    (ROOT/'build/app.ico').write_bytes(header+body)
    values={'CompanyName':PUBLISHER,'FileDescription':PRODUCT,'FileVersion':VERSION,'ProductName':PRODUCT,'ProductVersion':VERSION,'LegalCopyright':'Original project © 2023 Gaius Pluto; contributors','OriginalFilename':'MediaDownloader.exe'}
    strings=','.join(f'StringStruct({k!r}, {v!r})' for k,v in values.items())
    (ROOT/'build/version.txt').write_text(f"VSVersionInfo(ffi=FixedFileInfo(filevers={WINDOWS_VERSION!r}, prodvers={WINDOWS_VERSION!r}, mask=0x3f, flags=0, OS=0x40004, fileType=1, subtype=0, date=(0,0)), kids=[StringFileInfo([StringTable('040904B0',[{strings}])]), VarFileInfo([VarStruct('Translation',[1033,1200])])])",encoding='utf-8')


def licenses(destination, lock):
    from release_licenses import collect
    collect(destination, lock)


def main():
    if sys.platform!='win32':raise SystemExit('Build requires Windows x64')
    CACHE.mkdir(exist_ok=True);lock=json.loads((ROOT/'build/runtime-lock.json').read_text())
    download(lock['inno'])
    native=CACHE/'b43/native-build/prefix/bin';quickjs=CACHE/'b43/quickjs/build/qjs.exe'
    for name,digest in lock['ffmpeg']['files'].items():
        if not (native/name).is_file() or sha(native/name)!=digest:raise ValueError('Rebuild pinned native runtime: '+name)
    if not quickjs.is_file() or sha(quickjs)!=lock['quickjs']['sha256']:raise ValueError('Rebuild pinned QuickJS runtime')
    metadata_files()
    build_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    work=ROOT/'build/work';clean(work)
    bundle=ROOT/'dist/MediaDownloader';portable=ROOT/'dist/MediaDownloader-Portable';release=ROOT/'dist/release'
    for p in (bundle,portable,release):clean(p)
    release.mkdir(parents=True)
    build_env=dict(os.environ)
    build_env['PATH']=str(Path(sys.base_prefix))+os.pathsep+str(Path(os.environ['SystemRoot'])/'System32')+os.pathsep+os.environ['SystemRoot']
    for key in ('PYTHONPATH','QT_PLUGIN_PATH','QML2_IMPORT_PATH'):build_env.pop(key,None)
    subprocess.run([sys.executable,'-m','PyInstaller','--noconfirm','--clean','--workpath',str(work),str(ROOT/'build/MediaDownloader.spec')],cwd=ROOT,env=build_env,check=True)
    (bundle/'bin/runtime').mkdir(parents=True)
    for name in lock['ffmpeg']['files']:shutil.copy2(native/name,bundle/'bin'/name)
    shutil.copy2(quickjs,bundle/'bin/runtime/qjs.exe')
    licenses(bundle/'licenses',lock)
    installer_sources=bundle/'SOURCES/Installer';installer_sources.mkdir()
    for name in ('ChineseSimplified.isl','installer-language-source.json'):
        shutil.copy2(ROOT/'build'/name,installer_sources/name)
    notice=bundle/'THIRD_PARTY_NOTICES.txt'
    notice.write_text(notice.read_text(encoding='utf-8').replace('@VERSION@',VERSION),encoding='utf-8')
    (bundle/'README.txt').write_text((ROOT/'build/README.txt').read_text(encoding='utf-8').replace('@VERSION@',VERSION),encoding='utf-8')
    from release_licenses import inspect_bundle
    (bundle/'licenses/bundle-file-inventory.json').write_text(json.dumps(inspect_bundle(bundle),indent=2),encoding='utf-8')
    shutil.copytree(bundle,portable);(portable/'portable.flag').touch()
    shutil.make_archive(str(release/'MediaDownloader-Portable'),'zip',portable.parent,portable.name)
    iscc=str(CACHE/'inno/ISCC.exe')
    if not Path(iscc).is_file():raise SystemExit('Install the pinned Inno Setup 6.7.3 compiler into .tools/inno')
    subprocess.run([iscc,'/DAppVersion='+VERSION,'/DWindowsVersion='+'.'.join(map(str,WINDOWS_VERSION)),
                    '/DProductName='+PRODUCT,'/DProductPublisher='+PUBLISHER,str(ROOT/'build/installer.iss')],check=True)
    shutil.copy2(bundle/'THIRD_PARTY_NOTICES.txt',release/'THIRD_PARTY_NOTICES.txt');shutil.copytree(bundle/'licenses',release/'LICENSES')
    shutil.copytree(bundle/'source-offer',release/'source-offer')
    shutil.copytree(bundle/'SOURCES',release/'SOURCES')
    (release/'checksums.txt').write_text('\n'.join(sha(release/name)+'  '+name for name in ('MediaDownloader-Portable.zip','MediaDownloader-Setup.exe'))+'\n')
    manifest={'app':VERSION,'python':sys.version,'platform':sys.platform,'dependencies':{n:metadata.version(n) for n in ('yt-dlp','yt-dlp-ejs','PySide6','PyYAML','PyInstaller','pyinstaller-hooks-contrib')},'runtime':lock}
    (release/'build-manifest.json').write_text(json.dumps(manifest,indent=2));print(release)
    public_manifest={'product':PRODUCT,'version':VERSION,'build_commit':build_commit,'build_date':datetime.now(timezone.utc).isoformat(),
                     'architecture':'x64','portable_sha256':sha(release/'MediaDownloader-Portable.zip'),
                     'installer_sha256':sha(release/'MediaDownloader-Setup.exe'),'yt_dlp_version':metadata.version('yt-dlp'),
                     'ffmpeg_version':lock['ffmpeg']['version'],'quickjs_version':lock['quickjs']['version'],
                     'clean_machine_gate':'NOT TESTED','public_distribution_gate':'NEEDS LEGAL REVIEW'}
    (release/'release-manifest.json').write_text(json.dumps(public_manifest,indent=2)+'\n',encoding='utf-8')
    release_notes=f'RELEASE_NOTES_{VERSION}.md'
    shutil.copy2(ROOT/release_notes,release/release_notes)
    kit=ROOT/'release-test';kit.mkdir(exist_ok=True)
    for name in ('MediaDownloader-Portable.zip','MediaDownloader-Setup.exe','checksums.txt','release-manifest.json',release_notes):
        shutil.copy2(release/name,kit/name)


if __name__=='__main__':main()
