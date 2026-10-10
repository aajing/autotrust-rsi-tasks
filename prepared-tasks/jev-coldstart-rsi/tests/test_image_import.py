"""Exercise duplicate retention and missing-asset failure with tiny local PNGs."""
import io
import json
import tarfile
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from scripts.import_images import import_selected


class ImageImportTests(unittest.TestCase):
    def fixture(self, directory, names):
        root = Path(directory)
        public = root / 'data/public'; public.mkdir(parents=True)
        rows = [{'source_path': 'one.png', 'asset': 'asset-one.png', 'split': 'train'},
                {'source_path': 'two.png', 'asset': 'asset-two.png', 'split': 'evaluation'}]
        (public / 'image-requests.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in rows))
        b = io.BytesIO(); Image.new('RGB', (2, 2), (12, 34, 56)).save(b, format='PNG'); payload = b.getvalue()
        archive = root / 'fixture.tar'
        with tarfile.open(archive, 'w') as tar:
            for name in names:
                member = tarfile.TarInfo('nested/' + name); member.size = len(payload)
                tar.addfile(member, io.BytesIO(payload))
        return root, archive

    def test_same_bytes_across_partitions_preserve_every_record(self):
        with tempfile.TemporaryDirectory() as d:
            root, archive = self.fixture(d, ['one.png', 'two.png'])
            report = import_selected(archive, root, expected_count=2)
            self.assertEqual(report['status'], 'complete')
            self.assertEqual(report['imported'], 2)
            self.assertEqual(len(report['files']), 2)
            self.assertEqual(len(report['duplicate_byte_groups']), 1)
            self.assertEqual({r['split'] for r in report['duplicate_byte_groups'][0]['records']}, {'train', 'evaluation'})
            self.assertTrue(all((root / 'data/public/images' / r['asset']).is_file() for r in report['files']))

    def test_missing_pixels_never_become_reduced_cohort(self):
        with tempfile.TemporaryDirectory() as d:
            root, archive = self.fixture(d, ['one.png'])
            with self.assertRaises(ValueError): import_selected(archive, root, expected_count=2)
            report = json.loads((root / 'evidence/image-manifest.json').read_text())
            self.assertEqual(report['status'], 'incomplete')
            self.assertEqual(report['missing_source_paths'], ['two.png'])

    def test_duplicate_archive_member_is_not_a_new_item(self):
        with tempfile.TemporaryDirectory() as d:
            root, archive = self.fixture(d, ['one.png', 'one.png', 'two.png'])
            with self.assertRaises(ValueError): import_selected(archive, root, expected_count=2)


if __name__ == '__main__': unittest.main()
