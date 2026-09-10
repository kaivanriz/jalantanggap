# AI Traffic Impact Prediction

## Subdokumen Fase 4 JalanTanggap

> Dokumen ini adalah rancangan teknis **Fase 4 — AI Traffic Impact Prediction** pada [ROADMAP.md](ROADMAP.md). Dokumen ini bukan roadmap terpisah dan tidak mengubah urutan fase utama JalanTanggap.

Sebelum mencapai fase ini, JalanTanggap direncanakan telah melewati:

```text
Fase 1: BERT/SBERT + Survey + SAW
Fase 2: AI Prioritization
Fase 3: AI-Assisted Multi-Project Optimization
        ↓
Fase 4: AI Traffic Impact Prediction  ← dokumen ini
        ↓
Fase 5: Intelligent Road Maintenance Planning
```

## 1. Tujuan

Traffic Impact AI membantu menjawab:

> Jika satu atau beberapa ruas direncanakan untuk diperbaiki, ruas/kawasan mana yang berpotensi mengalami perubahan volume, penurunan kecepatan, atau peningkatan risiko kemacetan?

Fokus utamanya adalah **dampak rencana pekerjaan terhadap jaringan**, bukan sekadar pencarian jalur alternatif.

## 2. Hubungan dengan Fase Sebelumnya

Fase 4 tidak menentukan dari awal jalan mana yang prioritas.

```text
AI Priority Model (Fase 2)
        ↓
Priority Score
        ↓
Optimizer awal (Fase 3)
        ↓
Kandidat/Paket Pekerjaan
        ↓
Traffic Impact AI (Fase 4)
        ↓
Prediksi Dampak per Proyek/Paket
```

Pada Fase 5, prediksi ini dimasukkan kembali ke optimizer sehingga sistem dapat menyusun paket dan jadwal dengan mempertimbangkan dampak traffic.

## 3. Data yang Dibutuhkan

Data minimum yang diharapkan:
- historical traffic per ruas;
- historical roadworks/gangguan;
- volume kendaraan;
- speed dan free-flow speed;
- congestion index;
- kapasitas/jumlah lajur;
- karakteristik dan waktu pekerjaan;
- jumlah lajur yang ditutup;
- jaringan jalan/graph;
- pekerjaan lain yang aktif;
- aktivitas fasilitas/event dan cuaca bila tersedia.

Tanpa pasangan historical traffic + event pekerjaan yang cukup, sistem belum memiliki bukti untuk mengklaim model sebagai prediksi AI yang tervalidasi.

## 4. Historical Traffic

Skema time-series minimum:

```text
timestamp
id_segmen
direction
speed
free_flow_speed
volume
congestion_index
source
quality_flag
```

Interval dapat 5/10/15 menit sesuai sumber. Sumber kandidat mencakup ATCS Dishub, traffic counter, CCTV + vehicle counting, survei, provider, atau collector JalanTanggap.

## 5. Historical Roadworks

```text
id_event
id_segmen_pekerjaan
waktu_mulai
waktu_selesai
jenis_pekerjaan
jenis_pembatasan
jumlah_lajur_ditutup
arah_terdampak
severity
```

Traffic sebelum/saat/setelah event dipasangkan untuk membentuk label seperti:

```text
source_project = P001
target_segment = S015
time_window = 07:00-08:00
delta_volume = +420
delta_speed = -12
congestion = 1
```

## 6. Road Graph dan Propagasi Dampak

Jaringan jalan direpresentasikan sebagai graph untuk menghasilkan fitur seperti:
- graph distance;
- hop count;
- konektivitas;
- simpang terkait;
- kapasitas koridor penerima;
- overlap area dampak beberapa pekerjaan.

Graph analysis sendiri tidak harus AI. Ia menjadi feature engineering dan alat analisis penyebaran dampak.

## 7. Model MVP

Kandidat awal: **XGBoost atau Random Forest** pada fitur tabular + spasial/graph.

Contoh feature:

```text
project_segment
candidate_affected_segment
graph_distance
hop_count
baseline_volume
baseline_speed
free_flow_speed
capacity
lanes
lanes_closed
closure_type
hour
day_of_week
duration
nearby_active_projects
facility_activity
weather_optional
```

Target:

```text
delta_volume
delta_speed
congestion_probability
risk_class
```

Pemilihan model final harus berdasarkan hasil validasi.

## 8. Contoh Prediksi

```text
Pekerjaan: Jalan A
Waktu: Senin 07.00–16.00
Penutupan: 1 dari 2 lajur

Prediksi:
Jalan B      +52% volume    risiko 0.87
Simpang C    +46% volume    risiko 0.82
Jalan D      +21% volume    risiko 0.61
Jalan E       +6% volume    risiko 0.24
```

Output dashboard dapat menampilkan:

```text
🔴 Simpang C    risiko tinggi
🔴 Jalan B      risiko tinggi
🟡 Jalan D      risiko sedang
🟢 Jalan E      risiko rendah
```

Angka di dokumentasi hanyalah ilustrasi.

## 9. Baseline Sebelum Model AI Matang

Jika histori belum cukup, gunakan risk scoring berbasis:
- graph distance/hop;
- kapasitas ruas;
- baseline traffic;
- jumlah lajur;
- jenis penutupan;
- overlap pekerjaan;
- jam sibuk;
- aktivitas sekitar.

Output harus diberi label **baseline/risk scoring**, bukan prediksi AI.

Baseline berguna sebagai pembanding setelah model ML tersedia.

## 10. Analisis Banyak Proyek

Setelah prediksi dampak individual tersedia, sistem dapat membentuk overlap/conflict information.

Contoh:

| | A | B | C | D |
|---|---:|---:|---:|---:|
| A | - | Rendah | Rendah | Tinggi |
| B | Rendah | - | Sedang | Rendah |
| C | Rendah | Sedang | - | Sedang |
| D | Tinggi | Rendah | Sedang | - |

Matriks tersebut menjadi input penting **Fase 5**, bukan keputusan jadwal final Fase 4.

Output Fase 4:
- dampak tiap pekerjaan;
- affected roads/areas;
- heatmap;
- overlap area dampak;
- conflict score/matrix;
- confidence/uncertainty;
- faktor utama prediksi.

## 11. Evaluasi

Untuk target numerik:
- MAE;
- RMSE;
- MAPE jika sesuai.

Untuk klasifikasi risiko:
- precision;
- recall;
- F1-score;
- confusion matrix;
- probability calibration bila menghasilkan probabilitas.

Evaluasi spasial:
- apakah ruas yang diprediksi terdampak benar-benar terdampak;
- ketepatan ranking area kritis;
- seberapa jauh propagasi dampak diprediksi dengan benar.

Split data perlu memperhatikan waktu/proyek agar data dari event yang sama tidak bocor antara training dan test.

## 12. Model Lanjutan

Jika tersedia sensor/CCTV yang padat, histori panjang, dan graph yang stabil, dapat dievaluasi **Spatio-Temporal Graph Neural Network** seperti keluarga DCRNN/Graph WaveNet atau arsitektur setara.

ST-GNN bukan kebutuhan MVP dan hanya digunakan bila performanya terbukti lebih baik serta biaya operasionalnya masuk akal.

## 13. Integrasi ke Fase 5

```text
AI Priority
     +
Cost / Duration / Budget
     +
Traffic Impact Prediction
     +
Conflict Matrix
     +
Resource Constraints
     ↓
MULTI-PROJECT OPTIMIZER
     ↓
Paket Perbaikan
     ↓
Tahapan + Jadwal + Heatmap + Alasan
```

Fase 5 dapat memberikan penalti pada kombinasi yang menghasilkan risiko traffic tinggi tanpa otomatis membuang ruas yang memiliki kebutuhan sangat mendesak.

## 14. Pembagian Komponen

| Komponen | Fungsi | Kategori |
|---|---|---|
| AI Priority | menentukan priority/benefit kandidat | AI/ML — Fase 2 |
| XGBoost/RF Traffic | prediksi dampak traffic | AI/ML — Fase 4 |
| Graph analysis | konektivitas/propagasi | algoritmik |
| Conflict matrix | overlap dampak | analitik |
| OR-Tools/MILP/CP-SAT | paket dan jadwal | mathematical optimization |
| Dijkstra/A* | routing alternatif opsional | algoritmik |
| PostGIS | data spasial | database |
| Leaflet | heatmap/WebGIS | visualisasi |

## 15. Definition of Done Fase 4

Fase 4 dianggap selesai ketika:
1. historical traffic dan roadworks dapat dipasangkan dengan ID ruas konsisten;
2. baseline traffic impact tersedia;
3. model ML dilatih dengan split yang mencegah leakage;
4. model dibandingkan dengan baseline;
5. prediksi `delta_volume`/`delta_speed` atau congestion risk tervalidasi;
6. affected roads dapat divisualisasikan di WebGIS;
7. uncertainty/confidence tersedia atau keterbatasannya dinyatakan;
8. hasil dapat digunakan sebagai input Fase 5;
9. evaluasi terhadap pekerjaan nyata mulai direkam untuk retraining.

## Prinsip Penting

Traffic Impact AI tidak mengetahui kemacetan tanpa data. Klaim prediksi harus didukung historical traffic, karakteristik pekerjaan, jaringan jalan, dan observasi outcome. Bila data belum memadai, gunakan baseline yang jujur dan tampilkan ketidakpastian.
