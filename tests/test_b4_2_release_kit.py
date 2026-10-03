import hashlib,json,os,shutil,subprocess,tempfile,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


class ReleaseKitTests(unittest.TestCase):
    def collect(self,directory,*args):
        result=subprocess.run(['powershell.exe','-NoProfile','-File',str(ROOT/'release-test/clean_machine_test.ps1'),
                               '-OutputDirectory',str(directory),*args],capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr.decode(errors='replace'))
        files=list(Path(directory).rglob('clean-machine-report.json'));self.assertEqual(len(files),1)
        return json.loads(files[0].read_text(encoding='utf-8-sig'))

    def test_preflight_never_claims_functional_or_independent_pass(self):
        before=os.environ['PATH']
        with tempfile.TemporaryDirectory() as tmp:
            report=self.collect(tmp,'-Stage','collector-self-test')
        self.assertEqual(set(report['Dependencies']),{'python','py','yt-dlp','ffmpeg','ffprobe','qjs'})
        self.assertEqual(report['Dependencies']['qjs']['Command'],'where.exe qjs')
        self.assertEqual(report['Stage'],'collector-self-test')
        self.assertTrue(all('ExitCode' in v and 'Paths' in v for v in report['Dependencies'].values()))
        self.assertTrue(report['CleanMachine'].startswith('NOT TESTED'))
        self.assertTrue(report['IndependentEnvironment'].startswith('NOT VERIFIED'))
        self.assertEqual(report['SystemChanges'],'NONE');self.assertEqual(os.environ['PATH'],before)

    def test_missing_application_is_reported_without_crashing(self):
        with tempfile.TemporaryDirectory() as tmp:
            report=self.collect(Path(tmp)/'reports','-PortableRoot',str(Path(tmp)/'missing app'))
        self.assertEqual(report['RuntimeDiagnostics'][0]['Status'],'EXECUTABLE NOT FOUND')
        self.assertEqual(report['RuntimeDiagnostics'][0]['PathsWithinRoot'],{})

    def test_checksum_collection_detects_a_changed_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            kit=Path(tmp);script=kit/'clean_machine_test.ps1'
            shutil.copy2(ROOT/'release-test/clean_machine_test.ps1',script)
            good=b'original';digest=hashlib.sha256(good).hexdigest()
            (kit/'MediaDownloader-Portable.zip').write_bytes(good)
            (kit/'MediaDownloader-Setup.exe').write_bytes(b'changed')
            (kit/'checksums.txt').write_text(''.join(digest+'  '+n+'\n' for n in ('MediaDownloader-Portable.zip','MediaDownloader-Setup.exe')))
            result=subprocess.run(['powershell.exe','-NoProfile','-File',str(script),'-OutputDirectory',str(kit/'reports')],capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr.decode(errors='replace'))
            report=json.loads(next((kit/'reports').rglob('clean-machine-report.json')).read_text(encoding='utf-8-sig'))
            self.assertEqual([r['Match'] for r in report['ArtifactChecksums']],[True,False])


if __name__=='__main__':unittest.main()
