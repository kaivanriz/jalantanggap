"""Run closure scenarios on the real OSM corridor graph (Kota Tangerang).

Trip: west end of "Jalan Muhammad Thoha" (= Jalan Raya M. Toha, per OSM)
toward the Iskandar Muda area in Neglasari, approximating the documented
home trip M. Toha -> Rajeg. Closure model per scenario:

- partial: sort each work's mapped ways along its dominant axis and block the
  middle third (a work segment in the middle of the road),
- full: block every mapped way (over-conservative; shown to explain why
  segment boundaries matter - the news says no road is fully closed).

Checks per scenario: does a route survive; does it use the official detour
streets (Aria Wangsakara / Aria Santika); does it cross OTHER active works
(conflict flag). Distances are proxies; no traffic volumes are used.
"""
import csv
import heapq
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'data' / 'real-tangerang'
OSM = ROOT / 'osm'
DETOUR_KEYS = ('wangsakara', 'santika')
SCENARIOS = {
    'S0_tanpa_penutupan': {'partial': [], 'full': []},
    'S1_mtoha_sebagian': {'partial': ['CT01'], 'full': []},
    'S2_alternatif_ikut_dikerjakan': {'partial': ['CT01', 'SIM99'], 'full': []},
    'S3_semua_pekerjaan_asli_sebagian': {'partial': ['CT01', 'CT02', 'CT03', 'CT04'], 'full': []},
    'S4_semua_penutupan_total': {'partial': [], 'full': ['CT01', 'CT02', 'CT03', 'CT04']},
}


def load():
    nodes = {}
    with (OSM / 'koridor_nodes.csv').open(encoding='utf-8', newline='') as fh:
        for r in csv.DictReader(fh):
            nodes[r['id']] = (float(r['lon']), float(r['lat']))
    adj = {}
    way_edges = {}
    way_names = {}
    with (OSM / 'koridor_edges.csv').open(encoding='utf-8', newline='') as fh:
        for r in csv.DictReader(fh):
            if not r['osm_id']:
                continue
            adj.setdefault(r['from'], []).append(
                (r['to'], float(r['length_m']), r['name'], r['osm_id']))
            way_edges.setdefault(r['osm_id'], []).append((r['from'], r['to']))
            way_names.setdefault(r['osm_id'], r['name'])
    return nodes, adj, way_edges, way_names


def road_nodes(nodes, adj, alias):
    hits = set()
    for u, edges in adj.items():
        for v, _, nm, _ in edges:
            if alias.lower() in nm.lower():
                hits.add(u)
                hits.add(v)
    return [n for n in hits if n in nodes]


def way_centroids(nodes, way_edges):
    pts = {}
    for sid, pairs in way_edges.items():
        for u, v in pairs:
            pts.setdefault(sid, []).extend([nodes[u], nodes[v]])
    return {sid: (sum(p[0] for p in ps) / len(ps), sum(p[1] for p in ps) / len(ps))
            for sid, ps in pts.items()}


def middle_third(ways, centroids):
    """Sort ways along the dominant axis of their centroids and drop the ends,
    keeping the middle third (at least one way)."""
    if len(ways) <= 1:
        return list(ways)
    xs = [centroids[w][0] for w in ways]
    ys = [centroids[w][1] for w in ways]
    key = 0 if (max(xs) - min(xs)) >= (max(ys) - min(ys)) else 1
    ordered = sorted(ways, key=lambda w: centroids[w][key])
    cut = max(1, len(ordered) // 3)
    return ordered[cut:len(ordered) - cut] or ordered[cut:cut + 1]


def dijkstra(adj, start, goal, blocked):
    pq = [(0.0, start, [], [])]
    seen = set()
    while pq:
        dist, node, path, sids = heapq.heappop(pq)
        if node == goal:
            return dist, path, sids
        if node in seen:
            continue
        seen.add(node)
        for to, ln, nm, sid in adj.get(node, []):
            if (node, to) in blocked or to in seen:
                continue
            heapq.heappush(pq, (dist + ln, to, path + [nm], sids + [sid]))
    return None, None, None


def main():
    nodes, adj, way_edges, way_names = load()
    mapping = {m['id_pekerjaan']: set(m['osm_ids']) for m in
               json.loads((ROOT / 'pemetaan_pekerjaan_osm.json')
                          .read_text(encoding='utf-8'))['pekerjaan']}
    # Pseudo-work SIM99: "jalur alternatif ikut diperbaiki" - a SIMULATION of
    # the bad-luck case from the story (closure of the middle of Aria Santika).
    mapping['SIM99'] = {sid for sid, nm in way_names.items()
                        if 'aria santika' in nm.lower()}
    centroids = way_centroids(nodes, way_edges)
    blocked_by_work = {}
    for cid, ways in mapping.items():
        present = [w for w in ways if w in way_edges]
        mid = middle_third(present, centroids)
        b_partial = {e for w in mid for e in way_edges[w]}
        b_full = {e for w in present for e in way_edges[w]}
        blocked_by_work[cid] = {'partial': b_partial, 'full': b_full,
                                'way_total': len(present), 'way_tengah': len(mid)}
    thoha = road_nodes(nodes, adj, 'Muhammad Thoha')
    santika = road_nodes(nodes, adj, 'Jalan Aria Santika')
    wangsakara = road_nodes(nodes, adj, 'Jalan Aria Wangsakara')
    origin = min(thoha, key=lambda n: nodes[n][0])
    dest = max(santika, key=lambda n: nodes[n][0])
    wnode = min(wangsakara, key=lambda n: nodes[n][0])
    snode = max(santika, key=lambda n: nodes[n][0])
    results = []
    base = None
    for name, spec in SCENARIOS.items():
        blocked = set()
        for cid in spec['partial']:
            blocked |= blocked_by_work[cid]['partial']
        for cid in spec['full']:
            blocked |= blocked_by_work[cid]['full']
        closed_ids = spec['partial'] + spec['full']
        other_active = set()
        for cid, b in blocked_by_work.items():
            if cid not in closed_ids:
                other_active |= {s for pair in b['partial'] for s in pair}
        other_way_ids = set()
        for cid, ways in mapping.items():
            if cid not in closed_ids and cid != 'SIM99':
                other_way_ids |= ways
        dist, path, sids = dijkstra(adj, origin, dest, blocked)
        r = {'skenario': name, 'sebagian': spec['partial'], 'total': spec['full'],
             'edge_diblokir': len(blocked)}
        if dist is None:
            r.update({'rute': False,
                      'catatan': 'tidak ada rute; penutupan total seluruh way lebih '
                                 'berat dari kondisi berita (tidak ada penutupan penuh)'})
            results.append(r)
            print(f'{name}: TIDAK ADA RUTE (blokir {len(blocked)} edge)')
            continue
        streets = [s for s in dict.fromkeys(path) if s]
        detour = [s for s in streets if any(k in s.lower() for k in DETOUR_KEYS)]
        d1, _, _ = dijkstra(adj, origin, wnode, blocked)
        d2, _, _ = dijkstra(adj, wnode, snode, blocked)
        d3, _, _ = dijkstra(adj, snode, dest, blocked)
        official = (round((d1 + d2 + d3) / 1000, 2)
                    if None not in (d1, d2, d3) else None)
        conflict = sorted({s for s in sids if s in other_way_ids})
        hits_names = sorted({nm for sid, nm in zip(sids, path) if sid in other_way_ids})
        if base is None:
            base = dist
        r.update({'rute': True, 'jarak_km': round(dist / 1000, 2),
                  'delta_km': round((dist - base) / 1000, 2),
                  'jalur_resmi_km': official,
                  'jalan_dilalui': streets, 'detour_resmi_terpakai': detour,
                  'konflik': {'jumlah_way_pekerjaan_lain': len(conflict),
                              'nama_jalan': hits_names}})
        results.append(r)
        flag = (f'KONFLIK: menembus {len(conflict)} way pekerjaan lain '
                f'({", ".join(hits_names[:3])})') if conflict else 'tanpa konflik'
        print(f"{name}: {dist/1000:.2f} km (+{(dist-base)/1000:.2f}) | "
              f"jalur resmi: {official if official is not None else 'terputus'} km | {flag}")
    out = OSM / 'skenario_penutupan.json'
    out.write_text(json.dumps({
        'sumber': {'graf': 'koridor_nodes.csv + koridor_edges.csv (OSM)',
                   'pekerjaan': 'pekerjaan_resmi.csv (berita Pemkot Tangerang)',
                   'pemetaan': 'pemetaan_pekerjaan_osm.json'},
        'asal': {'node': origin, 'label': 'ujung barat Jalan Muhammad Thoha (M. Toha)', 'koordinat_lonlat': list(nodes[origin])},
        'tujuan': {'node': dest, 'label': 'ujung timur Jalan Aria Santika (titik temu jalur resmi ke arah Otista)', 'koordinat_lonlat': list(nodes[dest])},
        'model_penutupan': {
            cid: {'way_dipetakan': b['way_total'], 'way_tengah_ditutup': b['way_tengah']}
            for cid, b in blocked_by_work.items()},
        'perhatian': ['jalur_resmi_km: rute paksa origin -> Aria Wangsakara -> '
                      'Aria Santika -> dest (3 kaki Dijkstra); "terputus" berarti '
                      'akses/pintu jalur resmi ikut terhalang penutupan.',
                      'SIM99 = penutupan separuh Jalan Aria Santika untuk mensimulasikan '
                      '"alternatifnya juga diperbaiki"; bukan pekerjaan resmi.',
                      'Way "tengah" = sepertiga tengah urutan centroid searah sumbu '
                      'dominan; pendekatan kasar untuk demo, bukan batas lapangan.',
                      'Jarak = proksi geometrik; tanpa volume lalu lintas tidak ada '
                      'prediksi kemacetan.',
                      'S0 tetap memakai jalan pekerjaan (sesuai berita: tidak ada '
                      'penutupan total).'],
        'hasil': results}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('ditulis:', out.name)


if __name__ == '__main__':
    main()
