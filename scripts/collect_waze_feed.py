"""Collect Waze for Cities (WFC) feed snapshots periodically into a
traffic_history CSV, building history that Waze itself does not provide.

Waze shares real-time feeds only; the partner is responsible for storing them.
This script polls the feed URL on an interval and appends de-duplicated rows.

Usage:
    uv run python scripts/collect_waze_feed.py --url "<feed-url>" [options]

Options:
    --url URL          WFC feed URL (from Partner Hub > Toolbox > Waze Data Feed).
                       Can also be set via the WAZE_FEED_URL environment variable.
    --mapping CSV      nama_jalan,id_segmen mapping (optional).
    --out CSV          Output file (default data/real-tangerang/traffic_history_waze.csv).
    --interval SECONDS Seconds between polls (default 300 = 5 minutes).
    --iterations N     Number of polls; 0 = run forever (default 0).
    --timeout SECONDS  Per-request timeout (default 30).

Notes:
    - `volume_veh_per_jam` is always empty: Waze does not provide vehicle volume.
    - Rows are de-duplicated on (timestamp, id_segmen, quality_flag, speed, free_flow, congestion).
    - The feed URL contains a secret token; do not commit it. Keep it in the
      environment variable or pass it on the command line only.
    - Data (c) Waze, used under the Waze for Cities partner terms; attribute Waze.

Example (test without a real token, using the bundled example):
    uv run python scripts/collect_waze_feed.py --url "file://data/sample-tangerang/waze_feed_contoh.json" --iterations 1 --interval 0
"""
import argparse
import csv
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from waze_common import FIELDS, convert, dedupe_key, load_mapping  # noqa: E402


def fetch(url, timeout):
    if url.startswith('file://'):
        path = Path(url[7:])
        return json.loads(path.read_text(encoding='utf-8'))
    req = urllib.request.Request(url, headers={'User-Agent': 'JalanTanggap-WFC-collector/0.1'})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode('utf-8'))


def load_seen(path):
    if not path.exists():
        return set()
    seen = set()
    with path.open(encoding='utf-8', newline='') as fh:
        for row in csv.DictReader(fh):
            seen.add((row['timestamp'], row['id_segmen'], row['quality_flag'],
                      row['speed_kmh'], row['free_flow_speed_kmh'], row['congestion_index']))
    return seen


def append_rows(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    new_file = not path.exists()
    with path.open('a', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        if new_file:
            writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description='Collect Waze for Cities feed snapshots.')
    parser.add_argument('--url', default=os.environ.get('WAZE_FEED_URL', ''))
    parser.add_argument('--mapping', default=None)
    parser.add_argument('--out', default='data/real-tangerang/traffic_history_waze.csv')
    parser.add_argument('--interval', type=int, default=300)
    parser.add_argument('--iterations', type=int, default=0)
    parser.add_argument('--timeout', type=int, default=30)
    args = parser.parse_args()

    if not args.url:
        parser.error('--url wajib diisi (atau set WAZE_FEED_URL). Token feed bersifat rahasia.')

    mapping = load_mapping(args.mapping)
    out = Path(args.out)
    seen = load_seen(out)
    print(f'Mulai mengumpulkan. interval={args.interval}s, iterations={args.iterations or "tak terbatas"}')
    print(f'Output: {out} | id_segmen terpetakan awal: {len(mapping)} nama jalan')

    count = 0
    total_new = 0
    while args.iterations == 0 or count < args.iterations:
        count += 1
        try:
            payload = fetch(args.url, args.timeout)
        except Exception as exc:
            print(f'[{count}] gagal mengambil feed: {exc}')
            if args.iterations and count >= args.iterations:
                break
            time.sleep(max(1, args.interval))
            continue
        snapshots = payload if isinstance(payload, list) else [payload]
        rows = []
        for snap in snapshots:
            rows.extend(convert(snap, mapping))
        fresh = []
        for row in rows:
            key = dedupe_key(row)
            if key not in seen:
                seen.add(key)
                fresh.append(row)
        if fresh:
            append_rows(out, fresh)
            total_new += len(fresh)
        print(f'[{count}] feed: {len(rows)} baris, baru: {len(fresh)}, total baru: {total_new}')
        if args.iterations and count >= args.iterations:
            break
        time.sleep(max(1, args.interval))

    print(f'Selesai. {total_new} baris baru ditambahkan ke {out}')


if __name__ == '__main__':
    main()
