"""Build a graph from real OSM road geometry and test the official M. Toha detour.

No external libraries: coordinates are rounded to ~11 m to form nodes.
"""
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'data' / 'real-tangerang' / 'osm'
PRECISION = int(sys.argv[1]) if len(sys.argv) > 1 else 4


def key(lon, lat):
    return (round(lon, PRECISION), round(lat, PRECISION))


def distance(a, b):
    return 111195 * math.hypot(a[1] - b[1],
                               (a[0] - b[0]) * math.cos(math.radians(a[1])))


def load():
    geo = json.loads((ROOT / 'jalan_tangerang.geojson').read_text(encoding='utf-8'))
    adjacency = defaultdict(list)
    names_at = defaultdict(set)
    for feature in geo['features']:
        coords = feature['geometry']['coordinates']
        name = feature['properties']['name']
        for a, b in zip(coords, coords[1:]):
            ka, kb = key(*a), key(*b)
            adjacency[ka].append(kb)
            adjacency[kb].append(ka)
            names_at[ka].add(name)
            names_at[kb].add(name)
    return adjacency, names_at


def find_nodes(names_at, pattern):
    hit = {}
    for node, names in names_at.items():
        for n in names:
            if pattern.lower() in n.lower():
                hit.setdefault(n, []).append(node)
    return hit


def component(adjacency, start, allowed_names=None, names_at=None):
    seen = {start}
    stack = [start]
    while stack:
        node = stack.pop()
        for nxt in adjacency[node]:
            if nxt in seen:
                continue
            if allowed_names and names_at:
                shared = names_at[node] | names_at[nxt]
                if not any(any(p.lower() in nm.lower() for p in allowed_names) for nm in shared):
                    continue
            seen.add(nxt)
            stack.append(nxt)
    return seen


def main():
    adjacency, names_at = load()
    print('nodes:', len(adjacency))
    for pattern in ('Wangsakara', 'Santika', 'Otista', 'Surya', 'Teuku Umar', 'Iskandar Muda'):
        found = find_nodes(names_at, pattern)
        total = sum(len(v) for v in found.values())
        print(f'  {pattern}: {len(found)} nama, {total} titik')
        for name in found:
            print(f'      - {name}')

    detour = ['Wangsakara', 'Santika', 'Otista']
    nodes = find_nodes(names_at, 'Wangsakara')
    if not nodes:
        print('Tidak ada jalan Wangsakara di graf; detour resmi tidak dapat ditelusuri.')
        return 1
    start = nodes[sorted(nodes)[0]][0]
    reach = component(adjacency, start)
    connected_names = sorted({n for node in reach for n in names_at[node]})
    print('\nDari Aria Wangsakara, komponen berisi', len(reach), 'titik dan', len(connected_names), 'nama jalan.')
    for p in detour:
        present = [n for n in connected_names if p.lower() in n.lower()]
        print(f'  detour "{p}" terjangkau: {bool(present)} {present}')

    geo = json.loads((ROOT / 'jalan_tangerang.geojson').read_text(encoding='utf-8'))
    kept = [f for f in geo['features']
            if any(p.lower() in f['properties']['name'].lower() for p in detour)]
    if kept:
        out = ROOT / 'koridor_detour_mtoha.geojson'
        out.write_text(json.dumps({'type': 'FeatureCollection',
            'attribution': '(c) OpenStreetMap contributors (ODbL)',
            'note': 'Koridor nama resmi jalur alternatif M. Toha (nama OSM), belum termasuk titik pekerjaan.',
            'features': kept}, ensure_ascii=False, indent=1), encoding='utf-8')
        print('koridor ditulis:', out.name, len(kept), 'way')
    return 0


if __name__ == '__main__':
    sys.exit(main())
