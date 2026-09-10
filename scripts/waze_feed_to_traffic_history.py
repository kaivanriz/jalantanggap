"""Convert one Waze for Cities (WFC) feed snapshot to JalanTanggap traffic_history rows.

Usage:
    uv run python scripts/waze_feed_to_traffic_history.py <feed.json> [mapping.csv] [out.csv]

`feed.json` accepts a raw WFC JSON payload ({"jams": [...], "irregularities": [...]})
or a JSON array of such snapshots. Waze does not provide vehicle volume, so
`volume_veh_per_jam` is left empty and flagged, never guessed.

Data (c) Waze, used under the Waze for Cities partner terms; attribute Waze.
For periodic collection, use scripts/collect_waze_feed.py instead.
"""
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from waze_common import FIELDS, convert, load_mapping  # noqa: E402


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    feed = Path(sys.argv[1])
    mapping = load_mapping(sys.argv[2] if len(sys.argv) > 2 else None)
    out = Path(sys.argv[3]) if len(sys.argv) > 3 else feed.with_name('traffic_history_from_waze.csv')
    payload = json.loads(feed.read_text(encoding='utf-8'))
    snapshots = payload if isinstance(payload, list) else [payload]
    rows = []
    for snap in snapshots:
        rows.extend(convert(snap, mapping))
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
