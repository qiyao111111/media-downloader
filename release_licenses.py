"""File-backed redistribution evidence; no application/download behavior."""
import hashlib
import importlib.metadata as metadata
import json
import posixpath
import shutil
import subprocess
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path
from PyInstaller.archive.readers import CArchiveReader

ROOT=Path(__file__).resolve().parent


def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def inspect_bundle(bundle):
    archive=CArchiveReader(str(bundle/'MediaDownloader.exe'))
    modules=sorted(archive.open_embedded_archive('PYZ.pyz').toc)
    files={str(p.relative_to(bundle)).replace('\\','/'):{'bytes':p.stat().st_size,'sha256':sha(p)}
           for p in sorted(bundle.rglob('*')) if p.is_file() and 'licenses' not in p.relative_to(bundle).parts
           and p.name!='THIRD_PARTY_NOTICES.txt'}
    return {'files':files,'embedded_modules':modules,'bootloader_members':sorted(archive.toc)}


def fetch_source(item):
    target=ROOT/'.tools/license-sources'/item['name'];target.parent.mkdir(parents=True,exist_ok=True)
    if target.is_file() and sha(target)==item['sha256']:return target
    temporary=target.with_suffix(target.suffix+'.tmp')
    try:
        if item['url'].startswith('https://api.github.com/'):
            args=['gh','api',item['url'].split('https://api.github.com/')[1]]
            if '/contents/' in item['url']:args+=['-H','Accept: application/vnd.github.raw+json']
            with temporary.open('wb') as stream:subprocess.run(args,stdout=stream,check=True)
        else:
            with urllib.request.urlopen(item['url'],timeout=60) as response,temporary.open('wb') as stream:shutil.copyfileobj(response,stream)
        if sha(temporary)!=item['sha256']:raise ValueError('License/source checksum mismatch: '+item['name'])
        temporary.replace(target)
    finally:temporary.unlink(missing_ok=True)
    return target


def collect_native_materials(destination):
    """Ship the actual native build inputs, grants and rebuild/relink materials."""
    from build_native_runtime import BUILD, PREFIX, LLVM, source
    bundle=destination.parent;sources=bundle/'SOURCES';sources.mkdir()
    lock=json.loads((ROOT/'build/native-runtime-lock.json').read_text(encoding='utf-8'))
    for item in lock['sources']:
        archive=ROOT/'.tools/b43/native-sources'/item['archive']
        if sha(archive)!=item['sha256']:raise ValueError('Native source mismatch: '+item['component'])
        shutil.copy2(archive,sources/item['archive'])
    for filename in ('build_native_runtime.py','build/native-runtime-lock.json'):
        shutil.copy2(ROOT/filename,sources/Path(filename).name)
    for filename in ('config.h','config_components.h','ffbuild/config.mak','ffbuild/config.log','libavutil/ffversion.h'):
        shutil.copy2(BUILD/'ffmpeg'/filename,sources/Path(filename).name)
    for filename in ('commands.json','receipt.json','meson.ini'):
        shutil.copy2(BUILD/filename,sources/filename)
    shutil.copy2(ROOT/'redistribution/NATIVE_BUILD_INSTRUCTIONS.txt',sources/'BUILD_INSTRUCTIONS.txt')
    (sources/'PATCHES.txt').write_text('No local FFmpeg or dependency source modifications.\nUpstream zlib CMake renames/generates its configuration header.\nVersion metadata is supplied by the pinned build recipe; no source-code patch.\n',encoding='utf-8')
    # Complete rebuilt static dependencies and compiled FFmpeg objects accompany
    # source, so recipients also have the concrete inputs for library relinking.
    with zipfile.ZipFile(sources/'native-relink-materials.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for path in sorted((PREFIX/'lib').glob('*.a')):archive.write(path,'static-libraries/'+path.name)
        for path in sorted((BUILD/'ffmpeg').rglob('*.o')):archive.write(path,'ffmpeg-objects/'+str(path.relative_to(BUILD/'ffmpeg')))
        for name in ('libc++.a','libc++abi.a','libunwind.a','libwinpthread.a'):
            path=LLVM.parent/'x86_64-w64-mingw32/lib'/name
            if not path.is_file():raise ValueError('Missing relink runtime archive: '+name)
            archive.write(path,'toolchain-runtime/'+name)
    grants={'ffmpeg':('COPYING.LGPLv2.1','COPYING.GPLv2','LICENSE.md'),
            'lame':('COPYING','LICENSE','README'), 'opus':('COPYING',),
            'dav1d':('COPYING',),'quickjs':('LICENSE',),'zlib':('README',),
            'openh264':('LICENSE',),'vpx':('LICENSE','PATENTS','AUTHORS'),
            'webp':('COPYING','PATENTS','AUTHORS')}
    for component,files in grants.items():
        for filename in files:shutil.copy2(source(component)/filename,destination/(component+'-'+filename.replace('.','-')+'.txt'))
    for component,files in {'ffmpeg':('libavcodec/jfdctfst.c','libavcodec/jfdctint_template.c','libavcodec/jrevdct.c'),
                             'quickjs':('quickjs.c','quickjs-libc.c','qjs.c','cutils.h','libregexp.c','libunicode.c','dtoa.c'),
                             'lame':('libmp3lame/lame.c',),'zlib':('zlib.h',)}.items():
        notices=[]
        for filename in files:
            content=(source(component)/filename).read_text(encoding='utf-8')
            if component=='zlib':content=content[:content.index('ZLIB_VERSION')]
            else:content=content.split('#include',1)[0]
            notices.append(filename+'\n'+content)
        (destination/(component+'-SOURCE-NOTICES.txt')).write_text('\n'.join(notices),encoding='utf-8')
    mingw=LLVM.parent/'x86_64-w64-mingw32/share/mingw32'
    shutil.copy2(mingw/'COPYING.MinGW-w64-runtime.txt',destination/'MinGW-w64-runtime-NOTICES.txt')
    shutil.copy2(mingw/'COPYING.winpthreads.txt',destination/'Winpthreads-LICENSE.txt')
    shutil.copy2(LLVM.parent/'LICENSE.TXT',destination/'LLVM-runtime-LICENSE.txt')
    for component,relative in [('ffmpeg','libavutil/x86/x86inc.asm'),('dav1d','src/ext/x86/x86inc.asm'),('vpx','third_party/x86inc/x86inc.asm')]:
        original=source(component)/relative
        if not original.is_file():raise ValueError('Missing assembly notice: '+str(original))
        lines=original.read_text(encoding='utf-8').splitlines()
        end=next(i for i,line in enumerate(lines) if line.strip() and not line.lstrip().startswith(';'))
        (destination/(component+'-x86inc-NOTICE.txt')).write_text('\n'.join(lines[:end])+'\n',encoding='utf-8')
    (destination/'native-source-provenance.json').write_text(json.dumps(lock,indent=2),encoding='utf-8')


def collect(destination, runtime_lock):
    bundle=destination.parent;destination.mkdir(parents=True,exist_ok=True)
    inventory=inspect_bundle(bundle);modules=inventory['embedded_modules']
    assert not any(n=='PyInstaller' or n.startswith(('PyInstaller.','yt_dlp.__pyinstaller')) for n in modules)
    shutil.copy2(ROOT/'LICENSE',destination/'Original-Project-MIT.txt')
    shutil.copy2(ROOT/'redistribution/Inno-Setup-LICENSE.txt',destination/'Inno-Setup-LICENSE.txt')
    collect_native_materials(destination)
    packages={'PySide6':'PySide6','PySide6_Essentials':'PySide6','PySide6_Addons':'PySide6',
              'shiboken6':'shiboken6','yt-dlp':'yt_dlp','yt-dlp-ejs':'yt_dlp_ejs','PyYAML':'yaml',
              'setuptools':'setuptools','packaging':'packaging','altgraph':'altgraph','pefile':'pefile','pywin32-ctypes':'win32ctypes',
              'PyInstaller':None}
    versions={}
    for package,prefix in packages.items():
        if prefix and not any(n==prefix or n.startswith(prefix+'.') for n in modules):continue
        dist=metadata.distribution(package);versions[package]=dist.version
        for file in dist.files or []:
            if any(word in str(file).lower() for word in ('license','copying','notice')):
                if 'commercial' in str(file).lower():continue
                source=dist.locate_file(file)
                if source.is_file():
                    target=destination/package/str(file).replace('..','parent');target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
    runtime_sources=destination/'PyInstaller-runtime';runtime_sources.mkdir(exist_ok=True)
    for member in inventory['bootloader_members']:
        if member.startswith('pyi_rth_'):
            source=Path(metadata.distribution('PyInstaller').locate_file('PyInstaller/hooks/rthooks/'+member+'.py'))
            if source.is_file():shutil.copy2(source,runtime_sources/source.name)
    utilities=Path(metadata.distribution('PyInstaller').locate_file('PyInstaller/fake-modules/_pyi_rth_utils'))
    for source in utilities.rglob('*.py'):
        target=runtime_sources/'_pyi_rth_utils'/source.relative_to(utilities);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
    # MPL-2.0 vendored files, when present, have executable-form source obligations.
    # Retain the exact installed setuptools sources and their original notices.
    if 'setuptools' in versions:
        source_root=Path(metadata.distribution('setuptools').locate_file('setuptools'))
        source_zip=destination/'source-code'/('setuptools-'+versions['setuptools']+'.zip');source_zip.parent.mkdir(exist_ok=True)
        with zipfile.ZipFile(source_zip,'w',zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(source_root.rglob('*')):
                if path.is_file() and '__pycache__' not in path.parts:archive.write(path,'setuptools/'+str(path.relative_to(source_root)))
    # EJS's minified solver embeds complete ISC/MIT notices; retain them separately too.
    solver=(bundle/'_internal/yt_dlp_ejs/yt/solver/lib.min.js').read_text(encoding='utf-8')
    (destination/'EJS-Meriyah-Astring-NOTICES.txt').write_text(solver[:solver.index('*/')+2]+'\n',encoding='utf-8')
    shutil.copy2(Path(sys.base_prefix)/'LICENSE.txt',destination/'Python-LICENSE.txt')
    source_lock=json.loads((ROOT/'build/license-sources.json').read_text(encoding='utf-8'))
    catalog=[]
    for item in source_lock:
        source=fetch_source(item)
        if item.get('source_archive'):
            target=destination/'source-code'/item['name'];target.parent.mkdir(exist_ok=True);shutil.copy2(source,target)
            # Keep component grants and metadata-directed notices, not licenses
            # from every unshipped example/test/platform in the source snapshot.
            with tarfile.open(source) as archive:
                members={m.name:m for m in archive.getmembers() if m.isfile() and '..' not in Path(m.name).parts}
                selected=set()
                for name,member in members.items():
                    parts=Path(name).parts;leaf=parts[-1].lower()
                    if (len(parts)==2 and leaf in ('license','license.md','license.txt','copying','copyright','copying.lgplv2.1','copying.lgplv3','copying.gplv3')
                            or len(parts)==3 and parts[1]=='LICENSES' and leaf in ('lgpl-3.0-only.txt','gpl-3.0-only.txt','apache-2.0.txt')
                            or item['name'].startswith('Python-') and (name.endswith('/Doc/license.rst') or '/Modules/' in name and any(s in name for s in ('/expat/','/libmpdec/','/_hacl/')) and leaf.startswith(('license','copying','copyright')))):
                        selected.add(name)
                    if leaf!='qt_attribution.json':continue
                    relative='/'.join(parts[1:]).lower()
                    if not relative.startswith(('src/','sources/shiboken6/')) or any(s in relative for s in ('/tests/','/examples/','android','wayland','cocoa','macos','xcb','dbus')):continue
                    value=json.loads(archive.extractfile(member).read(),strict=False)
                    entries=value if isinstance(value,list) else [value]
                    entries=[v for v in entries if v.get('QDocModule') in ('qtcore','qtgui','qtnetwork','qtwidgets','qtsvg','qtimageformats','shiboken6') or relative.startswith('sources/shiboken6/')]
                    if not entries:continue
                    selected.add(name)
                    catalog.append({'source':item['name'],'path':name,'scope':'selected Windows module source; target-static inclusion requires build correspondence','attribution':entries})
                    for entry in entries:
                        for field in ('LicenseFile','LicenseFiles','CopyrightFile'):
                            files=entry.get(field,[]);files=[files] if isinstance(files,str) else files
                            for file in files:
                                path=posixpath.normpath(posixpath.join(posixpath.dirname(name),file))
                                if path not in members:raise ValueError('Missing attribution-directed notice: '+path)
                                selected.add(path)
                # Freetype's top-level grant refers to these full license texts.
                selected.update(n for n in members if '/freetype/' in n and n.endswith(('/FTL.TXT','/GPLv2.TXT')))
                for name in sorted(selected):
                    member=members[name];leaf=Path(name).name
                    label=hashlib.sha256(name.encode()).hexdigest()[:12]
                    target=destination/'source-notices'/item['name'].split('-')[0]/(leaf[:40]+'-'+label+('.json' if name.endswith('.json') else '.txt'))
                    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(archive.extractfile(member).read())
        else:shutil.copy2(source,destination/item['name'])
    # Full standard Apache text already comes from the installed packaging license.
    apache=next(destination.rglob('LICENSE.APACHE'),None)
    if apache:shutil.copy2(apache,destination/'Apache-2.0.txt')
    else:
        with tarfile.open(fetch_source(next(i for i in source_lock if i['name'].startswith('qtbase-')))) as archive:
            member=next(m for m in archive if m.name.endswith('LICENSES/Apache-2.0.txt'))
            (destination/'Apache-2.0.txt').write_bytes(archive.extractfile(member).read())
    configuration=subprocess.check_output([str(bundle/'bin/ffmpeg.exe'),'-buildconf'],stderr=subprocess.STDOUT).decode('utf-8',errors='replace')
    (destination/'FFmpeg-buildconf.txt').write_text(configuration,encoding='utf-8')
    (destination/'runtime-provenance.json').write_text(json.dumps(runtime_lock,indent=2),encoding='utf-8')
    (destination/'source-provenance.json').write_text(json.dumps(source_lock,indent=2),encoding='utf-8')
    (destination/'Qt-source-attributions.json').write_text(json.dumps(catalog,indent=2),encoding='utf-8')
    (destination/'bundle-file-inventory.json').write_text(json.dumps(inventory,indent=2),encoding='utf-8')
    (destination/'bundled-package-versions.json').write_text(json.dumps(versions,indent=2),encoding='utf-8')
    shutil.copy2(ROOT/'redistribution/THIRD_PARTY_NOTICES.txt',bundle/'THIRD_PARTY_NOTICES.txt')
    shutil.copytree(ROOT/'redistribution/source-offer',bundle/'source-offer')
    (destination/'bundle-file-inventory.json').write_text(json.dumps(inspect_bundle(bundle),indent=2),encoding='utf-8')
