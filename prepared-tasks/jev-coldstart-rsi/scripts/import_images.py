#!/usr/bin/env python3
"""Safely import the frozen image selection; report and retain byte duplicates."""
import argparse
import hashlib
import io
import json
import sys
import tarfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.task import ROOT, read_jsonl, write_json


def import_selected(archive_path, root=ROOT, expected_count=3560):
    from PIL import Image
    root = Path(root)
    requests = read_jsonl(root / 'data/public/image-requests.jsonl')
    wanted = {r['source_path']: r for r in requests}
    if len(wanted) != len(requests) or len(wanted) != expected_count:
        raise ValueError('Unexpected or duplicate image request manifest')
    found, pixel_groups = {}, {}
    with tarfile.open(archive_path, 'r|*') as archive:
        for member in archive:
            name = Path(member.name).name
            if name not in wanted:
                continue
            if not member.isfile() or not 0 < member.size <= 16 * 1024 * 1024:
                raise ValueError('Invalid selected tar member')
            if name in found:
                raise ValueError('Duplicate selected archive member')
            row = wanted[name]
            if Path(row['asset']).name != row['asset']:
                raise ValueError('Invalid destination asset basename')
            f = archive.extractfile(member)
            if f is None:
                raise ValueError('Unreadable member')
            payload = f.read()
            with Image.open(io.BytesIO(payload)) as image:
                image.verify()
            h = hashlib.sha256(payload).hexdigest()
            pixel_groups.setdefault(h, []).append({'asset': row['asset'], 'split': row['split']})
            dest = root / 'data/public/images' / row['asset']
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(payload)
            found[name] = {'asset': row['asset'], 'split': row['split'], 'bytes': len(payload), 'sha256': h}
    missing = set(wanted) - set(found)
    report = {'status': 'complete' if not missing else 'incomplete', 'expected': len(wanted), 'imported': len(found),
              'missing_source_paths': sorted(missing), 'files': sorted(found.values(), key=lambda r: r['asset']),
              'duplicate_byte_groups': [{'sha256': h, 'records': rows} for h, rows in sorted(pixel_groups.items()) if len(rows) > 1],
              'duplicate_policy': 'retain every frozen record; duplicates are disclosed, not excluded'}
    write_json(root / 'evidence/image-manifest.json', report)
    if missing:
        raise ValueError(f'{len(missing)} selected images missing; no placeholder substitution or reduced cohort allowed')
    return report


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--archive', required=True); a = p.parse_args()
    result = import_selected(a.archive)
    print(json.dumps({'status': result['status'], 'images': result['imported']}))
