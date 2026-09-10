# Data Demo JalanTanggap — Tangerang

> **SIMULASI.** Seluruh koordinat, nama jalan, laporan, survey, proyek, dan lalu lintas pada folder ini dibuat untuk pengujian. Bukan data kondisi jalan Kota Tangerang yang sebenarnya dan tidak boleh digunakan untuk keputusan lapangan atau navigasi.

Folder ini sekarang memiliki dua kelompok fixture: **fixture Fase 1** untuk Smart Reporting → NLP → map matching → deduplikasi → survey → SAW, serta **fixture legacy/Fase 4** yang sebelumnya dipakai untuk routing dan Traffic Impact AI.

## Fixture Fase 1 — direkomendasikan untuk pengembangan saat ini

Generator:

```bash
python scripts/generate_phase1_sample.py
```

Generator tersebut menghasilkan:

| File | Fungsi |
|---|---|
| `laporan_fase1.csv` | input mentah pengaduan: deskripsi + latitude/longitude; tidak membawa jawaban `id_segmen` atau label duplikasi |
| `ground_truth_fase1.csv` | ground truth terpisah untuk evaluasi map matching, NLP, dan deduplikasi |
| `survey_fase1.csv` | hasil survey teknis sintetis untuk 20 segmen kandidat |
| `aturan_fase1.json` | aturan pengujian map matching, deduplikasi, dan bobot SAW demo |

### Mengapa dipisah?

Fixture lama `laporan.csv` sudah mengandung `id_segmen`, `status`, dan `id_cluster_duplikat`. Itu berguna untuk demo lama tetapi dapat menyebabkan **label leakage** jika langsung dipakai sebagai input model.

Pada fixture Fase 1, input model hanya menerima data yang secara realistis tersedia dari aplikasi pengaduan:

```text
id_laporan
id_pelapor
waktu
latitude
longitude
deskripsi
foto_url
status=submitted
```

Jawaban yang diharapkan disimpan terpisah di `ground_truth_fase1.csv`.

## Desain data pengaduan Fase 1

Dataset generator membuat **100 pengaduan sintetis pada 20 ruas**. Setiap ruas memiliki dua kejadian sintetis pada posisi berbeda. Satu kejadian memiliki 3 laporan dan satu kejadian memiliki 2 laporan, sehingga semantic deduplication dapat diuji tanpa menganggap semua laporan pada satu ruas adalah kejadian yang sama.

Koordinat:
- selalu tersedia, mengikuti kondisi aplikasi pengaduan existing;
- dibuat dekat geometri ruas sintetis;
- diberi offset/jitter hingga sekitar 15 meter dari garis ruas;
- titik kejadian dijauhkan dari simpang agar ground truth map matching tidak ambigu.

Teks laporan memiliki variasi seperti:
- lubang;
- retak memanjang;
- aspal mengelupas;
- permukaan bergelombang;
- genangan;
- aspal amblas.

Terdapat parafrasa pada satu kejadian agar SBERT/sentence embedding dapat diuji untuk semantic similarity.

## Ground truth Fase 1

`ground_truth_fase1.csv` tidak boleh dimasukkan sebagai feature saat inferensi. File tersebut hanya untuk evaluasi dan berisi antara lain:

```text
expected_id_segmen
expected_category
expected_indication
expected_impact
expected_landmark
expected_duplicate_group
expected_is_duplicate
split
```

Dengan pemisahan ini kita dapat menghitung metrik secara jujur:
- accuracy map matching `coordinate → id_segmen`;
- classification/extraction NLP;
- precision/recall/F1 kandidat duplikasi.

## Survey Fase 1

`survey_fase1.csv` berisi 20 survey sintetis dengan:

```text
tingkat_kerusakan
jenis_kerusakan
panjang_rusak_m
dampak_akses
peran_jalan
fasilitas_kritis
lama_tidak_ditangani_hari
```

Survey merupakan sumber nilai teknis. **NLP laporan warga tidak boleh menetapkan tingkat kerusakan teknis final.**

## SAW Fase 1

`aturan_fase1.json` menggunakan bobot demo:

| Kriteria | Bobot |
|---|---:|
| tingkat kerusakan | 30% |
| dampak akses | 20% |
| peran jalan | 15% |
| panjang rusak | 15% |
| jumlah laporan valid | 10% |
| fasilitas kritis | 5% |
| lama tidak ditangani | 5% |

Jumlah laporan valid dihitung **setelah map matching, NLP/deduplikasi, dan verifikasi**, bukan dari jumlah baris mentah. Bobot dan skala hanya fixture pengembangan, bukan standar teknis PUPR.

## Pipeline uji Fase 1

```text
laporan_fase1.csv
        ↓
Map Matching koordinat → segmen.csv / jaringan.geojson
        ↓
BERT/IndoBERT → klasifikasi & ekstraksi
        ↓
SBERT → semantic similarity
        +
jarak koordinat + selisih waktu
        ↓
Candidate Duplicate
        ↓
Verifikasi
        +
survey_fase1.csv
        ↓
SAW (aturan_fase1.json)
        ↓
Ranking Top 10 / Top 20
```

Target awal map matching adalah `expected_id_segmen` pada ground truth. Untuk duplicate detection, target cluster adalah `expected_duplicate_group`.

## Fixture lama / kompatibilitas

File-file berikut tetap dipertahankan agar demo dan validator lama tidak rusak:

| File | Fungsi lama |
|---|---|
| `nodes.csv` | 25 simpul jaringan skematis |
| `segmen.csv` | 40 ruas sintetis |
| `jaringan.geojson` | geometri jaringan untuk Leaflet/map matching |
| `laporan.csv` | fixture laporan legacy; mengandung label/hasil yang tidak cocok sebagai raw input ML |
| `label_llm.csv` | label NLP legacy berbasis template |
| `penilaian.csv` | penilaian SAW legacy |
| `aturan.json` | aturan SAW/routing legacy |
| `proyek.csv`, `pembatasan.csv`, `aktivitas.csv` | fixture proyek/aktivitas |
| `roadworks_events.csv` | historical roadworks sintetis Fase 4 |
| `traffic_history.csv` | historical traffic sintetis Fase 4 |
| `traffic_ai_dataset.csv` | dataset Traffic AI sintetis Fase 4 |
| `skenario.json`, `hasil_validasi.json` | skenario/hasil routing demo lama |
| `waze_feed_contoh.json` | contoh struktur feed sintetis |

Generator lama tetap tersedia:

```bash
python scripts/generate_sample.py
python scripts/validate_sample.py
```

`generate_sample.py` dapat menimpa fixture legacy. Fixture Fase 1 baru dikelola oleh `generate_phase1_sample.py` agar perubahan untuk roadmap saat ini tidak merusak demo Traffic AI yang sudah ada.

## Relasi data

```text
segmen.from_node/to_node → nodes.id_node
survey_fase1.id_segmen → segmen.id_segmen
ground_truth_fase1.expected_id_segmen → segmen.id_segmen
ground_truth_fase1.id_laporan → laporan_fase1.id_laporan
```

`jaringan.geojson` menggunakan koordinat GeoJSON `[longitude, latitude]`, sedangkan CSV laporan menyimpan `latitude` dan `longitude` sebagai kolom terpisah.

## Batas penggunaan

Fixture sintetis hanya membuktikan pipeline dapat berjalan. Akurasi pada fixture ini **bukan** bukti performa terhadap laporan warga nyata. Sebelum pilot, diperlukan data pengaduan nyata yang dianonimkan sesuai kebutuhan, data ruas/GIS yang diverifikasi, survey teknis, serta evaluasi dengan label independen.

Roadmap utama proyek tetap berada di [`ROADMAP.md`](../../ROADMAP.md).
