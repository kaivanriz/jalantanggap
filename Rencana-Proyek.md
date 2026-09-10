# Rencana Proyek JalanTanggap

## Sistem Pendukung Keputusan Perbaikan Jalan yang Berevolusi dari SAW ke AI dan Intelligent Planning

> **Acuan utama:** [ROADMAP.md](ROADMAP.md). Jika terdapat perbedaan urutan fase, ROADMAP.md menjadi source of truth.

## 1. Ringkasan

JalanTanggap membantu pemerintah mengolah laporan warga dan hasil survei jalan menjadi rekomendasi prioritas yang transparan. Sistem dikembangkan bertahap: MVP menggunakan NLP + SAW, lalu data historis yang terkumpul digunakan untuk AI Prioritization, pemilihan paket melalui optimization, prediksi dampak lalu lintas, dan akhirnya intelligent road maintenance planning.

Tujuan akhir:

> Dari seluruh ruas yang membutuhkan penanganan, ruas mana yang perlu diperbaiki, kombinasi mana yang paling sesuai dengan anggaran/sumber daya, mana yang dapat dikerjakan bersamaan, kapan sebaiknya dikerjakan, dan wilayah mana yang berpotensi terdampak lalu lintas?

## 2. Prinsip

- Laporan warga adalah masukan, bukan pengganti survei teknis.
- BERT/SBERT membantu memahami dan mengelompokkan laporan warga.
- SAW adalah DSS/MCDM, bukan AI, dan digunakan sebagai baseline Fase 1.
- AI Prioritization dikembangkan setelah histori keputusan dan outcome tersedia.
- AI tidak dilatih hanya untuk meniru skor SAW.
- Optimization adalah optimisasi matematis yang menggunakan skor/prediksi dari komponen sebelumnya.
- Traffic AI baru digunakan jika data historis traffic dan roadworks memadai.
- Human-in-the-loop: keputusan akhir tetap pada petugas/pejabat dan override dicatat.

## 3. Arsitektur Evolusi

```text
FASE 1
Laporan Warga → BERT/SBERT → Verifikasi ─┐
                                         ├→ SAW → Ranking Top 10/20
Survey Jalan ────────────────────────────┘
                    ↓
            simpan histori/outcome
                    ↓
FASE 2
Historical Dataset → AI Priority Model → AI Priority Score
                    ↓
FASE 3
AI Priority + Cost + Budget + Resource → Optimizer → Paket Pekerjaan
                    ↓
FASE 4
Historical Traffic + Roadworks + Graph → Traffic Impact AI → Area Terdampak
                    ↓
FASE 5
AI Priority + Traffic AI + Constraints → Multi-Project Optimizer
                    ↓
Paket + Tahapan + Jadwal + Heatmap + Konflik + Alasan
```

## 4. Fase 1 — Smart Reporting + Survey + SAW

### NLP laporan warga
BERT/IndoBERT atau model NLP Bahasa Indonesia digunakan untuk klasifikasi dan ekstraksi laporan. Sentence-BERT/sentence embedding digunakan untuk semantic similarity, clustering, dan kandidat deduplikasi.

Contoh alur:

```text
Teks laporan
   ↓
BERT/NLP
   ↓
kategori + masalah + dampak + landmark
   ↓
SBERT similarity + lokasi + waktu
   ↓
kandidat cluster/duplikat
   ↓
verifikasi petugas
```

NLP tidak menetapkan tingkat kerusakan teknis final.

### Survey dan SAW
Data laporan terverifikasi digabungkan dengan survei teknis. Kriteria SAW dapat mencakup tingkat/panjang kerusakan, fungsi jalan, dampak akses, laporan valid, lama belum ditangani, fasilitas penting, dan riwayat penanganan.

Output:
- laporan terstruktur dan terdeduplikasi;
- data survei terverifikasi;
- skor SAW per ruas;
- ranking prioritas;
- Top 10/Top 20;
- peta prioritas;
- alasan per kriteria.

### Data yang harus disimpan
Simpan input, skor SAW, keputusan ahli, dipilih/tidak, biaya, pelaksanaan, kondisi sebelum/sesudah, dan outcome. Data inilah yang menjadi fondasi Fase 2.

## 5. Fase 2 — AI Prioritization

Historical dataset dari Fase 1 digunakan untuk mengembangkan model ML seperti XGBoost, LightGBM, Random Forest, atau model lain yang terbukti lebih baik pada validasi.

```text
Historical JalanTanggap
        ↓
Cleaning + Feature Engineering
        ↓
Train / Validation / Test
        ↓
AI Priority Model
        ↓
AI Priority Score
        ↓
Evaluasi vs SAW + ahli + outcome
```

SAW tetap tersedia sebagai baseline/audit. Target AI sebisa mungkin berasal dari keputusan ahli berkualitas dan outcome nyata, bukan sekadar skor SAW.

Output:
- AI Priority Score;
- explanation/feature importance;
- evaluasi terhadap baseline;
- rekomendasi prioritas berbasis AI.

## 6. Fase 3 — AI-Assisted Multi-Project Optimization

Fase ini menjawab pertanyaan paket: jika kandidat banyak tetapi anggaran/resource terbatas, kombinasi mana yang terbaik?

Input:
- AI Priority Score;
- biaya;
- durasi;
- anggaran;
- target jumlah ruas;
- kapasitas tim/resource;
- periode dan constraint teknis.

Kandidat teknologi: OR-Tools CP-SAT, MILP/Pyomo, atau solver setara.

```text
maximize total_benefit
subject to:
  total_cost <= budget
  project_count <= target
  simultaneous_projects <= team_capacity
  technical_constraints satisfied
```

Output:
- paket Top 10/Top 20;
- paket berdasarkan anggaran;
- kandidat terpilih/tidak terpilih beserta alasan;
- penggunaan anggaran;
- tahapan awal berdasarkan resource constraint.

## 7. Fase 4 — AI Traffic Impact Prediction

Traffic AI memprediksi dampak rencana pekerjaan pada jaringan sekitar. Detail teknis terdapat pada [AI-Traffic-Impact.md](AI-Traffic-Impact.md).

Input utama:
- historical traffic;
- historical roadworks;
- volume/speed/free-flow speed;
- kapasitas/lajur;
- waktu pekerjaan dan jenis penutupan;
- jaringan jalan/graph;
- pekerjaan aktif;
- aktivitas sekitar jika tersedia.

Target dapat berupa `delta_volume`, `delta_speed`, `congestion_probability`, dan risk class. MVP dapat mengevaluasi XGBoost/Random Forest + graph features. ST-GNN baru dievaluasi bila time-series sensor/CCTV memadai.

Jika histori belum cukup, keluaran disebut baseline/risk scoring, bukan prediksi AI tervalidasi.

## 8. Fase 5 — Intelligent Road Maintenance Planning

Semua komponen digabungkan:

```text
BERT/SBERT + Survey
        ↓
AI Priority
        │
        ├──────────────┐
        ↓              ↓
Budget/Resource   Traffic Impact AI
        │              │
        └──────┬───────┘
               ↓
      Multi-Project Optimizer
               ↓
 Paket + Tahapan + Jadwal + Heatmap
```

Sistem dapat menilai konflik antarpekerjaan, memisahkan proyek yang berdampak pada koridor sama, membandingkan skenario, dan menampilkan uncertainty. Jalur alternatif tetap menjadi fitur pendukung bila diperlukan.

## 9. Alur Pengguna

1. Warga mengirim laporan, lokasi, deskripsi, dan foto.
2. NLP mengklasifikasikan/mengekstrak informasi dan membantu kandidat deduplikasi.
3. Petugas memverifikasi laporan dan melakukan/memasukkan hasil survei.
4. Pada Fase 1, SAW menghasilkan ranking transparan.
5. Sistem menyimpan keputusan dan outcome sebagai historical dataset.
6. Pada Fase 2+, AI Priority memberikan rekomendasi prioritas.
7. Pada Fase 3+, petugas memilih target jumlah/anggaran dan optimizer membentuk paket.
8. Pada Fase 4+, Traffic AI menilai dampak paket/rencana pekerjaan.
9. Pada Fase 5, optimizer menggabungkan priority, resource, traffic impact, dan konflik untuk menyusun skenario tahapan/jadwal.
10. Petugas menyetujui atau override dengan alasan tercatat; outcome kembali masuk ke dataset.

## 10. Arsitektur Teknologi

| Komponen | Teknologi kandidat | Peran |
|---|---|---|
| Backend | Python / FastAPI | API dan orkestrasi |
| Database | PostgreSQL + PostGIS | transaksi, spasial, histori |
| WebGIS | Leaflet / OpenStreetMap | visualisasi |
| NLP | BERT/IndoBERT | klasifikasi/ekstraksi laporan |
| Semantic similarity | SBERT/Sentence Transformer | clustering/deduplikasi kandidat |
| Priority Fase 1 | SAW | baseline transparan |
| AI Priority | XGBoost/LightGBM/RF | rekomendasi prioritas setelah dataset tersedia |
| Graph | OSMnx + NetworkX | relasi jaringan/feature engineering |
| Optimization | OR-Tools/CP-SAT/MILP/Pyomo | paket dan tahapan |
| Traffic AI | XGBoost/RF; ST-GNN lanjutan | prediksi dampak traffic |
| Routing opsional | Dijkstra/A* | jalur alternatif |

## 11. Tahapan Implementasi Resmi

| Fase | Fokus | Output |
|---|---|---|
| 1 | BERT/SBERT + survey + SAW | ranking Top 10/20 dan dataset historis |
| 2 | AI Prioritization | AI Priority Score dan evaluasi vs SAW |
| 3 | Optimization | paket berdasarkan target/anggaran/resource |
| 4 | Traffic Impact AI | prediksi area/ruas terdampak + heatmap |
| 5 | Intelligent Planning | paket + tahapan + jadwal + dampak + konflik |

## 12. Evaluasi

### Fase 1
- kualitas klasifikasi/ekstraksi NLP;
- precision kandidat deduplikasi;
- kesesuaian data dengan verifikasi;
- transparansi/stabilitas SAW;
- audit faktor penentu.

### AI Priority
- performa terhadap label/outcome yang disepakati;
- evaluasi temporal dan data leakage;
- calibration bila probabilistik;
- explainability dan bias wilayah.

### Traffic AI
- MAE/RMSE untuk target numerik;
- precision/recall/F1 untuk risiko;
- akurasi spasial area terdampak;
- calibration/confidence.

### Optimizer
- total benefit dibanding Top-N sederhana;
- penggunaan anggaran;
- constraint violations = 0;
- jumlah konflik yang berhasil dihindari;
- sensitivitas terhadap parameter.

## 13. Tata Kelola

- Keputusan akhir tidak otomatis dibuat AI.
- Override manusia dicatat.
- Model, versi dataset, parameter SAW/optimizer, dan hasil rekomendasi dicatat untuk audit.
- Identitas warga tidak digunakan sebagai fitur priority tanpa dasar kebutuhan yang sah.
- Data teknis tidak dihasilkan oleh NLP/LLM.
- Ketidakpastian ditampilkan.
- Model hanya dipromosikan ke tahap operasional setelah evaluasi yang sesuai.

## 14. Keluaran Proyek

1. aplikasi JalanTanggap;
2. modul laporan warga + NLP;
3. modul survey/verifikasi;
4. SAW priority baseline;
5. historical dataset dan outcome feedback;
6. AI Priority Model;
7. multi-project optimizer;
8. AI Traffic Impact Prediction;
9. WebGIS/dashboard ranking, heatmap, timeline, dan conflict matrix;
10. dokumentasi model, data, asumsi, evaluasi, dan audit trail.
