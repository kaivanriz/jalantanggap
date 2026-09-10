# AI Traffic Impact Prediction

## Fokus baru JalanTanggap

JalanTanggap diarahkan untuk membantu petugas menjawab pertanyaan utama berikut:

> Jika terdapat beberapa rencana perbaikan jalan, ruas atau kawasan mana yang berpotensi mengalami peningkatan kepadatan, pekerjaan mana yang aman dilaksanakan bersamaan, dan pekerjaan mana yang sebaiknya dipisahkan waktunya?

Pencarian jalur alternatif tetap tersedia, tetapi menjadi fitur pendukung. Fokus utama sistem adalah **prediksi dampak kemacetan akibat rencana pekerjaan jalan**.

---

## 1. Skenario utama

Contoh terdapat 10 rencana perbaikan jalan:

1. Jalan A
2. Jalan B
3. Jalan C
4. Jalan D
5. Jalan E
6. Jalan F
7. Jalan G
8. Jalan H
9. Jalan I
10. Jalan J

Sistem menganalisis masing-masing pekerjaan dan kombinasi pekerjaan yang waktunya beririsan.

Contoh keluaran:

| Rencana pekerjaan | Ruas/kawasan terdampak | Prediksi perubahan | Risiko |
|---|---|---:|---|
| Jalan A | Jalan K, Simpang X | +45% s.d. +60% | Tinggi |
| Jalan B | Jalan L | +15% s.d. +25% | Sedang |
| Jalan C | Jalan M | <10% | Rendah |
| Jalan D | Jalan K, Simpang X | +35% s.d. +50% | Tinggi |

Sistem juga menilai interaksi antarpekerjaan. Contoh:

- Jalan A sendiri: dampak sedang.
- Jalan D sendiri: dampak sedang.
- Jalan A dan Jalan D dikerjakan bersamaan: dampak tinggi karena arus pengalihan bertemu pada ruas yang sama.

Dengan demikian rekomendasi sistem dapat berupa:

> Jalan C, E, F, dan H relatif aman dijadwalkan pada periode yang sama. Jalan A dan D sebaiknya tidak dilaksanakan bersamaan karena berpotensi meningkatkan beban pada Simpang X dan Jalan K.

Keputusan akhir tetap berada pada petugas/pejabat terkait.

---

## 2. Posisi AI dalam sistem

SAW bukan metode AI. SAW masih dapat dipakai secara opsional untuk penilaian administratif atau prioritas kebutuhan perbaikan, tetapi komponen AI utama ditempatkan pada **Traffic Impact Prediction**.

Alur utama:

```text
Rencana pekerjaan jalan
        +
Data historis lalu lintas
        +
Karakteristik ruas dan jaringan jalan
        +
Waktu, penutupan lajur, pekerjaan aktif, aktivitas sekitar
        ↓
Feature engineering spasial-temporal
        ↓
Model AI / Machine Learning
        ↓
Prediksi perubahan volume / kecepatan / risiko kemacetan per ruas
        ↓
Analisis penyebaran dampak pada graf jalan
        ↓
Peta zona dampak + ranking area paling kritis
        ↓
Analisis kombinasi 10+ rencana pekerjaan
        ↓
Rekomendasi jadwal dan konflik pekerjaan
```

---

## 3. Model AI yang direkomendasikan

### Tahap MVP: XGBoost atau Random Forest

Model tabular lebih realistis untuk prototipe karena dapat bekerja dengan jumlah data yang lebih terbatas dan lebih mudah dijelaskan.

Contoh fitur input:

- `id_segmen`
- hari dalam minggu
- jam
- volume lalu lintas normal
- kecepatan normal
- kecepatan aktual/historis
- rasio volume terhadap kapasitas
- jumlah lajur
- jumlah lajur yang ditutup
- jenis penutupan: total / sebagian / buka-tutup
- durasi pekerjaan
- kelas/fungsi jalan
- lebar jalan
- jarak dari lokasi pekerjaan
- hop/jumlah ruas pada graf dari lokasi pekerjaan
- jumlah simpang terdekat
- pekerjaan lain yang aktif di sekitar
- sekolah/pasar/fasilitas lain yang sedang aktif
- cuaca jika tersedia

Target model dapat berupa salah satu atau beberapa nilai berikut:

- perubahan volume kendaraan (`delta_volume`)
- perubahan kecepatan rata-rata (`delta_speed`)
- probabilitas kemacetan (`congestion_probability`)
- kelas risiko: rendah / sedang / tinggi

Contoh:

```text
Pekerjaan: Jalan A, 1 lajur ditutup, Senin 07.00–16.00

Prediksi:
Jalan B      +52% volume     risiko 0.87
Simpang C    +46% volume     risiko 0.82
Jalan D      +21% volume     risiko 0.61
Jalan E       +6% volume     risiko 0.24
```

### Tahap lanjutan: Spatio-Temporal Graph Neural Network

Jika kelak tersedia data sensor/CCTV yang padat dan historis panjang, jaringan jalan dapat direpresentasikan sebagai graph. Model spatio-temporal graph dapat mempelajari bagaimana gangguan di satu ruas merambat ke ruas lain dari waktu ke waktu.

Model ini bukan kebutuhan MVP.

---

## 4. Data historis kemacetan

Data historis sebaiknya disimpan dalam bentuk time-series per ruas jalan, bukan hanya label `macet/tidak macet`.

Skema minimum:

```text
timestamp
id_segmen
speed
free_flow_speed
volume
jam_factor / congestion_index
source
```

Contoh:

```csv
timestamp,id_segmen,speed,free_flow_speed,volume,congestion_index,source
2026-09-10 07:00,S001,18,40,1250,0.72,DISHUB
2026-09-10 07:05,S001,16,40,1320,0.78,DISHUB
```

Sumber data yang dapat digabungkan:

1. Data Dishub: ATCS, traffic counter, CCTV, survei volume lalu lintas.
2. Traffic provider bila tersedia.
3. CCTV yang diproses computer vision untuk menghitung kendaraan.
4. Data yang dikumpulkan sistem sendiri secara berkala untuk membangun histori.

Data pekerjaan jalan historis juga sangat penting:

```text
id_proyek
id_segmen_pekerjaan
waktu_mulai
waktu_selesai
jenis_penutupan
jumlah_lajur_ditutup
segmen_terdampak
volume_sebelum
volume_saat_pekerjaan
speed_sebelum
speed_saat_pekerjaan
```

Dari data tersebut model dapat belajar pola seperti:

```text
Perbaikan Jalan A
       ↓
Jalan B +68% volume
Jalan C +53% volume
Jalan D  +4% volume
```

---

## 5. Baseline sebelum AI matang

Jika data historis belum cukup untuk melatih model dengan baik, sistem tetap dapat memiliki baseline berbasis aturan dan graph analysis:

- jarak/hop dari lokasi pekerjaan
- kapasitas ruas penerima
- lebar dan jumlah lajur
- volume lalu lintas normal
- overlap pekerjaan
- overlap jalur pengalihan
- jam sibuk
- aktivitas sekolah/pasar

Baseline ini harus diberi label jelas sebagai **risk scoring**, bukan prediksi AI.

Setelah data historis terkumpul, hasil baseline dapat dibandingkan dengan model ML.

---

## 6. Analisis 10+ rencana pekerjaan

Untuk setiap rencana pekerjaan, sistem membuat skenario gangguan jaringan. Selanjutnya sistem mengevaluasi kombinasi pekerjaan yang waktunya beririsan.

Output yang dibutuhkan:

- prediksi dampak tiap pekerjaan
- ruas/kawasan paling terdampak
- pekerjaan yang memiliki wilayah dampak saling tumpang tindih
- pekerjaan yang aman dilaksanakan bersamaan
- pekerjaan yang sebaiknya dipisahkan waktunya
- skenario jadwal alternatif
- confidence/tingkat keyakinan model
- alasan faktor utama yang memengaruhi prediksi

Contoh matriks konflik:

| | A | B | C | D |
|---|---:|---:|---:|---:|
| A | - | Rendah | Rendah | Tinggi |
| B | Rendah | - | Sedang | Rendah |
| C | Rendah | Sedang | - | Sedang |
| D | Tinggi | Rendah | Sedang | - |

Matriks ini dapat dipakai oleh petugas untuk menyusun jadwal pekerjaan.

---

## 7. Visualisasi utama

Dashboard sebaiknya menampilkan:

- titik/ruas rencana perbaikan
- heatmap prediksi dampak
- ruas merah: risiko tinggi
- ruas kuning: risiko sedang
- ruas hijau: risiko rendah
- timeline seluruh pekerjaan
- konflik antarpekerjaan
- perbandingan skenario jadwal
- detail faktor penyebab prediksi

Contoh informasi yang ditampilkan saat sebuah pekerjaan dipilih:

```text
Rencana: Perbaikan Jalan A
Waktu: Senin 07.00–16.00
Penutupan: 1 dari 2 lajur

Area terdampak:
🔴 Simpang X       risiko 92%
🔴 Jalan B         risiko 87%
🟡 Jalan D         risiko 64%
🟢 Jalan E         risiko 18%

Konflik:
⚠ Perbaikan Jalan D memiliki area dampak yang sama.

Rekomendasi:
Pisahkan jadwal Jalan A dan Jalan D atau pilih waktu di luar jam sibuk.
```

---

## 8. Evaluasi model

Untuk target numerik seperti volume atau kecepatan:

- MAE
- RMSE
- MAPE jika sesuai

Untuk target kelas risiko:

- precision
- recall
- F1-score
- confusion matrix

Evaluasi juga perlu dilakukan secara spasial:

- apakah ruas yang diprediksi terdampak benar-benar terdampak
- seberapa jauh penyebaran dampak yang berhasil diprediksi
- apakah ranking area kritis sesuai observasi lapangan

---

## 9. Pembagian fungsi komponen

| Komponen | Fungsi |
|---|---|
| LLM | Ekstraksi laporan warga, klarifikasi, penjelasan hasil |
| XGBoost / Random Forest | Prediksi dampak lalu lintas pada MVP |
| Graph analysis | Memahami konektivitas dan penyebaran dampak antar-ruas |
| Dijkstra / A* | Jalur alternatif, jika diperlukan |
| SAW | Opsional untuk prioritas administratif, bukan komponen AI |
| PostGIS | Penyimpanan dan query data spasial |
| Leaflet | Visualisasi peta dan heatmap |

---

## 10. Tahapan implementasi yang disarankan

### Fase 1 — baseline
- inventarisasi ruas jalan
- masukkan rencana dan pekerjaan aktif
- simpan histori traffic per ruas
- bangun risk scoring berbasis aturan
- tampilkan heatmap konflik

### Fase 2 — AI MVP
- siapkan dataset training
- feature engineering
- latih XGBoost / Random Forest
- prediksi dampak tiap rencana pekerjaan
- ranking ruas/kawasan terdampak
- validasi dengan data lapangan

### Fase 3 — multi-project analysis
- evaluasi 10+ pekerjaan sekaligus
- matriks konflik antarpekerjaan
- rekomendasi pekerjaan yang dapat berjalan bersamaan
- optimasi jadwal

### Fase 4 — pengembangan lanjutan
- integrasi CCTV/ATCS realtime
- computer vision untuk counting kendaraan
- spatio-temporal graph model
- jalur alternatif adaptif

---

## Prinsip penting

JalanTanggap tidak menjanjikan bahwa AI dapat mengetahui kemacetan tanpa data. Model hanya boleh menggunakan data lalu lintas, jaringan jalan, karakteristik pekerjaan, dan observasi historis yang tersedia. Bila data historis belum memadai, sistem harus menampilkan hasil sebagai indikator risiko/baseline dan menyertakan tingkat ketidakpastian.
