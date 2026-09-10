"""Fetch drivable road network for the study corridor and build junction graph.

All road classes are needed: an arterial-only graph fragments into ~1000
disconnected components, so local streets act as the connectors between
arterial segments. Data (c) OpenStreetMap contributors, ODbL.
"""
import csv
import json
import math
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / 'data' / 'real-tangerang' / 'osm'
# Karawaci (M. Toha / Teuku Umar) - Neglasari (Iskandar Muda, Sitanala,
# Surya Darma) - Otista/Periuk side. Covers the official August-2026 works.
BBOX = (-6.210, 106.585, -6.115, 106.700)
KEEP = {'motorway', 'trunk', 'primary', 'secondary', 'tertiary',
        'unclassified', 'residential', 'living_street', 'service', 'road',
        'motorway_link', 'trunk_link', 'primary_link', 'secondary_link',
        'tertiary_link'}
ENDPOINTS = ('https://overpass.kumi.systems/api/interpreter',
             'https://overpass-api.de/api/interpreter')


def overpass(query):
    body = urllib.parse.urlencode({'data': query}).encode()
    last = None
    for url in ENDPOINTS:
        try:
            with urllib.request.urlopen(urllib.request.Request(url, data=body,
                    headers={'User-Agent': 'JalanTanggap-demo/0.1'}), timeout=180) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception as exc:
            last = exc
    raise SystemExit(f'Overpass gagal: {last}')


def main():
    s, w, n, e = BBOX
    data = overpass(f'[out:json][timeout:180];way["highway"]({s},{w},{n},{e});out geom;')
    coord, ways = {}, []
    for el in data['elements']:
        tags = el.get('tags', {})
        if el.get('type') != 'way' or tags.get('highway') not in KEEP:
            continue
        nodes, geom = el.get('nodes', []), el.get('geometry', [])
        if not nodes or len(nodes) != len(geom):
            continue
        for nid, p in zip(nodes, geom):
            coord[nid] = (p['lon'], p['lat'])
        ways.append({'id': el['id'], 'nodes': nodes, 'tags': tags})

    endpoints, shared = set(), {}
    for way in ways:
        endpoints.update({way['nodes'][0], way['nodes'][-1]})
        for nid in way['nodes']:
            shared[nid] = shared.get(nid, 0) + 1
    junction = endpoints | {nid for nid, c in shared.items() if c > 1}

    edges = []
    for way in ways:
        nodes, tags = way['nodes'], way['tags']
        oneway = tags.get('oneway', '')
        fwd = oneway not in ('yes', 'true', '1', '-1')
        bwd = oneway in ('-1',) or (oneway not in ('yes', 'true', '1'))
        start, length = nodes[0], 0.0
        for a, b in zip(nodes, nodes[1:]):
            la, lo = coord[a], coord[b]
            length += 111195 * math.hypot(lo[1]-la[1], (lo[0]-la[0])*math.cos(math.radians(la[1])))
            if b not in junction:
                continue
            if b == start:
                length = 0.0
                continue
            seg = {'from': start, 'to': b, 'name': tags.get('name', ''),
                   'highway': tags['highway'], 'length_m': round(length, 1),
                   'osm_id': way['id']}
            if fwd:
                edges.append(seg)
            if bwd:
                edges.append(dict(seg, **{'from': b, 'to': start}))
            start, length = b, 0.0

    used = {x for edge in edges for x in (edge['from'], edge['to'])}
    with (OUT / 'koridor_nodes.csv').open('w', newline='', encoding='utf-8') as fh:
        wtr = csv.DictWriter(fh, fieldnames=['id', 'lon', 'lat'])
        wtr.writeheader()
        for nid in used:
            wtr.writerow({'id': nid, 'lon': coord[nid][0], 'lat': coord[nid][1]})
    with (OUT / 'koridor_edges.csv').open('w', newline='', encoding='utf-8') as fh:
        wtr = csv.DictWriter(fh, fieldnames=['id', 'from', 'to', 'name', 'highway', 'length_m', 'osm_id'])
        wtr.writeheader()
        for i, edge in enumerate(edges):
            wtr.writerow({'id': f'E{i:05d}', **edge})
    print(f'{len(ways)} way -> {len(used)} node, {len(edges)} edge')
    und = defaultdict(set)
    for edge in edges:
        und[edge['from']].add(edge['to'])
        und[edge['to']].add(edge['from'])
    labeled = {}
    comp_size = []
    for start in list(und):
        if start in labeled:
            continue
        cid = len(comp_size)
        seen, stack = {start}, [start]
        labeled[start] = cid
        while stack:
            cur = stack.pop()
            for nxt in und[cur]:
                if nxt not in seen:
                    seen.add(nxt)
                    labeled[nxt] = cid
                    stack.append(nxt)
        comp_size.append(len(seen))
    comp_size.sort(reverse=True)
    print(f'komponen: {len(comp_size)} | terbesar {comp_size[0]} | ke-2 {comp_size[1] if len(comp_size) > 1 else 0} node')


if __name__ == '__main__':
    main()
