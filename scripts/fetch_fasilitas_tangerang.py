"""Fetch OSM facilities (schools, markets, health) for the study corridor.

Output: data/real-tangerang/osm/fasilitas.geojson
Data (c) OpenStreetMap contributors, ODbL. Requires network access.
"""
import json
import urllib.parse
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / 'data' / 'real-tangerang' / 'osm'
BBOX = (-6.210, 106.585, -6.135, 106.685)
ENDPOINTS = ('https://overpass.kumi.systems/api/interpreter',
             'https://overpass-api.de/api/interpreter')
QUERY = '''
[out:json][timeout:120];
(
  node["amenity"~"^(school|kindergarten|college|university|hospital|clinic|doctors)$"]({bbox});
  way["amenity"~"^(school|kindergarten|college|university|hospital|clinic|doctors)$"]({bbox});
  node["shop"="mall"]({bbox});
  node["amenity"="marketplace"]({bbox});
  way["amenity"="marketplace"]({bbox});
  node["building"="church"]({bbox});
);
out center tags;
'''.replace('{bbox}', '{},{},{},{}'.format(*BBOX))


def overpass(query):
    body = urllib.parse.urlencode({'data': query}).encode()
    last = None
    for url in ENDPOINTS:
        try:
            with urllib.request.urlopen(urllib.request.Request(url, data=body,
                    headers={'User-Agent': 'JalanTanggap-demo/0.1'}), timeout=120) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception as exc:
            last = exc
    raise SystemExit(f'Overpass gagal: {last}')


TIPE = {'school': 'sekolah', 'kindergarten': 'sekolah', 'college': 'sekolah',
        'university': 'sekolah', 'hospital': 'faskes', 'clinic': 'faskes',
        'doctors': 'faskes', 'marketplace': 'pasar', 'mall': 'pasar',
        'church': 'ibadah'}


def main():
    data = overpass(QUERY)
    features = []
    for el in data['elements']:
        tags = el.get('tags', {})
        amenity = tags.get('amenity', tags.get('shop', tags.get('building', '')))
        tipe = TIPE.get(amenity)
        if not tipe:
            continue
        if el['type'] == 'node':
            lon, lat = el['lon'], el['lat']
        else:
            c = el.get('center')
            if not c:
                continue
            lon, lat = c['lon'], c['lat']
        features.append({'type': 'Feature', 'properties': {
            'osm_id': el['id'], 'tipe_el': el['type'], 'nama': tags.get('name', ''),
            'jenis': tipe, 'amenity': amenity, 'jam_padat': '',
            'sumber': 'OpenStreetMap', 'lisensi': 'ODbL',
            'catatan': 'jam_padat belum diisi; perlu konfirmasi pengelola/petugas'},
            'geometry': {'type': 'Point', 'coordinates': [round(lon, 6), round(lat, 6)]}})
    geojson = {'type': 'FeatureCollection',
               'attribution': '(c) OpenStreetMap contributors (ODbL)',
               'bbox': list(BBOX), 'features': features}
    (OUT / 'fasilitas.geojson').write_text(
        json.dumps(geojson, ensure_ascii=False, indent=1), encoding='utf-8')
    dari = {}
    for f in features:
        dari[f['properties']['jenis']] = dari.get(f['properties']['jenis'], 0) + 1
    print('fasilitas:', dari)


if __name__ == '__main__':
    main()
