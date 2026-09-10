# 🛣️ JalanTanggap

## Dari laporan warga menjadi perencanaan perbaikan jalan berbasis data dan AI

**JalanTanggap** adalah rancangan sistem pendukung keputusan untuk membantu pemerintah menentukan ruas jalan yang perlu diprioritaskan, memilih paket pekerjaan sesuai anggaran dan sumber daya, serta pada tahap lanjut memprediksi dampak pekerjaan terhadap lalu lintas.

Pengembangan JalanTanggap dilakukan **bertahap**. Sistem tidak langsung bergantung pada AI ketika data historis belum tersedia. MVP dimulai dari **NLP untuk laporan warga + survei teknis + SAW**, kemudian berevolusi menjadi **AI Prioritization, Multi-Project Optimization, AI Traffic Impact Prediction, dan Intelligent Planning**.

> **Tujuan akhir:** menjawab ruas mana yang perlu diperbaiki, ruas mana yang dapat dikerjakan bersamaan, kapan sebaiknya dikerjakan, dan wilayah mana yang berpotensi terdampak lalu lintas.

---

## 🧭 Roadmap Utama

```text
JalanTanggap 1.0
BERT/SBERT + Survey Jalan + SAW
        ↓
"Mana jalan yang prioritas?"

JalanTanggap 2.0
NLP + Historical Dataset + AI Prioritization
        ↓
"Mana jalan yang direkomendasikan AI?"

JalanTanggap 3.0
AI Priority + Anggaran + Resource + Optimization
        ↓
"Dengan keterbatasan yang ada, paket pekerjaan mana yang terbaik?"

JalanTanggap 4.0
+ Historical Traffic + Road Network + Traffic Impact AI
        ↓
"Jika pekerjaan dilakukan, wilayah mana yang berpotensi terdampak?"

JalanTanggap 5.0
NLP + AI Priority + Traffic AI + Graph + Optimization
        ↓
"Mana yang diperbaiki, kapan, mana yang dapat bersamaan, dan apa dampaknya?"
```

Roadmap lengkap dan Definition of Done setiap fase tersedia di **[ROADMAP.md](ROADMAP.md)**.

---

# Fase 1 — Smart Reporting + Survey + SAW

Fase pertama adalah MVP yang dapat digunakan meskipun belum tersedia dataset historis besar.

```text
Laporan Warga
     ↓
BERT / NLP
     ↓
Klasifikasi + Ekstraksi
     ↓
SBERT / Semantic Similarity
     ↓
Deteksi kandidat laporan duplikat
     ↓
Verifikasi Petugas
     +
Survey Kondisi Jalan
     ↓
Data Ruas Terverifikasi
     ↓
SAW
     ↓
Priority Score
     ↓
Ranking Top 10 / Top 20
```

## BERT / NLP untuk laporan warga

BERT/IndoBERT atau model NLP Bahasa Indonesia digunakan untuk memahami teks laporan warga, misalnya:

- klasifikasi jenis laporan;
- ekstraksi jenis masalah seperti lubang, genangan, atau kerusakan permukaan;
- identifikasi dampak yang dilaporkan warga;
- ekstraksi landmark/lokasi dari teks;
- normalisasi laporan.

**Sentence-BERT/SBERT** atau sentence embedding digunakan untuk semantic similarity, clustering, dan membantu mendeteksi laporan yang kemungkinan membahas kejadian yang sama.

```text
"Jalan depan pasar banyak lubang"
              ≈
"Aspal rusak parah dekat pasar"
              ↓
Similarity teks + lokasi + waktu
              ↓
Kandidat laporan yang sama
              ↓
Verifikasi petugas
```

NLP **tidak menggantikan survei teknis**. Pernyataan warga seperti "rusak parah" hanya menjadi indikasi awal. Tingkat kerusakan final berasal dari hasil survei/verifikasi teknis.

## SAW sebagai baseline prioritas

Pada fase awal, **Simple Additive Weighting (SAW)** digunakan karena transparan, mudah diaudit, dan belum membutuhkan dataset training besar.

Kriteria dapat mencakup:

- tingkat kerusakan hasil survei;
- panjang/luas kerusakan;
- fungsi atau kelas jalan;
- dampak akses;
- jumlah laporan warga valid dan terdeduplikasi;
- lama belum ditangani;
- fasilitas publik/akses penting;
- riwayat penanganan.

Output Fase 1:

```text
1. Jalan A    0.94
2. Jalan C    0.91
3. Jalan F    0.88
...
10. Jalan K   0.72
```

Petugas memperoleh **ranking prioritas, Top 10/Top 20, peta prioritas, dan alasan skor per kriteria**.

SAW adalah metode DSS/MCDM dan **bukan AI**.

---

# Fase 2 — AI Prioritization

Selama Fase 1 berjalan, JalanTanggap menyimpan histori:

```text
Laporan warga
Hasil NLP
Hasil survey
SAW score
Keputusan petugas
Dipilih / tidak dipilih
Biaya dan pelaksanaan
Kondisi sebelum / sesudah
Outcome
        ↓
Historical JalanTanggap Dataset
```

Dataset tersebut digunakan untuk mengembangkan model prioritas berbasis machine learning.

```text
Historical Dataset
        ↓
Feature Engineering
        ↓
XGBoost / LightGBM / Random Forest / model terpilih
        ↓
AI Priority Model
        ↓
AI Priority Score
```

Pada fase ini, **SAW tidak langsung dihapus**. SAW menjadi baseline untuk membandingkan hasil AI dan membantu audit keputusan.

AI juga tidak sebaiknya dilatih hanya untuk meniru skor SAW. Target training diarahkan pada keputusan ahli yang terverifikasi dan outcome nyata agar model dapat memberikan nilai tambah dibanding formula awal.

---

# Fase 3 — AI-Assisted Multi-Project Optimization

Setelah tersedia AI Priority Score, masalah berkembang dari sekadar ranking menjadi pemilihan **kombinasi proyek terbaik**.

Contoh:

```text
73 kandidat jalan
Anggaran Rp20 miliar
Maksimal 20 ruas
4 tim pekerjaan
Periode pelaksanaan tertentu
        ↓
AI Priority + Cost + Duration + Resource
        ↓
Optimizer
        ↓
Paket pekerjaan terbaik
```

Optimizer dapat menggunakan **OR-Tools CP-SAT, MILP/Pyomo, atau metode constraint optimization lain**.

Secara konseptual:

```text
maximize:
    total manfaat / priority

subject to:
    total_biaya <= anggaran
    jumlah_proyek <= target
    proyek_simultan <= kapasitas_tim
    constraint teknis terpenuhi
```

Optimizer tidak harus menghasilkan tepat 20 ruas. Jika kombinasi terbaik dalam batas anggaran adalah 17 ruas, sistem dapat merekomendasikan 17 ruas disertai alasannya.

Optimization di sini adalah **optimisasi matematis**, sedangkan AI digunakan untuk menghasilkan informasi/prediksi yang menjadi input optimizer.

---

# Fase 4 — AI Traffic Impact Prediction

Fase ini menambahkan kemampuan untuk memperkirakan **dampak pekerjaan jalan terhadap jaringan lalu lintas di sekitarnya**.

Data utama:

- historical traffic;
- historical roadworks;
- volume kendaraan;
- kecepatan/free-flow speed;
- congestion index;
- waktu dan hari;
- kapasitas/jumlah lajur;
- jenis penutupan;
- jaringan jalan/graph;
- pekerjaan aktif;
- aktivitas sekitar bila tersedia.

```text
Rencana Pekerjaan
       +
Historical Traffic
       +
Historical Roadworks
       +
Road Network
       ↓
Traffic Impact AI
       ↓
Delta Volume / Delta Speed
       ↓
Congestion Probability
       ↓
Affected Roads / Areas
       ↓
Heatmap Dampak
```

Untuk MVP Traffic AI, kandidat awal adalah **XGBoost/Random Forest + fitur spasial/graph**. Jika kemudian tersedia time-series sensor/CCTV dalam skala besar, dapat dievaluasi model **spatio-temporal graph neural network**.

Contoh output:

```text
Perbaikan Jalan A
Senin 07.00–16.00
1 dari 2 lajur ditutup

🔴 Jalan B       risiko 91%
🔴 Simpang X     risiko 86%
🟡 Jalan C       risiko 64%
🟢 Jalan D       risiko 17%
```

Jika data historis belum memadai, sistem harus menyebut hasil sebagai **risk scoring/baseline**, bukan prediksi AI tervalidasi.

---

# Fase 5 — Intelligent Road Maintenance Planning

Fase akhir mengintegrasikan seluruh komponen.

```text
                 LAPORAN WARGA
                       ↓
                  BERT / NLP
                       ↓
                 DATA SURVEY
                       ↓
              AI PRIORITY MODEL
                       ↓
              Kandidat Perbaikan
                       │
         ┌─────────────┴─────────────┐
         ↓                           ↓
 Anggaran / Resource         Historical Traffic
                                     ↓
                            TRAFFIC IMPACT AI
         │                           │
         └─────────────┬─────────────┘
                       ↓
              MULTI-PROJECT OPTIMIZER
                       ↓
              REKOMENDASI PROGRAM
                       ↓
       ┌───────────────┼───────────────┐
       ↓               ↓               ↓
 Paket Jalan       Tahapan/Jadwal   Dampak Traffic
 Top 10/20         Timeline         Heatmap
```

Pada tahap ini JalanTanggap ditujukan untuk menjawab:

> **Dengan anggaran dan sumber daya yang tersedia, ruas mana yang sebaiknya diperbaiki, mana yang dapat dikerjakan bersamaan, kapan waktu pelaksanaannya, dan wilayah mana yang berpotensi terkena dampak lalu lintas?**

Output dapat mencakup paket ruas, alasan rekomendasi, penggunaan anggaran, tahapan pekerjaan, konflik antarproyek, heatmap dampak, confidence model, dan beberapa skenario perencanaan.

Jalur alternatif tetap dapat dikembangkan sebagai **fitur pendukung**, tetapi bukan fokus utama sistem.

---

## Peran AI dan Non-AI

| Komponen | Fungsi | Kategori |
|---|---|---|
| BERT / IndoBERT | Memahami dan mengklasifikasikan laporan warga | NLP / AI |
| SBERT / Sentence Embedding | Similarity, clustering, kandidat deduplikasi laporan | NLP / AI |
| SAW | Baseline prioritas Fase 1 | DSS / MCDM, bukan AI |
| XGBoost / LightGBM / RF | Kandidat AI Priority Model | Machine Learning |
| Traffic Impact Model | Prediksi dampak lalu lintas | Machine Learning / AI |
| Graph Analysis | Relasi dan propagasi antar ruas | Algoritmik, tidak harus AI |
| OR-Tools / MILP / CP-SAT | Memilih paket/tahapan berdasarkan constraint | Mathematical Optimization |
| Dijkstra / A* | Jalur alternatif opsional | Algoritma routing, bukan AI |

---

## Prinsip Sistem

- **Human-in-the-loop:** keputusan akhir tetap pada petugas/pejabat berwenang.
- Laporan warga adalah input penting, tetapi bukan satu-satunya penentu prioritas.
- NLP tidak boleh menggantikan hasil survei teknis.
- Laporan duplikat harus ditangani agar jumlah laporan tidak memanipulasi skor.
- SAW digunakan sebagai baseline transparan sebelum dataset AI matang.
- AI harus divalidasi terhadap data nyata dan outcome, bukan sekadar meniru SAW.
- Confidence/uncertainty model harus ditampilkan jika tersedia.
- Semua rekomendasi dan override manusia harus memiliki audit trail.

---

## Teknologi yang Direncanakan

| Komponen | Teknologi |
|---|---|
| Backend/API | Python / FastAPI |
| Database spasial | PostgreSQL + PostGIS |
| WebGIS | Leaflet / OpenStreetMap |
| NLP | BERT/IndoBERT + Sentence-BERT/Sentence Transformer |
| Priority MVP | SAW |
| AI Prioritization | XGBoost / LightGBM / Random Forest atau model terpilih |
| Road graph | OSMnx / NetworkX |
| Traffic Impact AI | XGBoost / Random Forest, lanjut ST-GNN bila data memadai |
| Optimization | OR-Tools / CP-SAT / MILP / Pyomo |
| Routing opsional | Dijkstra / A* |
| Visualisasi | Ranking, WebGIS, heatmap, timeline, conflict matrix |

---

## Dokumentasi


- [Sumber data eksternal (OSM, Google Maps, Dishub)](SUMBER-DATA-EKSTERNAL.md)
- **[ROADMAP.md](ROADMAP.md)** — acuan utama urutan pengembangan dan Definition of Done.
- [Rencana-Proyek.md](Rencana-Proyek.md) — rancangan proyek dan arsitektur.
- [Kebutuhan-Data.md](Kebutuhan-Data.md) — kebutuhan dataset setiap komponen.
- [AI-Traffic-Impact.md](AI-Traffic-Impact.md) — rancangan khusus Traffic Impact AI.
- [Data nyata Kota Tangerang](data/real-tangerang/README.md)
- [Analisis koridor Kota Tangerang](data/real-tangerang/analisis_koridor.md)
- [Data sampel Tangerang–Rajeg](data/sample-tangerang/README.md)

---

## Status Pengembangan

**Fokus saat ini: Fase 1 — Smart Reporting + Survey + SAW.**

Prioritas implementasi:

```text
Database & Data Ruas
        ↓
Laporan Warga
        ↓
BERT / SBERT
        ↓
Verifikasi Petugas
        ↓
Survey Jalan
        ↓
SAW
        ↓
Ranking Top 10 / Top 20
        ↓
WebGIS / Dashboard
```

Fase AI berikutnya dikembangkan setelah data historis yang dibutuhkan mulai tersedia dan dapat dievaluasi secara layak.
