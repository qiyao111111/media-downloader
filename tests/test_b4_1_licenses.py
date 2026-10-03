import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import release_licenses as licenses


class LicenseSourcesTests(unittest.TestCase):
    def test_verified_cache_needs_no_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);cache=root/'.tools/license-sources';cache.mkdir(parents=True)
            source=cache/'license.txt';source.write_bytes(b'original license')
            item={'name':source.name,'url':'https://example.invalid/license','sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
            with patch.object(licenses,'ROOT',root),patch.object(licenses.urllib.request,'urlopen',side_effect=AssertionError('unexpected network')):
                self.assertEqual(licenses.fetch_source(item),source)

    def test_bad_download_preserves_cache_and_removes_temporary(self):
        import io
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);cache=root/'.tools/license-sources';cache.mkdir(parents=True)
            source=cache/'license.txt';source.write_bytes(b'old cache')
            item={'name':source.name,'url':'https://example.invalid/license','sha256':'0'*64}
            with patch.object(licenses,'ROOT',root),patch.object(licenses.urllib.request,'urlopen',return_value=io.BytesIO(b'wrong source')):
                with self.assertRaisesRegex(ValueError,'checksum mismatch'):licenses.fetch_source(item)
            self.assertEqual(source.read_bytes(),b'old cache')
            self.assertFalse(source.with_suffix('.txt.tmp').exists())

    def test_bad_cache_replaced_only_after_verification(self):
        import io
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);cache=root/'.tools/license-sources';cache.mkdir(parents=True)
            source=cache/'license.txt';source.write_bytes(b'corrupt cache')
            data=b'verified source'
            item={'name':source.name,'url':'https://example.invalid/license','sha256':hashlib.sha256(data).hexdigest()}
            with patch.object(licenses,'ROOT',root),patch.object(licenses.urllib.request,'urlopen',return_value=io.BytesIO(data)):
                self.assertEqual(licenses.fetch_source(item).read_bytes(),data)


if __name__=='__main__':unittest.main()
