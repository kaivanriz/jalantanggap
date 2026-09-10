"""Validate relational fixtures and actual route outcomes without dependencies.

Covers Phase 1 tables plus Fase 4 datasets: traffic_history, roadworks_events,
and traffic_ai_dataset (baseline vs event pairing).
"""
import csv
import heapq
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'data' / 'sample-tangerang'


def load(name):
    with (ROOT / f'{name}.csv').open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def main():
    manifest = json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
    tables = {name: load(name) for name in manifest['counts']}
    for name, rows in tables.items():
        assert len(rows) == manifest['counts'][name], name
        assert all(None not in row and None not in row.values() for row in rows), name
        assert all(row['is_simulation'] == 'True' for row in rows), name

    nodes = {n['id_node'] for n in tables['nodes']}
    segments = {e['id_segmen']: e for e in tables['segmen']}
    projects = {p['id_proyek'] for p in tables['proyek']}
    reports = {r['id_laporan']: r for r in tables['laporan']}
    assert len(reports) == 100 and len(segments) == 40 and len(nodes) == 25
    for e in segments.values():
        assert e['from_node'] in nodes and e['to_node'] in nodes
        assert float(e['panjang_m']) > 0
        assert int(e['jumlah_lajur']) >= 1

    for name in ['laporan', 'penilaian', 'pembatasan', 'aktivitas']:
        for row in tables[name]:
            assert not row['id_segmen'] or row['id_segmen'] in segments

    # Phase 1: duplicate clusters must share the same segment.
    clusters = {}
    for r in reports.values():
        cid = r['id_cluster_duplikat']
        if cid:
            clusters.setdefault(cid, []).append(r)
    for cid, rows in clusters.items():
        segs = {r['id_segmen'] for r in rows}
        assert len(segs) == 1, f'cluster {cid} lintas segmen'
    for label in tables['label_llm']:
        assert label['id_laporan'] in reports

    closures = {b['id_pembatasan']: b for b in tables['pembatasan']}
    for b in closures.values():
        assert b['id_proyek'] in projects
    for name in ['pembatasan', 'aktivitas']:
        for row in tables[name]:
            assert datetime.fromisoformat(row['mulai']) < datetime.fromisoformat(row['selesai'])

    # Fase 4: traffic_history time-series shape.
    th = tables['traffic_history']
    assert th, 'traffic_history kosong'
    valid_flags = {'ok', 'penutupan_total', 'lajur_ditutup', 'penerima_pengalihan'}
    for row in th:
        datetime.fromisoformat(row['timestamp'])
        assert row['id_segmen'] in segments
        assert row['direction'] in ('forward', 'reverse')
        assert float(row['free_flow_speed_kmh']) > 0
        assert 0 <= float(row['congestion_index']) <= 1
        assert all(f in valid_flags for f in row['quality_flag'].split('+')), row['quality_flag']

    # Fase 4: roadworks events.
    events = {e['id_event']: e for e in tables['roadworks_events']}
    assert events, 'roadworks_events kosong'
    for ev in events.values():
        assert datetime.fromisoformat(ev['waktu_mulai']) < datetime.fromisoformat(ev['waktu_selesai'])
        assert ev['id_segmen_pekerjaan'] in segments
        for t in ev['segmen_terdampak'].split(';'):
            assert t in segments
        assert int(ev['jumlah_lajur_ditutup']) >= 1

    # Fase 4: AI dataset must pair baseline vs event and include targets.
    ai = tables['traffic_ai_dataset']
    assert ai, 'traffic_ai_dataset kosong'
    seen_pairs = set()
    for row in ai:
        assert row['id_event'] in events
        assert row['target_segment'] in segments
        assert int(row['hop_dari_pekerjaan']) >= 0
        float(row['delta_volume']); float(row['delta_speed'])
        assert row['congestion'] in ('0', '1')
        seen_pairs.add((row['id_event'], row['target_segment'], row['direction'], row['jam']))
    assert len(seen_pairs) == len(ai), 'ada pasangan duplikat di traffic_ai_dataset'
    closed = [r for r in ai if r['target_segment'] == events['RV01']['id_segmen_pekerjaan']]
    assert closed and all(float(r['delta_volume']) <= 0 for r in closed), \
        'segmen ditutup seharusnya volume turun/tidak naik'

    settings = json.loads((ROOT/'aturan.json').read_text(encoding='utf-8'))
    assert abs(sum(settings['weights'].values()) - 1) < 1e-9

    output = []
    for case in json.loads((ROOT/'skenario.json').read_text(encoding='utf-8')):
        time = datetime.fromisoformat(case['waktu'])
        active = [closures[k] for k in case['closures']
                  if datetime.fromisoformat(closures[k]['mulai']) <= time
                  < datetime.fromisoformat(closures[k]['selesai'])]
        blocked = {b['id_segmen'] for b in active if b['jenis'] == 'total'}
        adjacency = {n: [] for n in nodes}
        for e in segments.values():
            if e['id_segmen'] in blocked or settings['vehicle'] not in e['kendaraan'].split(';'):
                continue
            u, v = e['from_node'], e['to_node']
            adjacency[u].append((v, int(e['panjang_m']), e['id_segmen']))
            if e['arah'] == 'both':
                adjacency[v].append((u, int(e['panjang_m']), e['id_segmen']))
        queue = [(0, settings['origin'], [])]
        visited = set()
        result = None
        while queue:
            distance, node, path = heapq.heappop(queue)
            if node in visited:
                continue
            visited.add(node)
            if node == settings['destination']:
                result = dict(distance_m=distance, segments=path)
                break
            for neighbor, length, sid in adjacency[node]:
                heapq.heappush(queue, (distance + length, neighbor, path + [sid]))
        assert (result is not None) == case['expected_route'], case['id']
        if result:
            assert not blocked.intersection(result['segments'])
        output.append(dict(scenario=case['id'], route=result, is_simulation=True))

    geo = json.loads((ROOT/'jaringan.geojson').read_text(encoding='utf-8'))
    assert len(geo['features']) == len(segments)
    (ROOT/'hasil_validasi.json').write_text(
        json.dumps(dict(status='passed', scenarios=output), indent=2) + '\n', encoding='utf-8')
    print('PASS: CSV, relasi ID, cluster duplikat, time-series traffic, event, '
          'dataset AI, bobot, GeoJSON, dan 4 skenario rute.')


if __name__ == '__main__':
    main()
