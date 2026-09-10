# Analisis koridor Kota Tangerang (data nyata)

Dibuat 10 September 2026 dari OpenStreetMap (© kontributor, ODbL) dan berita resmi Pemkot Tangerang. **Bukan data simulasi**, kecuali satu skenario berlabel SIM99 (penutupan jalur alternatif untuk uji kasus).

## Rangkuman

1. **Kasus M. Toha terbukti di data resmi.** Dishub Kota Tangerang menetapkan jalur alternatif **Jalan Arya Wangsakara dan Arya Santikan ke arah Otista** untuk M. Toha, sementara **Iskandar Muda dan Marsekal Suryadarma dikerjakan bersamaan** (Agustus 2026) dan Sitanala tanpa rekayasa. Konflik "jalur alternatif ikut diperbaiki" adalah risiko nyata pada jaringan ini.
2. **Penemuan nama OSM:** jalan utama dicatat sebagai **"Jalan Muhammad Thoha"** (ejaan Thoha), bukan nama resmi "M. Toha"; "Jalan Marsekal Suryadarma" tercatat sebagai **"Jalan Surya Darma"** (dua kata, tanpa Marsekal). Pemetaan nama resmi ↔ way OSM wajib manual/konfirmasi; regex kasar kehilangan jalan ini.
3. **Graf koridor nyata:** 37.958 node, 86.362 edge, semua kelas jalan (hanya arteri terfragmentasi jadi ~1.200 komponen; jalan lokal adalah penghubungnya). 143 sekolah, 48 faskes, 28 pasar ikut diambil.
4. **Uji skenario penutupan** (perjalanan: ujung barat M. Toha → simpul jalur alternatif, 5 kaki Dijkstra per kasus; jarak = proksi geometrik, bukan prediksi kemacetan):

| Skenario | Rute terbaik | Δ | Jalur resmi (paksa) | Konflik |
|---|---|---|---|---|
| S0 tanpa penutupan | 5,29 km | – | 8,02 km | rute menembus way pekerjaan aktif M. Toha (sesuai berita: buka-tutup, tidak ditutup) |
| S1 M. Toha sebagian | 5,71 km | +0,42 | 8,36 km | bebas |
| S2 alternatif ikut dikerjakan (SIM99) | 5,71 km | +0,42 | 8,43 km | bebas |
| S3 semua pekerjaan asli sebagian | 5,71 km | +0,42 | 8,36 km | bebas |
| S4 penutupan total semua way | TIDAK ADA RUTE | – | – | menunjukkan kenapa batas segmen penting: berita tidak pernah menutup total |

**Bacaan:** penutupan parsial realistis menaikkan ~0,4 km (+8%) pada graf ini, dan mesin rute menemukan **pengganti lokal yang lebih pendek daripada jalur resmi** untuk perjalanan ini. Jalur resmi Wangsakara–Santika memang dirancang untuk arus lanjut **ke arah Otista (kota)**; `dest` pengujian berhenti di Santika, jadi 8,36 km bukan perbandingan sepadan penuh — gunakan sebagai pembanding, bukan sebagai penilai.

## Cara membuat ulang

```powershell
uv run python scripts/build_corridor_graph.py    # unduh OSM koridor + graf persimpangan
uv run python scripts/map_pekerjaan_osm.py       # pekerjaan resmi -> way OSM (alias)
uv run python scripts/scenario_closures.py       # tabel skenario di atas -> skenario_penutupan.json
uv run python scripts/route_corridor.py          # uji keterhubungan jalur resmi
uv run python scripts/fetch_fasilitas_tangerang.py  # sekolah/pasar/faskes
uv run python scripts/fetch_osm_tangerang.py     # (opsional) jalan bernama se-kota
```

File raw besar (`koridor_raw.json`, `koridor_jaringan.geojson`, `osm_raw.json`) di-`gitignore` (bisa dibuat ulang). Yang masuk git: CSV/GeoJSON ringkas, `skenario_penutupan.json`, `analisis_rute.json`, `pemetaan_pekerjaan_osm.json`, `fasilitas.geojson`, dan semua script.

## Keterbatasan dan langkah berikutnya

- **Teuku Umar (CT05) dan Otista tidak masuk bbox koridor**; Garuda (CT06) sebagian di luar. Perluas bbox bila akan dipakai menutup rute.
- **Batas pekerjaan = perkiraan.** "Sepertiga tengah" cara kasar; butuh koordinat batas & jam pembatasan dari PUPR/Dishub untuk penutupan akurat.
- **Tanpa volume lalu lintas** hasilnya bukan prediksi kemacetan; indikator konflik = rute menembus way pekerjaan lain.
- Data ini Kota Tangerang; Rajeg (Kabupaten) belum tercakup.

## Implikasi untuk JalanTanggap

- Rantai peristiwa yang dialami pengguna (penutupan → alternatif → alternatif juga kerja) **dapat direplikasi dan dinilai otomatis** pada graf nyata + berita resmi.
- Kebutuhan data bertambah satu lapisan: **tabel pemetaan nama resmi ↔ way OSM dengan status verifikasi** (sudah ada: `pemetaan_pekerjaan_osm.json`).
- Uji S0 membuktikan nilai "konflik pasif": bahkan tanpa penutupan, rute terbaik menembus area pekerjaan aktif — persis informasi yang perlu dilihat petugas saat menjadwalkan.