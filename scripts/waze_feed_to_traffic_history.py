"""Convert a Waze for Cities (WFC) feed snapshot to JalanTanggap traffic_history rows.

Waze WFC GeoRSS/JSON gives jams and irregularities with `speed`, `speedKPH`,
`regularSpeed`, `delay`, `level`, `severity`, `street`, and a coordinate line.
It does NOT provide vehicle volume, so `volume_veh_per_jam` is left empty and
flagged, never guessed.

Usage:
    uv run python scripts/waze_feed_to_traffic_history.py <feed.json> [mapping.csv] [out.csv]

mapping.csv (optional): nama_jalan,id_segmen  - maps Waze street names to the
corridor segment IDs. Without it, id_segmen is left empty for later matching.

Input accepts either a raw WFC JSON payload ({"jams": [...], "irregularities": [...]})
or a file saved with one snapshot per line. Data (c) Waze, used under the
Waze for Cities partner terms; attribute Waze when displaying.
"""
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

FIELDS = ['timestamp', 'id_segmen', 'direction', 'speed_kmh', 'free_flow_speed_kmh',
          'volume_veh_per_jam', 'congestion_index', 'source', 'quality_flag', 'is_simulation']


def load_mapping(path):
    if not path:
        return {}
    out = {}
    with Path(path).open(encoding='utf-8-sig', newline='') as fh:
        for row in csv.DictReader(fh):
            name = (row.get('nama_jalan') or '').strip().lower()
            if name:
                out[name] = row.get('id_segmen', '').strip()
    return out


def midpoint(line):
    pts = [p for p in line if isinstance(p, dict) and 'x' in p and 'y' in p]
    if not pts:
        return None
    return (sum(p['x'] for p in pts) / len(pts), sum(p['y'] for p in pts) / len(pts))


def iso_from_ms(ms):
    if ms in (None, ''):
        return ''
    return datetime.fromtimestamp(int(ms) / 1000, tz=timezone.utc).astimezone().isoformat(timespec='seconds')


def row_from(seg, sid, quality):
    speed = seg.get('speedKPH', seg.get('speed'))
    regular = seg.get('regularSpeed')
    cong = ''
    if regular not in (None, '', 0) and speed not in (None, ''):
        cong = round(max(0.0, min(1.0, 1 - float(speed) / float(regular))), 2)
    return {
        'timestamp': iso_from_ms(seg.get('pubMillis') or seg.get('detectionDateMillis')),
        'id_segmen': sid,
        'direction': seg.get('direction', ''),
        'speed_kmh': '' if speed in (None, '') else round(float(speed), 1),
        'free_flow_speed_kmh': '' if regular in (None, '') else round(float(regular), 1),
        'volume_veh_per_jam': '',
        'congestion_index': cong,
        'source': 'WAZE_WFC',
        'quality_flag': quality,
        'is_simulation': 'False',
    }


def convert(payload, mapping):
    rows = []
    for jam in payload.get('jams', []):
        street = (jam.get('street') or '').strip().lower()
        rows.append(row_from(jam, mapping.get(street, ''), 'waze_jam'))
    for irr in payload.get('irregularities', []):
        street = (irr.get('street') or '').strip().lower()
        rows.append(row_from(irr, mapping.get(street, ''), 'waze_irregularity'))
    return rows


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    feed = Path(sys.argv[1])
    mapping = load_mapping(sys.argv[2] if len(sys.argv) > 2 else None)
    out = Path(sys.argv[3]) if len(sys.argv) > 3 else feed.with_name('traffic_history_from_waze.csv')
    payload = json.loads(feed.read_text(encoding='utf-8'))
    rows = convert(payload, mapping)
    if not rows:
        print('Tidak ada jam/irregularity di feed.')
        return
    with out.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    mapped = sum(1 for r in rows if r['id_segmen'])
    print(f'{len(rows)} baris -> {out.name} | id_segmen terpetakan: {mapped} | volume kosong (Waze tidak menyediakan)')


if __name__ == '__main__':
    main()
