"""Export Fase 4 feature rows (work -> candidate affected segments) from the
real OSM corridor graph.

Targets: one row per (pekerjaan, segmen penerima) within HOPS, with graph
features required by AI-Traffic-Impact.md section 12. Traffic columns
(volume/speed/congestion) stay empty because no real traffic data exists yet;
this is explicit and documented, not filled with guesses.
"""
import csv
import json
from collections import defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'data' / 'real-tangerang'
OSM = ROOT / 'osm'
HOPS = 3
MAX_PER_WORK = 250


def load():
    nodes = {}
    with (OSM / 'koridor_nodes.csv').open(encoding='utf-8', newline='') as fh:
        for r in csv.DictReader(fh):
            nodes[r['id']] = (float(r['lon']), float(r['lat']))
    edges = {}
    node_edges = defaultdict(list)
    with (OSM / 'koridor_edges.csv').open(encoding='utf-8', newline='') as fh:
        for r in csv.DictReader(fh):
            if not r['osm_id']:
                continue
            edges[(r['from'], r['to'])] = r
            node_edges[r['from']].append(r)
            node_edges[r['to']].append(r)
    return nodes, edges, node_edges


def main():
    nodes, edges, node_edges = load()
    mapping = json.loads((ROOT / 'pemetaan_pekerjaan_osm.json')
                         .read_text(encoding='utf-8'))['pekerjaan']
    rows = []
    for work in mapping:
        way_ids = set(work['osm_ids'])
        start_nodes = {n for (a, b), r in edges.items() if r['osm_id'] in way_ids for n in (a, b)}
        dist = {n: 0 for n in start_nodes}
        queue = deque(start_nodes)
        while queue:
            n = queue.popleft()
            if dist[n] >= HOPS:
                continue
            for r in node_edges.get(n, []):
                for m in (r['from'], r['to']):
                    if m not in dist:
                        dist[m] = dist[n] + 1
                        queue.append(m)
        targets = {}
        for (a, b), r in edges.items():
            if r['osm_id'] in way_ids:
                continue
            hop = min(dist.get(a, 99), dist.get(b, 99))
            if hop > HOPS:
                continue
            key = (r['osm_id'], r['name'])
            if key not in targets or hop < targets[key]['hop']:
                targets[key] = {'hop': hop, 'length_m': r['length_m'],
                                'road_class': r['highway'], 'name': r['name']}
        ordered = sorted(targets.items(), key=lambda kv: (kv[1]['hop'], -float(kv[1]['length_m'])))
        for (sid, name), t in ordered[:MAX_PER_WORK]:
            rows.append(dict(
                id_pekerjaan=work['id_pekerjaan'], nama_pekerjaan=work['pekerjaan'],
                target_segment=sid, target_nama=name, hop_dari_pekerjaan=t['hop'],
                panjang_m=t['length_m'], road_class=t['road_class'],
                jumlah_lajur='', volume_baseline='', speed_baseline='',
                delta_volume='', delta_speed='', congestion='',
                catatan='volume/speed/congestion kosong: data lalu lintas nyata belum tersedia'))
    out = ROOT / 'traffic_ai_features.csv'
    with out.open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    per_work = defaultdict(int)
    for r in rows:
        per_work[r['id_pekerjaan']] += 1
    print(f'{len(rows)} baris fitur -> {out.name}')
    for k, v in per_work.items():
        print(f'  {k}: {v} segmen penerima (<= {HOPS} hop)')


if __name__ == '__main__':
    main()
