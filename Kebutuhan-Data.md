# Kebutuhan Data JalanTanggap

## Data dari Smart Reporting sampai Intelligent Planning

> **Acuan fase:** [ROADMAP.md](ROADMAP.md). Kebutuhan data dikumpulkan bertahap sesuai roadmap; tidak semua dataset harus tersedia untuk memulai Fase 1.

## 1. Peta Data per Fase

| Fase | Data utama | Digunakan untuk |
|---|---|---|
| 1 | laporan warga, hasil NLP, survey jalan, ruas, fasilitas dasar | BERT/SBERT + SAW |
| 2 | histori keputusan, skor SAW, dipilih/tidak, outcome | AI Prioritization |
| 3 | biaya, durasi, budget, resource, constraint | Multi-Project Optimization |
| 4 | historical traffic, historical roadworks, road graph | Traffic Impact AI |
| 5 | seluruh data + konflik + outcome traffic | Intelligent Planning |

## 2. Fase 1 — Laporan Warga dan NLP

Field minimum laporan:

```text
id_laporan
waktu_laporan
koordinat
id_segmen jika sudah dipetakan
nama_jalan/deskripsi_lokasi
deskripsi
foto
status_verifikasi
```

Simpan hasil NLP secara terstruktur, jangan hanya teks hasil model:

```text
nlp_model
nlp_model_version
kategori_prediksi
confidence_kategori
masalah_terekstrak
dampak_dilaporkan
landmark_terekstrak
embedding_model
embedding_version
cluster_id
similarity_score
candidate_duplicate_of
nlp_processed_at
```

Aturan:
- BERT/IndoBERT digunakan untuk klasifikasi/ekstraksi sesuai hasil benchmark;
- SBERT/sentence embedding digunakan untuk semantic similarity/clustering/deduplikasi kandidat;
- similarity teks dikombinasikan dengan lokasi dan waktu;
- hasil NLP bukan keputusan teknis;
- cluster/duplikasi final diverifikasi petugas;
- identitas warga tidak digunakan sebagai fitur prioritas tanpa kebutuhan operasional yang sah.

## 3. Fase 1 — Survey dan Kondisi Ruas

| Field | Keterangan |
|---|---|
| `id_segmen` | ID konsisten lintas dataset |
| `geometry` | LineString PostGIS |
| `nama_jalan` | nama ruas |
| `kewenangan` | kota/provinsi/nasional/dll |
| `kelas_jalan` | fungsi/kelas resmi |
| `panjang_m` | panjang segmen |
| `lebar_m` | jika tersedia |
| `jumlah_lajur` | jika tersedia |
| `tingkat_kerusakan` | hasil survey/verifikasi |
| `panjang_rusak_m` | panjang terdampak |
| `jenis_kerusakan` | klasifikasi teknis |
| `dampak_akses` | hasil verifikasi |
| `tanggal_survei` | freshness |
| `verified_by` | audit internal |

Nilai teknis berasal dari survei/verifikasi, bukan inferensi NLP.

## 4. Fase 1 — Data SAW

Contoh kriteria:

```text
tingkat_kerusakan
panjang_rusak
dampak_akses
kelas_fungsi_jalan
jumlah_laporan_valid
umur_laporan_tertua
lama_sejak_penanganan
jumlah_fasilitas_kritis
```

Simpan konfigurasi agar audit dapat dilakukan:

```text
saw_version
criterion
weight
attribute_type  # benefit/cost
normalization_method
raw_value
normalized_value
weighted_value
final_score
calculated_at
```

Bobot harus terdokumentasi dan disepakati dengan petugas teknis.

## 5. Riwayat Penanganan dan Outcome

Mulai dikumpulkan sejak Fase 1 karena menjadi fondasi Fase 2.

```text
id_penanganan
id_segmen
tanggal_mulai
tanggal_selesai
jenis_penanganan
estimasi_biaya
biaya_realisasi
kondisi_sebelum
kondisi_sesudah
umur_manfaat_jika_tersedia
```

Simpan juga keputusan per periode:

```text
planning_period
id_segmen
saw_score
expert_priority
decision_selected
selection_reason
override_reason
budget_context
outcome_score jika tersedia
```

## 6. Fase 2 — Dataset AI Prioritization

Training dataset dibentuk dari data historis yang sudah diverifikasi.

Kandidat feature:
- kondisi teknis;
- laporan valid/terdeduplikasi;
- lama laporan;
- fungsi jalan;
- fasilitas penting;
- riwayat penanganan;
- biaya historis;
- konteks akses;
- feature lain yang tersedia sebelum keputusan dibuat.

Kandidat target/label:
- expert priority terverifikasi;
- keputusan paket yang telah dikaji kualitasnya;
- outcome/manfaat setelah penanganan.

Jangan menggunakan skor SAW sebagai satu-satunya target karena model hanya akan belajar meniru formula SAW.

Untuk mencegah leakage, field yang baru diketahui setelah keputusan/pelaksanaan tidak boleh menjadi feature untuk memprediksi keputusan sebelumnya. Split temporal lebih disarankan untuk evaluasi historis.

Simpan metadata model:

```text
model_name
model_version
training_period
feature_schema_version
dataset_version
metrics
prediction
prediction_confidence
explanation
```

## 7. Fase 3 — Data Optimization

Data kandidat:

```text
id_kandidat
id_segmen
ai_priority_score
estimated_cost
estimated_duration
allowed_periods
required_periods
resource_requirement
technical_constraints
```

Parameter skenario:

```text
target_project_count
budget_limit
planning_start
planning_end
max_simultaneous_projects
available_crews
available_equipment
```

Simpan hasil optimizer:

```text
scenario_id
optimizer_version
objective_value
selected
assigned_period
constraint_reason
input_snapshot_version
```

Optimization adalah optimisasi matematis; AI Priority Score menjadi salah satu inputnya.

## 8. Fasilitas dan Aktivitas Sekitar

```text
id_fasilitas
tipe
nama
geometry
jam_aktif
jam_padat
akses_kritis
source
```

Contoh: sekolah, pasar, puskesmas, rumah sakit, terminal, layanan pemerintahan. Data ini dapat digunakan sebagai konteks prioritas dan kemudian konteks traffic impact.

## 9. Fase 4 — Jaringan Jalan / Graph

```text
id_segmen
from_node
to_node
geometry
length_m
oneway
road_class
lanes
width
access
turn_restriction
speed_limit
capacity
```

Graph digunakan untuk graph distance/hop, identifikasi koridor penerima dampak, feature engineering Traffic AI, conflict analysis, dan routing opsional.

Sumber awal dapat menggunakan OSM, tetapi atribut kritis perlu diverifikasi/dilengkapi dari data daerah.

## 10. Fase 4 — Historical Traffic

Format time-series per ruas:

```text
timestamp
id_segmen
direction
speed
free_flow_speed
volume
occupancy
congestion_index
source
quality_flag
```

Interval dapat 5/10/15 menit sesuai sumber dan kebutuhan. Sumber kandidat: ATCS Dishub, traffic counter, CCTV + vehicle counting, survei, provider, atau collector JalanTanggap.

Jangan mencampur sumber tanpa menyimpan `source` dan indikator kualitas.

## 11. Fase 4 — Historical Roadworks / Gangguan

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

Histori event harus dapat dipasangkan dengan traffic sebelum/saat/setelah pekerjaan.

Contoh training sample turunan:

```text
source_project = P001
target_segment = S015
time_window = 07:00-08:00
graph_distance = 3
delta_volume = +420
delta_speed = -12
congestion = 1
```

## 12. Dataset Traffic AI

Feature kandidat per pasangan pekerjaan → target ruas:

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

Model awal dapat mengevaluasi XGBoost/Random Forest. Model final dipilih berdasarkan validasi, bukan nama algoritma.

## 13. Pekerjaan Aktif dan Terjadwal

```text
id_proyek
id_segmen
status
periode_mulai
periode_selesai
jam_pembatasan
jenis_pembatasan
jumlah_lajur_ditutup
estimasi_biaya
progress
```

Data ini penting pada Fase 4–5 untuk traffic context dan konflik antarproyek.

## 14. Fase 5 — Data Integrated Planning

Optimizer akhir dapat menggunakan:

```text
id_kandidat
ai_priority_score
estimated_cost
estimated_duration
traffic_risk
traffic_uncertainty
affected_segments
allowed_periods
conflicting_project_ids
resource_requirement
```

Output:

```text
scenario_id
selected_projects
project_stage
project_schedule
objective_value
budget_used
predicted_traffic_impact
conflicts_avoided
uncertainty
human_decision
human_override_reason
```

## 15. Outcome Setelah Pelaksanaan

Outcome menjadi feedback loop untuk Fase 2 dan Fase 4:

```text
id_proyek
actual_start
actual_end
actual_cost
actual_closure
actual_traffic_per_affected_segment
complaints_during_work
incident_count
condition_after
operator_notes
```

Digunakan untuk evaluasi rekomendasi, evaluasi Traffic AI, retraining, dan pengukuran manfaat nyata.

## 16. Contoh CSV Minimum Fase 1

### laporan.csv

```csv
id_laporan,waktu,id_segmen,deskripsi,status
L001,2026-09-01 08:12,S001,"Lubang besar dan mengganggu kendaraan",Valid
L002,2026-09-02 10:30,S001,"Jalan rusak depan sekolah",Valid
```

### segmen_jalan.csv

```csv
id_segmen,nama_jalan,tingkat_kerusakan,panjang_rusak_m,dampak_akses,jumlah_lajur
S001,Jalan A,5,120,Sulit,2
S002,Jalan B,3,40,Terganggu,2
```

### saw_input.csv

```csv
id_segmen,tingkat_kerusakan,panjang_rusak,jumlah_laporan_valid,dampak_akses
S001,5,120,8,4
S002,3,40,2,2
```

## 17. Urutan Pengumpulan Data Sesuai Roadmap

### Fase 1
1. master ruas dan geometry;
2. laporan warga;
3. output/version NLP dan embedding;
4. hasil deduplikasi + verifikasi;
5. survey kondisi jalan;
6. kriteria/bobot/hasil SAW;
7. keputusan petugas;
8. outcome mulai dicatat.

### Fase 2
9. historical decisions;
10. expert labels;
11. outcome penanganan;
12. versioned ML training dataset.

### Fase 3
13. estimasi biaya/durasi;
14. budget/resource;
15. technical constraints;
16. historical optimizer scenarios.

### Fase 4
17. road graph;
18. historical traffic;
19. historical roadworks/gangguan;
20. traffic outcome per pekerjaan.

### Fase 5
21. pekerjaan aktif/terjadwal;
22. conflict data;
23. integrated scenario/outcome history;
24. realtime/CCTV/cuaca sebagai pengayaan bila tersedia.

## 18. Data Quality dan Governance

Setiap dataset penting sebaiknya memiliki `source`, timestamp pembaruan, status verifikasi, quality/confidence flag, ID ruas konsisten, dan version/audit trail.

Periksa missing value, koordinat salah, ruas ganda, timestamp/timezone, perubahan ID OSM, laporan duplikat, kondisi kedaluwarsa, label bias, dan data leakage.

## 19. Batasan

1. Banyak laporan tidak otomatis berarti ruas paling rusak.
2. Wilayah dengan partisipasi warga rendah tidak boleh otomatis mendapat prioritas rendah.
3. NLP tidak menghasilkan nilai teknis kondisi jalan.
4. Tanpa historical labels/outcome, AI Priority belum layak menggantikan SAW.
5. Tanpa historical traffic + roadworks yang memadai, Traffic AI belum dapat diklaim tervalidasi.
6. Prediksi AI tidak menggantikan keputusan pejabat atau survei teknis.
7. Estimasi biaya/resource harus berasal dari sumber teknis.
8. Data pribadi warga tidak diperlukan sebagai feature model rekomendasi.
