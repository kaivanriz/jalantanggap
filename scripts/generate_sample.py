"""Deterministic synthetic fixtures; Python standard library only."""
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'data' / 'sample-tangerang'


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    tables = {}

    def save(name, rows):
        tables[name] = rows
        with (ROOT / f'{name}.csv').open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    def dump(name, obj):
        (ROOT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    # Schematic grid within the broader Tangerang area; NOT real street geometry.
    nodes = [dict(id_node=f'N{r*5+c:02}', latitude=round(-6.18+r*.018, 6),
                  longitude=round(106.51+c*.025, 6), is_simulation=True)
             for r in range(5) for c in range(5)]
    save('nodes', nodes)
    lookup = {n['id_node']: n for n in nodes}
    edges = []
    for r in range(5):
        for c in range(5):
            u = r*5+c
            for v in ([u+1] if c < 4 else []) + ([u+5] if r < 4 else []):
                a, b = nodes[u], nodes[v]
                length = round(111195 * math.hypot(b['latitude']-a['latitude'],
                               (b['longitude']-a['longitude'])*math.cos(math.radians(a['latitude']))))
                i = len(edges)
                edges.append(dict(id_segmen=f'S{i:02}', from_node=a['id_node'], to_node=b['id_node'],
                    nama=f'Jalan simulasi Tangerang {i:02}', panjang_m=length,
                    arah='forward' if i == 3 else 'both', lebar_m=4 if i % 7 == 0 else 7,
                    kendaraan='motor' if i == 6 else 'mobil;motor', kewenangan='belum_diverifikasi',
                    surface='aspal_simulasi', is_simulation=True))
    save('segmen', edges)
    features = []
    for e in edges:
        coords = [[lookup[n]['longitude'], lookup[n]['latitude']] for n in (e['from_node'], e['to_node'])]
        features.append(dict(type='Feature', properties=e, geometry=dict(type='LineString', coordinates=coords)))
    dump('jaringan.geojson', dict(type='FeatureCollection', features=features))

    reports, labels = [], []
    for i in range(100):
        sid = f'S{i%20:02}'
        e = edges[i%20]
        a, b = lookup[e['from_node']], lookup[e['to_node']]
        unclear = i % 10 == 8
        duplicate = i >= 90
        original = i-20
        text = 'Jalan dekat rumah rusak, tolong dicek.' if unclear else (
            f"Di {e['nama']} ada lubang. Kendaraan harus bergantian lewat, terutama sore hari.")
        reports.append(dict(id_laporan=f'L{i:03}', id_segmen='' if unclear else sid,
            id_pelapor=f'W{original if duplicate else i:03}',
            waktu=f'2026-09-{1+i%8:02}T17:00:00+07:00',
            latitude='' if unclear else round((a['latitude']+b['latitude'])/2, 6),
            longitude='' if unclear else round((a['longitude']+b['longitude'])/2, 6),
            deskripsi=text, foto_url='', status='duplikat' if duplicate else 'perlu_klarifikasi' if unclear else 'valid',
            duplicate_of=f'L{original:03}' if duplicate else '', is_simulation=True))
        labels.append(dict(id_laporan=f'L{i:03}', jenis='kerusakan_tidak_spesifik' if unclear else 'berlubang',
            dampak='tidak_disebutkan' if unclear else 'kendaraan_bergantian',
            info_kurang='lokasi_pasti;detail_kerusakan' if unclear else '',
            split='test' if i%5 == 0 else 'development', is_simulation=True))
    save('laporan', reports)
    save('label_llm', labels)
    assessments = [dict(id_penilaian=f'V{i:02}', id_segmen=f'S{i:02}',
        tanggal='2026-09-09', kerusakan=1+i%5, dampak_akses=1+i%4, peran_jalan=1+i%3,
        panjang_rusak_m=20+i*5, penilai='PETUGAS_SIMULASI', is_simulation=True) for i in range(20)]
    save('penilaian', assessments)
    save('proyek', [dict(id_proyek=pid, nama=title, status=status, updated_at='2026-09-10T08:00:00+07:00',
        pic='PETUGAS_SIMULASI', is_simulation=True) for pid, title, status in [
        ('P01','Pekerjaan jalan utama simulasi','usulan'),
        ('P02','Pekerjaan jalur alternatif simulasi','aktif'),
        ('P03','Pembatasan parsial simulasi','aktif'),
        ('P04','Pekerjaan lama simulasi','selesai')]])
    closures = [dict(id_pembatasan='B01', id_proyek='P01', id_segmen='S00',
        mulai='2026-09-10T16:00:00+07:00', selesai='2026-09-10T20:00:00+07:00',
        jenis='total', capacity_factor=0, scope='candidate', is_simulation=True),
        dict(id_pembatasan='B02', id_proyek='P02', id_segmen='S01',
        mulai='2026-09-10T16:00:00+07:00', selesai='2026-09-10T18:00:00+07:00',
        jenis='total', capacity_factor=0, scope='active', is_simulation=True),
        dict(id_pembatasan='B03', id_proyek='P03', id_segmen='S09',
        mulai='2026-09-10T16:00:00+07:00', selesai='2026-09-10T20:00:00+07:00',
        jenis='parsial', capacity_factor=.5, scope='active', is_simulation=True)]
    save('pembatasan', closures)
    save('aktivitas', [dict(id_aktivitas=f'A{i:02}', nama=f'{kind} simulasi {i}',
        id_segmen=f'S{i:02}', jenis=kind, mulai='2026-09-10T16:00:00+07:00',
        selesai='2026-09-10T18:00:00+07:00', is_simulation=True)
        for i, kind in enumerate(['sekolah','pasar','faskes','pulang_kerja']*3)])
    save('traffic', [dict(id_segmen=e['id_segmen'], arah=d, mulai=f'2026-09-10T{h:02}:00:00+07:00',
        selesai=f'2026-09-10T{h+1:02}:00:00+07:00', volume_mobil_per_jam=150+int(e['id_segmen'][1:])*8,
        kapasitas_mobil_per_jam=800, unit='mobil_penumpang/jam/arah', sumber='asumsi_sintetis',
        is_simulation=True) for e in edges for d in (['forward'] if e['arah']=='forward' else ['forward','reverse'])
        for h in [7,12,17]])
    dump('skenario.json', [dict(id='BASE', waktu='2026-09-10T17:00:00+07:00', closures=[], expected_route=True),
        dict(id='UTAMA', waktu='2026-09-10T17:00:00+07:00', closures=['B01'], expected_route=True),
        dict(id='KONFLIK', waktu='2026-09-10T17:00:00+07:00', closures=['B01','B02','B03'], expected_route=False),
        dict(id='SETELAH', waktu='2026-09-10T18:00:00+07:00', closures=['B01','B02','B03'], expected_route=True)])
    dump('aturan.json', dict(is_simulation=True, origin='N00', destination='N24', vehicle='mobil',
        interval='[mulai, selesai)', weights=dict(kerusakan=.4, dampak_akses=.3, peran_jalan=.2, pelapor=.1),
        reporter_window=['2026-08-12T00:00:00+07:00','2026-09-11T00:00:00+07:00'],
        reporter_score_bands=[dict(max=2,score=1),dict(max=5,score=2),dict(max=10,score=3),dict(max=20,score=4)],
        reporter_score_above_20=5, turn_restrictions=[],
        note='Tidak ada larangan belok dalam graf sintetis ini; tidak boleh diasumsikan untuk peta nyata.'))
    dump('manifest.json', dict(version=1, is_simulation=True, context='Tangerang–Rajeg / pengalaman M. Toha',
        provenance='Seluruh data dan geometri dibuat sintetis; bukan OSM, survei, atau data pemerintah.',
        timezone='Asia/Jakarta', coordinate_system='EPSG:4326', counts={k:len(v) for k,v in tables.items()},
        generated_by='scripts/generate_sample.py', photos='Tidak tersedia; kolom foto kosong, tidak ada bukti foto buatan.'))
    print(json.dumps({k:len(v) for k,v in tables.items()}, indent=2))


if __name__ == '__main__':
    main()
