"""RC metadata, icons, pinned native files and copied test-kit validation."""
import hashlib,json,struct,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pefile
from PySide6.QtGui import QImage
from app.version import PRODUCT,VERSION,WINDOWS_VERSION
from release_licenses import sha
from validate_b4_1_artifacts import run

root=Path(__file__).resolve().parents[1];out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
run(Path(sys.argv[1]),out/'artifact-validation.json')
release=root/'dist/release';bundle=root/'dist/MediaDownloader';lock=json.loads((root/'build/runtime-lock.json').read_text())
result={}
for name in ('MediaDownloader.exe','MediaDownloader-Setup.exe'):
    pe=pefile.PE(str(bundle/name if name=='MediaDownloader.exe' else release/name));texts={}
    for block in pe.FileInfo:
        for entry in block:
            if hasattr(entry,'StringTable'):
                for table in entry.StringTable:texts.update({k.decode():v.decode().strip() for k,v in table.entries.items()})
    assert texts['ProductName']==PRODUCT and texts['ProductVersion']==VERSION
    fixed=pe.VS_FIXEDFILEINFO[0]
    assert (fixed.FileVersionMS>>16,fixed.FileVersionMS&65535,fixed.FileVersionLS>>16,fixed.FileVersionLS&65535)==WINDOWS_VERSION
    resources=[r.id for r in pe.DIRECTORY_ENTRY_RESOURCE.entries]
    assert 3 in resources and 14 in resources and pe.OPTIONAL_HEADER.Subsystem==2
    result[name]={'strings':texts,'subsystem':'WINDOWS_GUI','icon_resources':True,'numeric_version':WINDOWS_VERSION}
for name,digest in lock['ffmpeg']['files'].items():assert sha(bundle/'bin'/name)==digest
assert sha(bundle/'bin/runtime/qjs.exe')==lock['quickjs']['sha256']
def pixels(file):
    data=file.read_bytes();frames=[]
    for i in range(struct.unpack_from('<H',data,4)[0]):
        *_,length,offset=struct.unpack_from('<BBBBHHII',data,6+16*i)
        image=QImage.fromData(data[offset:offset+length]);assert not image.isNull()
        frames.append((image.width(),image.height(),hashlib.sha256(bytes(image.constBits())).hexdigest()))
    return frames
# Qt can write different PNG physical-DPI metadata before/after QApplication;
# icon image sizes and actual pixels must match.
assert pixels(bundle/'_internal/app.ico')==pixels(root/'build/app.ico')
origin=json.loads((root/'build/installer-language-source.json').read_text())
assert sha(bundle/'SOURCES/Installer/ChineseSimplified.isl')==origin['sha256']
assert hashlib.sha256(subprocess.check_output(['git','show','HEAD:build/ChineseSimplified.isl'],cwd=root)).hexdigest()==origin['sha256']
for name in ('MediaDownloader-Portable.zip','MediaDownloader-Setup.exe','checksums.txt','release-manifest.json','RELEASE_NOTES_0.9.0-rc1.md'):
    assert sha(release/name)==sha(root/'release-test'/name)
result.update(native_runtime_hashes_unchanged=True,kit_identical=True,upstream_language_exact=True,icon_pixels=pixels(bundle/'_internal/app.ico'))
(out/'product-metadata.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(result))
