# Kebutuhan Data JalanTanggap

## Rekomendasi Paket Perbaikan + AI Traffic Impact + Optimization

Dokumen ini mendefinisikan data untuk menjawab dua pertanyaan:

1. **Dari seluruh jalan yang membutuhkan penanganan, ruas mana yang sebaiknya masuk paket 10/20 ruas atau paket sesuai anggaran?**
2. **Jika ruas tersebut dikerjakan, apa dampaknya terhadap lalu lintas dan pekerjaan lain?**

---

## 1. Ringkasan Data

| Kategori | Fungsi | Sumber utama |
|---|---|---|
| Laporan warga | aspirasi dan dampak yang dirasakan | form/sistem pengaduan |
| Kondisi ruas | dasar kebutuhan teknis | PUPR/survei/verifikasi |
| Riwayat penanganan | umur penanganan dan outcome | PUPR |
| Biaya & durasi | constraint optimizer | perencanaan teknis |
| Fasilitas/aktivitas | dampak pelayanan | data daerah/OSM/verifikasi |
| Jaringan jalan | relasi spasial dan graph | GIS/OSM |
| Historical traffic | baseline dan training AI | Dishub/ATCS/CCTV/provider |
| Historical roadworks | label efek pekerjaan | PUPR/Dishub |
| Pekerjaan aktif/rencana | konflik multi-proyek | PUPR/pengawas |
| Outcome pelaksanaan | evaluasi dan retraining | sistem + lapangan |

---

## 2. Laporan Warga

```text
id_laporan
waktu_laporan
koordinat
id_segmen
nama_jalan
deskripsi
foto
dampak_dilaporkan
status_verifikasi
id_cluster_duplikat
hasil_ekstraksi_llm
hasil_verifikasi
```

Aturan:
- laporan harus dihubungkan ke ruas setelah verifikasi;
- laporan duplikat tidak dihitung sebagai kejadian kerusakan berbeda;
- jumlah laporan menjadi salah satu sinyal, bukan penentu tunggal;
- identitas warga tidak digunakan sebagai fitur prioritas kecuali kebutuhan operasional yang sah dan terpisah.

LLM dapat membantu ekstraksi lokasi/keluhan dan mendeteksi kandidat duplikasi, tetapi hasilnya diverifikasi.

---

## 3. Kondisi Ruas

| Field | Contoh/keterangan |
|---|---|
| `id_segmen` | ID konsisten lintas dataset |
| `geometry` | LineString PostGIS |
| `nama_jalan` | nama ruas |
| `kewenangan` | kota/provinsi/nasional/dll |
| `kelas_jalan` | fungsi/kelas resmi |
| `panjang_m` | panjang segmen |
| `lebar_m` | jika tersedia |
| `jumlah_lajur` | jika tersedia |
| `tingkat_kerusakan` | hasil survei/verifikasi |
| `panjang_rusak_m` | panjang terdampak |
| `jenis_kerusakan` | lubang/retak/dll sesuai data teknis |
| `dampak_akses` | normal/terganggu/sulit/terputus |
| `tanggal_survei` | freshness data |
| `verified_by` | audit internal |

Nilai kondisi teknis harus berasal dari sumber/verifikasi teknis, bukan inferensi LLM.

---

## 4. Riwayat Penanganan

```text
id_penanganan
id_segmen
tanggal_mulai
tanggal_selesai
jenis_penanganan
biaya_realisasi
kondisi_sebelum
kondisi_sesudah
umur_manfaat_jika_tersedia
```

Dipakai untuk melihat lama belum ditangani, frekuensi kerusakan berulang, biaya historis, dan outcome.

---

## 5. Data Biaya dan Durasi Kandidat

Diperlukan agar mode `berdasarkan anggaran` benar-benar dapat dioptimalkan.

```text
id_kandidat
id_segmen
jenis_penanganan_usulan
estimasi_biaya
estimasi_durasi_hari
jumlah_lajur_terdampak
jenis_pembatasan
opsi_waktu_mulai
batasan_teknis
```

Tanpa estimasi biaya, sistem hanya dapat mengoptimalkan berdasarkan jumlah ruas atau constraint lain.

---

## 6. Fasilitas dan Aktivitas Sekitar

```text
id_fasilitas
tipe
nama
geometry
jam_aktif
jam_padat
akses_kritis
```

Contoh: sekolah, pasar, puskesmas, rumah sakit, terminal, layanan pemerintahan, kawasan aktivitas tinggi.

Digunakan sebagai konteks manfaat dan dampak. Keberadaan fasilitas tidak otomatis menentukan prioritas; bobot/aturan harus terdokumentasi.

---

## 7. Jaringan Jalan / Graph

Data minimum:

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
speed_limit jika tersedia
capacity jika tersedia
```

Sumber awal dapat menggunakan OSM, kemudian atribut penting diverifikasi/dilengkapi dari data daerah.

Graph dipakai untuk:
- hubungan antar-ruas;
- jarak/hop dari lokasi pekerjaan;
- identifikasi koridor penerima dampak;
- feature engineering traffic AI;
- jalur alternatif opsional.

---

## 8. Historical Traffic

Ini data utama untuk **AI Traffic Impact Prediction**.

### Format time-series per ruas

```text
timestamp
id_segmen
direction
speed
free_flow_speed
volume
occupancy jika tersedia
congestion_index
source
quality_flag
```

Idealnya interval konsisten, misalnya 5/10/15 menit sesuai sumber.

Sumber kandidat:
- ATCS Dishub;
- traffic counter;
- CCTV + vehicle counting;
- survei lalu lintas;
- traffic provider jika tersedia;
- collector berkala JalanTanggap.

Jangan mencampur sumber tanpa menyimpan `source` dan indikator kualitas.

---

## 9. Historical Roadworks / Gangguan

Agar model dapat belajar efek pekerjaan, histori traffic harus dapat dipasangkan dengan histori gangguan.

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
segmen_pengalihan jika diketahui
```

Training sample kemudian dapat membandingkan baseline dengan kondisi saat event.

Contoh label turunan:

```text
source_project = P001
target_segment = S015
time_window = 07:00-08:00
delta_volume = +420 veh/hour
delta_speed = -12 km/hour
congestion = 1
```

---

## 10. Pekerjaan Aktif dan Terjadwal

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

Digunakan untuk mendeteksi konflik dengan paket baru.

---

## 11. Dataset Priority / Need Scoring

### Baseline MVP

Fitur dapat mencakup:

```text
tingkat_kerusakan
panjang_rusak
dampak_akses
kelas_jalan
jumlah_laporan_valid
umur_laporan_tertua
lama_sejak_penanganan
jumlah_fasilitas_kritis
estimasi_biaya
```

Pada MVP, gunakan aturan/SAW yang disepakati petugas dan simpan komponen skor agar dapat diaudit.

### Jika menggunakan ML

Diperlukan target/label yang jelas. Contoh yang mungkin setelah data tersedia:
- prioritas ahli terverifikasi;
- outcome/manfaat setelah penanganan;
- keputusan paket historis yang telah dikaji kualitasnya.

Tidak disarankan mengklaim priority scoring sebagai AI jika hanya menggunakan bobot manual.

---

## 12. Dataset Traffic AI

### Feature per pasangan pekerjaan → target ruas

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

### Target

```text
delta_volume
delta_speed
congestion_probability
risk_class
```

Untuk MVP, XGBoost/Random Forest dapat diuji. Pemilihan model final berdasarkan hasil validasi, bukan nama algoritma.

---

## 13. Data untuk Optimizer

Optimizer membutuhkan hasil dari mesin sebelumnya ditambah constraint perencanaan:

```text
id_kandidat
need_score
estimated_cost
estimated_duration
traffic_risk
uncertainty
allowed_periods
required_periods
conflicting_project_ids
resource_requirement
```

Parameter skenario:

```text
target_project_count = 10 / 20 / null
budget_limit
planning_start
planning_end
max_simultaneous_projects
max_acceptable_traffic_risk
```

Output optimizer harus menyimpan objective score dan alasan constraint yang membuat kandidat tidak masuk/berpindah tahap.

---

## 14. Outcome Setelah Pelaksanaan

Bagian ini penting agar sistem dapat belajar.

```text
id_proyek
actual_start
actual_end
actual_cost
actual_closure
actual_traffic_per_affected_segment
complaints_during_work
incident_count jika tersedia
condition_after
operator_notes
```

Outcome dipakai untuk:
- menguji prediksi;
- memperbaiki dataset;
- retraining;
- mengetahui apakah rekomendasi paket benar-benar memberikan hasil baik.

---

## 15. Contoh CSV Minimum

### `laporan.csv`

```csv
id_laporan,waktu,id_segmen,deskripsi,status
L001,2026-09-01 08:12,S001,"Lubang besar dan mengganggu kendaraan",Valid
L002,2026-09-02 10:30,S001,"Jalan rusak depan sekolah",Valid
```

### `segmen_jalan.csv`

```csv
id_segmen,nama_jalan,tingkat_kerusakan,panjang_rusak_m,dampak_akses,jumlah_lajur
S001,Jalan A,5,120,Sulit,2
S002,Jalan B,3,40,Terganggu,2
```

### `traffic_history.csv`

```csv
timestamp,id_segmen,speed,free_flow_speed,volume,congestion_index,source
2026-09-10 07:00,S001,18,40,1250,0.72,DISHUB
2026-09-10 07:05,S001,16,40,1320,0.78,DISHUB
```

### `kandidat_pekerjaan.csv`

```csv
id_kandidat,id_segmen,estimasi_biaya,estimasi_durasi_hari,jumlah_lajur_terdampak
K001,S001,500000000,14,1
K002,S002,300000000,7,1
```

---

## 16. Urutan Pengumpulan Data

### Wajib untuk Recommendation MVP
1. ruas dan kondisi jalan;
2. laporan warga terverifikasi;
3. kandidat pekerjaan;
4. estimasi biaya/durasi;
5. jaringan jalan;
6. pekerjaan aktif.

### Wajib untuk Traffic AI yang layak
7. historical traffic per ruas;
8. historical roadworks/gangguan;
9. pasangan baseline vs kondisi saat gangguan;
10. validasi outcome.

### Pengayaan
11. fasilitas/aktivitas;
12. cuaca;
13. CCTV vehicle counting;
14. data realtime.

---

## 17. Data Quality

Setiap dataset sebaiknya memiliki:
- `source`;
- waktu pembaruan;
- status verifikasi;
- quality/confidence flag;
- ID ruas yang konsisten;
- version/audit trail untuk perubahan penting.

Masalah utama yang perlu diperiksa: missing value, koordinat salah, ruas ganda, timestamp/timezone tidak konsisten, data traffic kosong, perubahan ID OSM, laporan duplikat, dan data kondisi yang sudah kedaluwarsa.

---

## 18. Batasan

1. Banyak laporan tidak otomatis berarti ruas paling rusak.
2. Wilayah dengan partisipasi warga rendah tidak boleh otomatis mendapat skor rendah.
3. Tanpa historical traffic + event pekerjaan yang memadai, dampak kemacetan hanya dapat dinilai sebagai baseline/risk scoring.
4. Prediksi AI tidak menggantikan survei teknis atau keputusan pejabat.
5. Estimasi biaya dan kapasitas harus berasal dari sumber teknis.
6. Contoh data dalam dokumentasi adalah ilustrasi.
7. Data pribadi warga tidak diperlukan untuk training model rekomendasi.
