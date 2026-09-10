"""Fetch the corridor road network and build a compact junction routing graph.

Uses real OSM node IDs, so ways share nodes at junctions. Degree-2 OSM nodes are
then contracted per street. Data (c) OpenStreetMap contributors, ODbL.
"""
import csv
import json
import math
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / 'data' / 'real-tangerang' / 'osm'
# Core study corridor: Karawaci (M. Toha) - Otista - Neglasari.
BBOX = (-6.210, 106.585, -6.135, 106.685)
KEEP = {'motorway', 'trunk', 'primary', 'secondary', 'tertiary',
        'unclassified', 'residential', 'living_street', 'service', 'road',
        'motorway_link', 'trunk_link', 'primary_link', 'secondary_link', 'tertiary_link'}
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


def haversine(a, b):
    return 111195 * math.hypot(b['lat'] - a['lat'],
                               (b['lon'] - a['lon']) * math.cos(math.radians(a['lat'])))


def main():
    s, w, n, e = BBOX
    data = overpass(f'[out:json][timeout:180];way["highway"]({s},{w},{n},{e});out geom;')
    OUT.mkdir(parents=True, exist_ok=True)
    coord = {}
    ways = []
    for el in data['elements']:
        tags = el.get('tags', {})
        if el.get('type') != 'way' or 'geometry' not in el or tags.get('highway') not in KEEP:
            continue
        nodes = el.get('nodes', [])
        geom = el['geometry']
        if len(nodes) != len(geom):
            continue
        for nid, p in zip(nodes, geom):
            coord[nid] = {'lat': p['lat'], 'lon': p['lon']}
        ways.append({'osm_id': el['id'], 'nodes': nodes, 'tags': tags})

    # A node is "significant" if it is a way endpoint or shared by multiple ways.
    way_count = defaultdict(int)
    significant = set()
    for way in ways:
        for nid in way['nodes']:
            way_count[nid] += 1
        significant.update({way['nodes'][0], way['nodes'][-1]})
    significant.update(nid for nid, count in way_count.items() if count > 1)

    edges = []
    for way in ways:
        nodes, tags = way['nodes'], way['tags']
        oneway = tags.get('oneway', '')
        forward = oneway not in ('yes', 'true', '1', '-1')
        backward = oneway not in ('yes', 'true', '1') or oneway == '-1'
        segment_start = nodes[0]
        length = 0.0
        for a, b in zip(nodes, nodes[1:]):
            length += haversine(coord[a], coord[b])
            if b not in significant:
                continue
            segment = {'from': segment_start, 'to': b, 'name': tags.get('name', ''),
                       'highway': tags['highway'], 'length_m': round(length, 1),
                       'osm_id': way['osm_id']}
            if forward:
                edges.append(segment)
            if backward:
                edges.append(dict(segment, **{'from': b, 'to': segment_start}))
            segment_start, length = b, 0.0

    used = {x for edge in edges for x in (edge['from'], edge['to'])}
    with (OUT / 'koridor_nodes.csv').open('w', newline='', encoding='utf-8') as fh:
        wtr = csv.DictWriter(fh, fieldnames=['id', 'lon', 'lat'])
        wtr.writeheader()
        for nid in used:
            wtr.writerow({'id': nid, 'lon': coord[nid]['lon'], 'lat': coord[nid]['lat']})
    with (OUT / 'koridor_edges.csv').open('w', newline='', encoding='utf-8') as fh:
        wtr = csv.DictWriter(fh, fieldnames=['id', 'from', 'to', 'name', 'highway', 'length_m', 'osm_id'])
        wtr.writeheader()
        for i, edge in enumerate(edges):
            wtr.writerow({'id': f'E{i:05d}', **edge})
    print(f'{len(used)} nodes, {len(edges)} directed edges')


if __name__ == '__main__':
    main()
