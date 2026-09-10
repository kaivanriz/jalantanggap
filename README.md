# 🛣️ JalanTanggap

## Pilih jalan yang paling perlu diperbaiki, tanpa membuat masalah lalu lintas baru

JalanTanggap adalah rancangan **sistem rekomendasi paket perbaikan jalan berbasis data dan AI**. Sistem membantu pemerintah menjawab pertanyaan:

> **Dari seluruh ruas yang rusak dan laporan warga, jika hanya 10 atau 20 lokasi yang dapat diperbaiki, lokasi mana yang sebaiknya dipilih dan bagaimana pelaksanaannya agar manfaatnya tinggi tetapi dampak kemacetannya tetap terkendali?**

Sistem tidak hanya membuat ranking jalan. JalanTanggap menggabungkan **kondisi jalan + aspirasi warga + AI Traffic Impact Prediction + optimization** untuk menghasilkan paket pekerjaan yang dapat dipertanggungjawabkan.

## Skenario utama

Misalnya tersedia 100 kandidat ruas rusak, sedangkan kapasitas program hanya 20 ruas atau dibatasi anggaran tertentu.

```text
Data kerusakan + laporan warga + konteks pelayanan
                    ↓
        Priority / Need Scoring
                    ↓
           Kandidat perbaikan
                    ↓
       AI Traffic Impact Prediction
                    ↓
 Dampak tiap kandidat ke jaringan sekitar
                    ↓
       Multi-Project Optimization
                    ↓
   Paket 10 / 20 ruas / sesuai anggaran
                    ↓
 Tahapan pelaksanaan + peta dampak + alasan
```

Contoh hasil:

| Ruas | Kebutuhan | Risiko traffic | Keputusan |
|---|---:|---|---|
| Jalan A | 94% | Sedang | Dipilih — Tahap 1 |
| Jalan B | 91% | Tinggi | Tetap prioritas, tetapi jangan bersamaan dengan A |
| Jalan C | 88% | Rendah | Dipilih — Tahap 1 |
| Jalan F | 86% | Rendah | Dipilih — Tahap 1 |

Jalan dengan skor kebutuhan tinggi tidak otomatis dikeluarkan hanya karena berdampak pada lalu lintas. Sistem dapat merekomendasikan **waktu/tahap berbeda**.

## Tiga mesin keputusan

### 1. Priority / Need Scoring
Menilai seberapa penting suatu ruas ditangani berdasarkan data terverifikasi, misalnya tingkat dan panjang kerusakan, dampak akses, fungsi jalan, lama belum ditangani, fasilitas publik, serta laporan warga yang valid.

Pada MVP, bila belum tersedia label historis yang memadai, scoring dapat menggunakan SAW/rule-based yang transparan. Setelah tersedia data keputusan dan outcome historis, model ML dapat dikembangkan untuk membantu priority prediction.

### 2. AI Traffic Impact Prediction
Memprediksi efek pekerjaan pada ruas sekitar berdasarkan histori lalu lintas, karakteristik jaringan, waktu pekerjaan, kapasitas/lajur, pekerjaan aktif, dan aktivitas sekitar.

Contoh:

```text
Perbaikan Jalan A — Senin 07.00–16.00 — 1 lajur ditutup

🔴 Simpang X    risiko 92%
🔴 Jalan K      risiko 87%
🟡 Jalan D      risiko 64%
🟢 Jalan E      risiko 18%
```

Untuk MVP, model yang disarankan adalah **XGBoost atau Random Forest**. Jika kelak tersedia histori sensor/CCTV yang besar, dapat dikembangkan ke model spatio-temporal graph.

### 3. Multi-Project Optimization
Memilih kombinasi pekerjaan terbaik, bukan sekadar mengambil ranking 10/20 teratas.

Optimizer mempertimbangkan manfaat, risiko lalu lintas, konflik antarpekerjaan, jumlah proyek, anggaran, periode pelaksanaan, dan constraint teknis.

Secara konseptual:

```text
maximize:
  manfaat_perbaikan - risiko_kemacetan - konflik_proyek

subject to:
  jumlah_proyek <= target
  total_biaya <= anggaran
  proyek_berkonflik tidak dijalankan bersamaan
```

Metode yang dapat digunakan: **Mixed Integer Programming / constraint optimization**.

## Masukan sistem

- laporan/aspirasi warga;
- hasil verifikasi kondisi jalan;
- tingkat dan panjang kerusakan;
- kelas/fungsi/kewenangan jalan;
- fasilitas penting di sekitar;
- riwayat penanganan;
- estimasi biaya dan durasi pekerjaan;
- jaringan jalan;
- histori volume, kecepatan, dan kepadatan;
- pekerjaan aktif/terjadwal;
- jenis dan waktu pembatasan lajur;
- aktivitas sekolah, pasar, faskes, atau event.

## Keluaran utama

Petugas dapat memilih mode **Top 10**, **Top 20**, atau **berdasarkan anggaran**. Sistem menghasilkan:

- paket ruas yang direkomendasikan;
- alasan pemilihan dan faktor dominan;
- kandidat penting yang belum dipilih beserta alasannya;
- heatmap dampak lalu lintas;
- ranking ruas/kawasan terdampak;
- matriks konflik antarpekerjaan;
- pekerjaan yang relatif aman dilakukan bersamaan;
- pekerjaan yang perlu dipisahkan tahap/waktunya;
- skenario jadwal;
- confidence/ketidakpastian model;
- jalur alternatif sebagai fitur pendukung bila diperlukan.

## Peran AI dan non-AI

| Komponen | Fungsi | AI? |
|---|---|---|
| LLM | Ekstraksi dan klarifikasi laporan warga, penjelasan hasil | Ya |
| XGBoost / Random Forest | Traffic Impact Prediction | Ya |
| Priority ML | Pengembangan lanjutan bila label historis tersedia | Ya |
| SAW / rule scoring | Baseline prioritas yang transparan | Tidak |
| Graph analysis | Konektivitas dan penyebaran dampak | Tidak harus AI |
| Optimization | Memilih paket dan tahapan dengan constraint | Optimisasi matematis |
| Dijkstra / A* | Jalur alternatif opsional | Tidak |

## Prinsip penting

- **Manusia tetap pengambil keputusan akhir.**
- Jumlah laporan warga tidak boleh menjadi satu-satunya penentu prioritas.
- LLM tidak boleh menebak kondisi teknis, volume, biaya, atau kapasitas jalan.
- Jika histori traffic belum cukup, keluaran harus disebut **risk scoring/baseline**, bukan prediksi AI.
- Model AI harus divalidasi sebelum digunakan untuk rekomendasi operasional.
- Ruas yang sangat mendesak tetap dapat direkomendasikan walaupun berdampak tinggi, dengan mitigasi jadwal/tahapan.

## Teknologi yang direncanakan

| Komponen | Rencana |
|---|---|
| Backend | Python / FastAPI |
| Database spasial | PostgreSQL + PostGIS |
| Peta | Leaflet / OpenStreetMap |
| Jaringan jalan | OSMnx / NetworkX |
| AI Traffic Impact | XGBoost / Random Forest |
| Optimizer | OR-Tools / Pyomo atau solver setara |
| Priority baseline | SAW / rule-based |
| LLM | Ekstraksi laporan dan penjelasan |
| Rute opsional | Dijkstra / A* |
| Visualisasi | Heatmap, timeline, matriks konflik, paket rekomendasi |

## Dokumentasi

- [Rencana proyek](Rencana-Proyek.md)
- [Kebutuhan data](Kebutuhan-Data.md)
- [AI Traffic Impact Prediction](AI-Traffic-Impact.md)
- [Data nyata Kota Tangerang](data/real-tangerang/README.md)
- [Analisis koridor Kota Tangerang](data/real-tangerang/analisis_koridor.md)
- [Data sampel Tangerang–Rajeg](data/sample-tangerang/README.md)

## Status

Tahap **perencanaan dan dokumentasi**. Angka pada contoh merupakan ilustrasi, bukan hasil pengukuran nyata. Prioritas awal dapat dibangun dengan metode transparan sambil mengumpulkan histori yang diperlukan untuk model AI.
