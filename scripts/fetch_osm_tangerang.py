"""Fetch real OSM road geometry for the Kota Tangerang study corridor.

Data (c) OpenStreetMap contributors, ODbL. Requires network access.
"""
import json
import urllib.parse
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / 'data' / 'real-tangerang' / 'osm'
# Bounding box (south, west, north, east) around Kota Tangerang.
BBOX = (-6.30, 106.50, -6.05, 106.90)
NAMES = ('M. Toha|Muhammad Toha|Toha Raya|Teuku Umar|Iskandar Muda|'
         'Marsekal Surya|Sitanala|Aria Wangsakara|Arya Wangsakara|RD. Aria Wangsakara|'
         'Aria Santika|Arya Santikan|Aria Jaya Santika|Otista|Otto Iskandar|'
         'Husein Sastranegara|Sangego|Prabu Kian Santang|Kedaung Barat|Bayur|'
         'Tangga Abu|Garuda|Sultan Iskandar Muda')
ENDPOINTS = ('https://overpass-api.de/api/interpreter',
             'https://overpass.kumi.systems/api/interpreter')


def overpass(query):
    body = urllib.parse.urlencode({'data': query}).encode()
    last = None
    for url in ENDPOINTS:
        try:
            with urllib.request.urlopen(urllib.request.Request(url, data=body,
                    headers={'User-Agent': 'JalanTanggap-demo/0.1'}), timeout=120) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception as exc:  # try the next mirror
            last = exc
    raise SystemExit(f'Overpass gagal: {last}')


def main():
    s, w, n, e = BBOX
    query = (f'[out:json][timeout:120];'
             f'way["highway"]["name"~"{NAMES}",i]({s},{w},{n},{e});'
             f'out tags geom;')
    data = overpass(query)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'osm_raw.json').write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    features = []
    for el in data['elements']:
        if el.get('type') != 'way' or 'geometry' not in el:
            continue
        props = {'osm_id': el['id'], 'name': el['tags'].get('name', ''),
                 'highway': el['tags'].get('highway', ''),
                 'oneway': el['tags'].get('oneway', ''),
                 'lanes': el['tags'].get('lanes', ''),
                 'maxspeed': el['tags'].get('maxspeed', ''),
                 'source': 'OpenStreetMap', 'license': 'ODbL'}
        features.append({'type': 'Feature', 'properties': props,
                         'geometry': {'type': 'LineString',
                                      'coordinates': [[p['lon'], p['lat']] for p in el['geometry']]}})
    geojson = {'type': 'FeatureCollection',
               'attribution': '(c) OpenStreetMap contributors (ODbL)',
               'source_url': 'https://www.openstreetmap.org',
               'features': features}
    (OUT / 'jalan_tangerang.geojson').write_text(json.dumps(geojson, ensure_ascii=False), encoding='utf-8')
    names = sorted({f['properties']['name'] for f in features})
    print(f'{len(features)} ways, {len(names)} nama jalan -> {OUT}')


if __name__ == '__main__':
    main()
