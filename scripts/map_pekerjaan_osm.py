"""Map official road-work sites to OSM ways/nodes and build closure scenarios.

Approach: match by street name (news name -> OSM name aliases) inside the
corridor bbox, then pick the OSM ways whose centroid falls in the reported
work area. The mapping is review material, NOT a verified closure polygon.
"""
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'data' / 'real-tangerang'
OSM = ROOT / 'osm'
BBOX = (-6.210, 106.585, -6.115, 106.700)

# Official site -> OSM name aliases (verified against the corridor graph).
ALIASES = {
    'CT01': {'pekerjaan': 'Jalan Raya M. Toha (Karawaci)',
             'osm': ['Jalan Muhammad Thoha', 'Jalan Toha Raya'],
             'status_pemetaan': 'cocok',
             'catatan': 'OSM mencatat jalan utama dengan ejaan "Jalan Muhammad Thoha" '
                        '(bukan nama resmi "M. Toha"). Temuan 10 Sep 2026.'},
    'CT02': {'pekerjaan': 'Jalan Iskandar Muda (Neglasari)',
             'osm': ['Jalan Iskandar Muda'],
             'status_pemetaan': 'cocok',
             'catatan': 'Bedakan dari "Jalan Sultan Iskandar Muda" (koridor timur, trunk).'},
    'CT03': {'pekerjaan': 'Jalan Marsekal Suryadarma (Neglasari)',
             'osm': ['Jalan Marsekal Surya Darma', 'Jalan Surya Darma'],
             'status_pemetaan': 'cocok_alias',
             'catatan': 'Nama resmi "Marsekal Suryadarma"; di OSM tercatat sebagai "Jalan Surya Darma" '
                        '(tanpa kata Marsekal). Verifikasi manual tetap diperlukan.'},
    'CT04': {'pekerjaan': 'Jalan Dokter Sitanala (Neglasari)',
             'osm': ['Jalan Dokter Sitanala', 'Jalan Doktor Sitanala'],
             'status_pemetaan': 'cocok',
             'catatan': 'Pelebaran 146 m; skema tidak mengubah akses.'},
    'CT05': {'pekerjaan': 'Jalan Teuku Umar (Karawaci)',
             'osm': ['Jalan Teuku Umar', 'Jalan Teuku Umar Raya'],
             'status_pemetaan': 'parsial',
             'catatan': 'Nama sama dipakai di wilayah lain Tangerang; hanya segmen dalam bbox koridor yang dipetakan.'},
    'CT06': {'pekerjaan': 'Jalan Garuda (Batuceper)',
             'osm': ['Jalan Garuda'],
             'status_pemetaan': 'di_luar_koridor',
             'catatan': 'Batuceper berada di luar bbox koridor Karawaci-Neglasari.'},
}
JALAN_UTAMA = ['Jalan Aria Wangsakara', 'Jalan Aria Santika', 'Jalan Otista Raya']


def load_ways():
    """Rebuild way centroids from the corridor graph itself, so every mapped
    osm_id is guaranteed to exist as edges that can actually be closed."""
    nodes = {}
    with (OSM / 'koridor_nodes.csv').open(encoding='utf-8', newline='') as fh:
        for r in csv.DictReader(fh):
            nodes[r['id']] = (float(r['lon']), float(r['lat']))
    pts = defaultdict(list)
    name = {}
    with (OSM / 'koridor_edges.csv').open(encoding='utf-8', newline='') as fh:
        for r in csv.DictReader(fh):
            pts[r['osm_id']].append(nodes[r['from']])
            pts[r['osm_id']].append(nodes[r['to']])
            name[r['osm_id']] = r['name']
    return [{'osm_id': sid, 'name': name[sid],
             'lon': statistics.mean(p[0] for p in ps),
             'lat': statistics.mean(p[1] for p in ps)}
            for sid, ps in pts.items() if name[sid]]


def main():
    ways = load_ways()
    mapping = []
    for cid, spec in ALIASES.items():
        matched = [w for w in ways
                   if any(w['name'] == alias for alias in spec['osm'])
                   and BBOX[0] <= w['lat'] <= BBOX[2] and BBOX[1] <= w['lon'] <= BBOX[3]]
        mapping.append({'id_pekerjaan': cid, **spec,
                        'jumlah_way_osm': len(matched),
                        'osm_ids': [w['osm_id'] for w in matched]})
    (ROOT / 'pemetaan_pekerjaan_osm.json').write_text(
        json.dumps({'perhatian': 'Pemetaan nama -> way OSM untuk ditinjau petugas, '
                   'bukan poligon penutupan terverifikasi.',
                   'pekerjaan': mapping}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for m in mapping:
        print(f"{m['id_pekerjaan']} {m['pekerjaan']}: {m['jumlah_way_osm']} way [{m['status_pemetaan']}]")


if __name__ == '__main__':
    main()
