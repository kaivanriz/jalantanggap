"""Validate relational fixtures and actual route outcomes without dependencies."""
import csv
import heapq
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'data' / 'sample-tangerang'


def load(name):
    with (ROOT / f'{name}.csv').open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def main():
    manifest = json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
    tables = {name:load(name) for name in manifest['counts']}
    for name, rows in tables.items():
        assert len(rows) == manifest['counts'][name], name
        assert all(None not in row and None not in row.values() for row in rows), name
        assert all(row['is_simulation']=='True' for row in rows), name
    nodes = {n['id_node'] for n in tables['nodes']}
    segments = {e['id_segmen']:e for e in tables['segmen']}
    projects = {p['id_proyek'] for p in tables['proyek']}
    reports = {r['id_laporan']:r for r in tables['laporan']}
    assert len(reports)==100 and len(segments)==40 and len(nodes)==25
    for e in segments.values():
        assert e['from_node'] in nodes and e['to_node'] in nodes
        assert float(e['panjang_m'])>0
    for name in ['laporan','penilaian','pembatasan','aktivitas','traffic']:
        for row in tables[name]:
            assert not row['id_segmen'] or row['id_segmen'] in segments
    for r in reports.values():
        if r['duplicate_of']:
            original=reports[r['duplicate_of']]
            assert r['id_segmen']==original['id_segmen'] and r['id_pelapor']==original['id_pelapor']
    for label in tables['label_llm']:
        assert label['id_laporan'] in reports
    closures={b['id_pembatasan']:b for b in tables['pembatasan']}
    for b in closures.values():
        assert b['id_proyek'] in projects
    for name in ['pembatasan','aktivitas','traffic']:
        for row in tables[name]:
            assert datetime.fromisoformat(row['mulai']) < datetime.fromisoformat(row['selesai'])
    settings=json.loads((ROOT/'aturan.json').read_text(encoding='utf-8'))
    assert abs(sum(settings['weights'].values())-1)<1e-9
    output=[]
    for case in json.loads((ROOT/'skenario.json').read_text(encoding='utf-8')):
        time=datetime.fromisoformat(case['waktu'])
        active=[closures[k] for k in case['closures'] if datetime.fromisoformat(closures[k]['mulai'])<=time<datetime.fromisoformat(closures[k]['selesai'])]
        blocked={b['id_segmen'] for b in active if b['jenis']=='total'}
        adjacency={n:[] for n in nodes}
        for e in segments.values():
            if e['id_segmen'] in blocked or settings['vehicle'] not in e['kendaraan'].split(';'):
                continue
            u,v=e['from_node'],e['to_node']
            adjacency[u].append((v,int(e['panjang_m']),e['id_segmen']))
            if e['arah']=='both':
                adjacency[v].append((u,int(e['panjang_m']),e['id_segmen']))
        queue=[(0,settings['origin'],[])]
        visited=set()
        result=None
        while queue:
            distance,node,path=heapq.heappop(queue)
            if node in visited:
                continue
            visited.add(node)
            if node==settings['destination']:
                result=dict(distance_m=distance,segments=path)
                break
            for neighbor,length,sid in adjacency[node]:
                heapq.heappush(queue,(distance+length,neighbor,path+[sid]))
        assert (result is not None)==case['expected_route'], case['id']
        if result:
            assert not blocked.intersection(result['segments'])
        output.append(dict(scenario=case['id'],route=result,is_simulation=True))
    geo=json.loads((ROOT/'jaringan.geojson').read_text(encoding='utf-8'))
    assert len(geo['features'])==len(segments)
    (ROOT/'hasil_validasi.json').write_text(json.dumps(dict(status='passed',scenarios=output),indent=2)+'\n',encoding='utf-8')
    print('PASS: CSV, relasi ID, label simulasi, waktu, bobot, GeoJSON, dan 4 skenario rute.')


if __name__=='__main__':
    main()
