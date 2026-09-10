"""Route on the real OSM corridor graph between two coordinates.

Prints the streets used, so we can see whether the official detour streets
(Aria Wangsakara / Aria Santika) appear in a real shortest path.
"""
import csv
import heapq
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'data' / 'real-tangerang' / 'osm'


def load():
    nodes = {}
    with (ROOT / 'koridor_nodes.csv').open(encoding='utf-8', newline='') as fh:
        for r in csv.DictReader(fh):
            nodes[r['id']] = (float(r['lon']), float(r['lat']))
    adj = {}
    names = {}
    with (ROOT / 'koridor_edges.csv').open(encoding='utf-8', newline='') as fh:
        for r in csv.DictReader(fh):
            adj.setdefault(r['from'], []).append((r['to'], float(r['length_m']), r['name']))
            if r['name']:
                names.setdefault(r['from'], set()).add(r['name'])
                names.setdefault(r['to'], set()).add(r['name'])
    return nodes, adj, names


def nearest(nodes, lon, lat):
    return min(nodes, key=lambda n: math.hypot(nodes[n][0] - lon, nodes[n][1] - lat))


def dijkstra(adj, start, goal):
    pq = [(0.0, start, [])]
    seen = set()
    while pq:
        dist, node, path = heapq.heappop(pq)
        if node == goal:
            return dist, path
        if node in seen:
            continue
        seen.add(node)
        for to, length, name in adj.get(node, []):
            if to not in seen:
                heapq.heappush(pq, (dist + length, to, path + [name]))
    return None, None


def run(nodes, adj, names, label, a, b, results):
    s, g = nearest(nodes, *a), nearest(nodes, *b)
    dist, path = dijkstra(adj, s, g)
    if dist is None:
        print(f'{label}: tidak ada rute')
        results.append({'uji': label, 'rute': False})
        return
    streets = [n for n in dict.fromkeys(path) if n]
    detour = [n for n in streets if any(k in n.lower() for k in ('wangsakara', 'santika', 'otista', 'otto'))]
    print(f'{label}: {dist/1000:.2f} km, {len(streets)} nama jalan')
    print('   dilalui:', ' -> '.join(streets[:12]) or '(jalan tanpa nama)')
    print('   jalan alternatif resmi terpakai:', detour or 'tidak')
    results.append({'uji': label, 'rute': True, 'jarak_km': round(dist/1000, 2),
                    'nama_jalan': streets, 'jalan_alternatif_resmi': detour})


def main():
    nodes, adj, names = load()
    print('graf koridor:', len(nodes), 'node,', sum(len(v) for v in adj.values()), 'edge')
    results = []
    run(nodes, adj, names, 'Wangsakara->Santika (jalur alternatif resmi)',
        (106.6045, -6.1800), (106.6160, -6.1778), results)
    run(nodes, adj, names, 'Wangsakara->Sitanala (Neglasari)',
        (106.6045, -6.1800), (106.6340, -6.1620), results)
    out = ROOT / 'analisis_rute.json'
    out.write_text(json.dumps({
        'sumber': 'OpenStreetMap (c) kontributor, ODbL',
        'catatan': 'Rute dihitung dari graf koridor hasil scripts/build_corridor_graph.py. '
                   'Belum ada penutupan pekerjaan nyata; ini uji keterhubungan.',
        'hasil': results}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('ditulis:', out.name)


if __name__ == '__main__':
    main()
