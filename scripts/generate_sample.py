"""Deterministic synthetic fixtures, Phase 4 (Fase 4) schemas included.

Generates Phase 1 reporting/survey tables plus Fase 4 datasets:
traffic_history.csv (time-series per ruas), roadworks_events.csv
(historical/gangguan events), and traffic_ai_dataset.csv (baseline vs event
paired features/targets shaped for the XGBoost MVP described in
AI-Traffic-Impact.md). Standard library only.
"""
import csv
import json
import math
import random
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'data' / 'sample-tangerang'
EVENT_DAYS_1 = ['2026-09-03', '2026-09-04', '2026-09-05', '2026-09-06', '2026-09-07']
EVENT_DAYS_2 = ['2026-09-03', '2026-09-04', '2026-09-05']
BASELINE_DAYS = ['2026-09-01', '2026-09-02', '2026-09-08', '2026-09-09']
EVENT_HOURS = [16, 17]
CAP_PER_LAjur = 400


def hour_factor(h):
    if 7 <= h <= 9:
        return 1.6
    if 16 <= h <= 19:
        return 1.5
    if 12 <= h <= 13:
        return 0.9
    return 1.0


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
                lebar = 4 if i % 7 == 0 else 7
                edges.append(dict(id_segmen=f'S{i:02}', from_node=a['id_node'], to_node=b['id_node'],
                    nama=f'Jalan simulasi Tangerang {i:02}', panjang_m=length,
                    arah='forward' if i == 3 else 'both', lebar_m=lebar,
                    jumlah_lajur=1 if lebar < 5 else 2,
                    kendaraan='motor' if i == 6 else 'mobil;motor', kewenangan='belum_diverifikasi',
                    surface='aspal_simulasi', is_simulation=True))
    save('segmen', edges)
    seg = {e['id_segmen']: e for e in edges}
    features = [dict(type='Feature', properties=e, geometry=dict(
        type='LineString', coordinates=[[lookup[n]['longitude'], lookup[n]['latitude']]
                                        for n in (e['from_node'], e['to_node'])]))
        for e in edges]
    dump('jaringan.geojson', dict(type='FeatureCollection', features=features))

    # ring-1 neighbours per segment (shared endpoint node)
    node_to_segs = {}
    for e in edges:
        for n in (e['from_node'], e['to_node']):
            node_to_segs.setdefault(n, []).append(e['id_segmen'])
    ring1 = {}
    for e in edges:
        nb = []
        for n in (e['from_node'], e['to_node']):
            nb += [s for s in node_to_segs[n] if s != e['id_segmen']]
        ring1[e['id_segmen']] = list(dict.fromkeys(nb))

    reports, labels = [], []
    for i in range(100):
        sid = f'S{i%20:02}'
        e = seg[sid]
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
            id_cluster_duplikat='' if unclear else f'C{original if duplicate else i:03}',
            is_simulation=True))
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
    save('pembatasan', [dict(id_pembatasan='B01', id_proyek='P01', id_segmen='S00',
        mulai='2026-09-10T16:00:00+07:00', selesai='2026-09-10T20:00:00+07:00',
        jenis='total', capacity_factor=0, scope='candidate', is_simulation=True),
        dict(id_pembatasan='B02', id_proyek='P02', id_segmen='S01',
        mulai='2026-09-10T16:00:00+07:00', selesai='2026-09-10T18:00:00+07:00',
        jenis='total', capacity_factor=0, scope='active', is_simulation=True),
        dict(id_pembatasan='B03', id_proyek='P03', id_segmen='S09',
        mulai='2026-09-10T16:00:00+07:00', selesai='2026-09-10T20:00:00+07:00',
        jenis='parsial', capacity_factor=.5, scope='active', is_simulation=True)])
    save('aktivitas', [dict(id_aktivitas=f'A{i:02}', nama=f'{kind} simulasi {i}',
        id_segmen=f'S{i:02}', jenis=kind, mulai='2026-09-10T16:00:00+07:00',
        selesai='2026-09-10T18:00:00+07:00', is_simulation=True)
        for i, kind in enumerate(['sekolah','pasar','faskes','pulang_kerja']*3)])

    # ---- Fase 4: events, time-series traffic, AI dataset -------------------
    events = [dict(id_event='RV01', id_segmen_pekerjaan='S01',
        waktu_mulai='2026-09-03T16:00:00+07:00', waktu_selesai='2026-09-07T18:00:00+07:00',
        jenis_pekerjaan='rekonstruksi', jenis_pembatasan='tutup_total',
        jumlah_lajur_ditutup=seg['S01']['jumlah_lajur'], arah_terdampak='dua_arah',
        severity='tinggi', segmen_terdampak=';'.join(ring1['S01'][:4]), is_simulation=True),
        dict(id_event='RV02', id_segmen_pekerjaan='S09',
        waktu_mulai='2026-09-03T16:00:00+07:00', waktu_selesai='2026-09-05T18:00:00+07:00',
        jenis_pekerjaan='perbaikan_berkala', jenis_pembatasan='lajur_ditutup',
        jumlah_lajur_ditutup=1, arah_terdampak='satu_arah',
        severity='sedang', segmen_terdampak=';'.join(ring1['S09'][:4]), is_simulation=True)]
    save('roadworks_events', events)

    def event_state(sid, day, h):
        """(volume_factor, speed_factor, flag) combining active events."""
        f_v, f_s, flags = 1.0, 1.0, []
        for ev in events:
            active = day in ({'RV01': EVENT_DAYS_1, 'RV02': EVENT_DAYS_2}[ev['id_event']]) \
                and h in EVENT_HOURS
            if not active:
                continue
            if ev['id_event'] == 'RV01':
                if sid == 'S01':
                    f_v, f_s = 0.0, 0.0
                    flags.append('penutupan_total')
                elif sid in ring1['S01'][:4]:
                    f_v *= 1.38
                    f_s *= 0.68
                    flags.append('penerima_pengalihan')
            if ev['id_event'] == 'RV02':
                if sid == 'S09':
                    f_v *= 0.82
                    f_s *= 0.85
                    flags.append('lajur_ditutup')
                elif sid in ring1['S09'][:4]:
                    f_v *= 1.22
                    f_s *= 0.83
                    flags.append('penerima_pengalihan')
        return f_v, f_s, '+'.join(flags) if flags else 'ok'

    traffic = []
    for e in edges:
        for d in (['forward'] if e['arah'] == 'forward' else ['forward', 'reverse']):
            ff = 30 if e['lebar_m'] < 5 else 45
            cap = CAP_PER_LAjur * e['jumlah_lajur']
            base_v = 150 + int(e['id_segmen'][1:]) * 8
            for day in BASELINE_DAYS + EVENT_DAYS_1:
                for h in range(6, 20):
                    rng = random.Random(f"{e['id_segmen']}-{d}-{day}-{h}")
                    jitter = rng.uniform(-0.1, 0.1)
                    vol = base_v * hour_factor(h) * (1 + jitter)
                    if day[-2:] in ('06', '07'):
                        vol *= 0.9
                    spf = 1.0
                    flag = 'ok'
                    f_v, f_s, ev_flag = event_state(e['id_segmen'], day, h)
                    if ev_flag != 'ok':
                        vol *= f_v
                        spf = f_s if f_v == 0.0 else spf * f_s
                        flag = ev_flag
                    speed = ff * max(0.25, 1 - 0.55 * min(1.0, vol / cap)) * spf
                    if f_v == 0.0:
                        speed = 0.0
                    cong = min(0.99, vol / cap) if f_v else 1.0
                    traffic.append(dict(
                        timestamp=f'{day}T{h:02d}:00:00+07:00', id_segmen=e['id_segmen'],
                        direction=d, speed_kmh=round(speed, 1), free_flow_speed_kmh=ff,
                        volume_veh_per_jam=round(vol), congestion_index=round(cong, 2),
                        source='SURVEI_SIMULASI', quality_flag=flag, is_simulation=True))
    save('traffic_history', traffic)

    fac = {}
    for a in tables['aktivitas']:
        fac[a['id_segmen']] = fac.get(a['id_segmen'], 0) + 1
    baseline = {}
    for row in traffic:
        if row['quality_flag'] == 'ok':
            k = (row['id_segmen'], row['direction'], int(row['timestamp'][11:13]))
            baseline.setdefault(k, []).append((row['volume_veh_per_jam'], row['speed_kmh']))
    rows_ai = []
    for ev in events:
        days = {'RV01': EVENT_DAYS_1, 'RV02': EVENT_DAYS_2}[ev['id_event']]
        targets = [ev['id_segmen_pekerjaan']] + ev['segmen_terdampak'].split(';')
        for t in targets:
            for d in (['forward'] if seg[t]['arah'] == 'forward' else ['forward', 'reverse']):
                for h in EVENT_HOURS:
                    b = baseline.get((t, d, h), [(0, 0)])
                    bv = sum(x[0] for x in b) / len(b)
                    bs = sum(x[1] for x in b) / len(b)
                    cur = [r for r in traffic if r['id_segmen'] == t and r['direction'] == d
                           and r['timestamp'][11:13] == f'{h:02d}' and r['timestamp'][:10] in days]
                    if not cur:
                        continue
                    av = sum(r['volume_veh_per_jam'] for r in cur) / len(cur)
                    asp = sum(r['speed_kmh'] for r in cur) / len(cur)
                    overlap = int(any('+' in r['quality_flag'] for r in cur))
                    rows_ai.append(dict(
                        id_event=ev['id_event'], source_pekerjaan=ev['id_segmen_pekerjaan'],
                        target_segment=t, hop_dari_pekerjaan=0 if t == ev['id_segmen_pekerjaan'] else 1,
                        direction=d, jam=f'{h:02d}:00', jam_sibuk=int(h >= 16),
                        jenis_pembatasan=ev['jenis_pembatasan'],
                        lajur_ditutup=ev['jumlah_lajur_ditutup'], kapasitas_veh_jam=CAP_PER_LAjur*seg[t]['jumlah_lajur'],
                        volume_baseline=round(bv), speed_baseline=round(bs, 1),
                        fasilitas_aktif=fac.get(t, 0), pekerjaan_lain_overlap=overlap,
                        delta_volume=round(av - bv), delta_speed=round(asp - bs, 1),
                        congestion=int(max(r['congestion_index'] for r in cur) >= 0.7),
                        is_simulation=True))
    save('traffic_ai_dataset', rows_ai)

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
    dump('manifest.json', dict(version=2, is_simulation=True,
        context='Tangerang-Rajeg / pengalaman M. Toha',
        skema='traffic_history/roadworks_events/traffic_ai_dataset mengikuti Kebutuhan-Data.md Fase 4',
        provenance='Seluruh data dan geometri dibuat sintetis; bukan OSM, survei, atau data pemerintah.',
        timezone='Asia/Jakarta', coordinate_system='EPSG:4326',
        counts={k: len(v) for k, v in tables.items()},
        generated_by='scripts/generate_sample.py',
        photos='Tidak tersedia; kolom foto kosong, tidak ada bukti foto buatan.'))
    print(json.dumps({k: len(v) for k, v in tables.items()}, indent=2))


if __name__ == '__main__':
    main()
