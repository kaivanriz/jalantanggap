"""Shared helpers to convert Waze for Cities (WFC) feed payloads to
JalanTanggap traffic_history rows.

Waze provides `speed`, `speedKPH`, `regularSpeed`, `delay`, `level`,
`severity`, `street`, and a coordinate line, but NOT vehicle volume.
`volume_veh_per_jam` is therefore always left empty, never guessed.

Data (c) Waze, used under the Waze for Cities partner terms; attribute Waze.
Feed spec: https://support.google.com/waze/partners/answer/13458165
"""
import csv
from datetime import datetime, timezone
from pathlib import Path

FIELDS = ['timestamp', 'id_segmen', 'direction', 'speed_kmh', 'free_flow_speed_kmh',
          'volume_veh_per_jam', 'congestion_index', 'source', 'quality_flag', 'is_simulation']

SOURCE = 'WAZE_WFC'


def load_mapping(path):
    """CSV with columns nama_jalan,id_segmen -> {lowercased name: id_segmen}."""
    if not path:
        return {}
    out = {}
    with Path(path).open(encoding='utf-8-sig', newline='') as fh:
        for row in csv.DictReader(fh):
            name = (row.get('nama_jalan') or '').strip().lower()
            if name:
                out[name] = (row.get('id_segmen') or '').strip()
    return out


def midpoint(line):
    pts = [p for p in (line or []) if isinstance(p, dict) and 'x' in p and 'y' in p]
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
        'source': SOURCE,
        'quality_flag': quality,
        'is_simulation': 'False',
    }


def convert(payload, mapping):
    """WFC payload -> list of traffic_history row dicts (jams + irregularities)."""
    rows = []
    for jam in payload.get('jams', []) or []:
        street = (jam.get('street') or '').strip().lower()
        rows.append(row_from(jam, mapping.get(street, ''), 'waze_jam'))
    for irr in payload.get('irregularities', []) or []:
        street = (irr.get('street') or '').strip().lower()
        rows.append(row_from(irr, mapping.get(street, ''), 'waze_irregularity'))
    return rows


def dedupe_key(row):
    return (row['timestamp'], row['id_segmen'], row['quality_flag'],
            row['speed_kmh'], row['free_flow_speed_kmh'], row['congestion_index'])
