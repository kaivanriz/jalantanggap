# Rencana Proyek JalanTanggap

## Sistem Rekomendasi Paket Perbaikan Jalan Berbasis Data, AI Traffic Impact, dan Optimization

---

## 1. Ringkasan

JalanTanggap membantu pemerintah memilih **10, 20, atau sejumlah ruas sesuai anggaran** dari seluruh kandidat jalan yang membutuhkan penanganan. Pemilihan tidak hanya mempertimbangkan kondisi fisik dan aspirasi warga, tetapi juga dampak pelaksanaan terhadap lalu lintas dan konflik antarpekerjaan.

Pertanyaan utama:

> Dari seluruh ruas yang rusak, ruas mana yang paling layak masuk paket perbaikan, dan bagaimana mengatur pelaksanaannya agar manfaat pelayanan tinggi tanpa menciptakan masalah lalu lintas baru?

### Keluaran utama

1. skor kebutuhan/prioritas setiap ruas;
2. rekomendasi paket Top 10 / Top 20 / berdasarkan anggaran;
3. alasan ruas dipilih atau belum dipilih;
4. prediksi dampak pekerjaan ke ruas/kawasan sekitar;
5. heatmap risiko lalu lintas;
6. matriks konflik antarpekerjaan;
7. rekomendasi pekerjaan yang dapat berjalan bersamaan atau perlu dipisahkan;
8. skenario tahapan/jadwal;
9. jalur alternatif sebagai fitur pendukung.

---

## 2. Masalah yang Diselesaikan

- Banyak ruas membutuhkan penanganan sementara anggaran dan kapasitas pekerjaan terbatas.
- Aspirasi warga penting, tetapi jumlah laporan tidak selalu identik dengan tingkat kerusakan.
- Penentuan paket pekerjaan perlu menggabungkan kondisi teknis, dampak pelayanan, biaya, dan kebutuhan masyarakat.
- Dua ruas yang sama-sama prioritas belum tentu aman dikerjakan pada waktu yang sama.
- Gangguan pada satu ruas dapat memindahkan beban kendaraan ke ruas lain.
- Data perencanaan, laporan warga, jaringan jalan, dan lalu lintas perlu dianalisis dalam satu konteks spasial.

---

## 3. Tujuan

1. Mengumpulkan dan menormalisasi laporan warga tentang kerusakan jalan.
2. Menghubungkan laporan dengan ruas jalan dan hasil verifikasi lapangan.
3. Menilai kebutuhan penanganan secara transparan.
4. Membentuk kandidat paket perbaikan berdasarkan target jumlah atau anggaran.
5. Menggunakan AI/ML untuk memprediksi dampak lalu lintas dari kandidat pekerjaan jika data historis memadai.
6. Mengoptimalkan kombinasi dan tahapan pekerjaan dengan mempertimbangkan constraint anggaran, waktu, dan konflik lalu lintas.
7. Menyediakan alasan rekomendasi yang dapat ditinjau petugas.

---

## 4. Arsitektur Keputusan

```text
Laporan warga ──┐
Kondisi jalan ──┼──> Validasi & Feature Store
Data fasilitas ─┘             │
                              ↓
                    Priority / Need Scoring
                              │
                              ↓
                     Kandidat perbaikan
                              │
          ┌───────────────────┴───────────────────┐
          ↓                                       ↓
Historical Traffic                      Jaringan Jalan/Graph
          └───────────────────┬───────────────────┘
                              ↓
                   AI Traffic Impact Model
                              ↓
                  Dampak per kandidat proyek
                              ↓
                  Multi-Project Optimizer
                              ↓
             Paket 10/20/sesuai anggaran
                              ↓
          Tahapan + Heatmap + Konflik + Alasan
```

---

## 5. Mesin 1 — Priority / Need Scoring

### 5.1 Tujuan
Menentukan seberapa mendesak/manfaatnya sebuah ruas untuk ditangani.

### 5.2 Fitur awal
- tingkat kerusakan;
- panjang/luas kerusakan;
- dampak akses;
- kelas/fungsi jalan;
- kewenangan;
- jumlah laporan warga **valid dan terdeduplikasi**;
- umur laporan/lama belum ditangani;
- riwayat penanganan;
- akses sekolah, pasar, faskes, layanan publik;
- hasil verifikasi petugas;
- estimasi biaya dan durasi.

### 5.3 Metode
Untuk MVP, gunakan **SAW/rule-based scoring** sebagai baseline yang transparan. SAW bukan AI.

ML untuk priority prediction baru digunakan jika tersedia label historis yang layak, misalnya keputusan prioritas sebelumnya dan outcome setelah penanganan. Model tidak boleh dilatih hanya untuk meniru keputusan lama tanpa evaluasi bias dan kualitas label.

---

## 6. Mesin 2 — AI Traffic Impact Prediction

### 6.1 Pertanyaan
Jika kandidat Jalan A dikerjakan pada waktu tertentu, **ruas mana yang berpotensi terdampak dan seberapa besar risikonya?**

### 6.2 MVP
Gunakan XGBoost atau Random Forest pada fitur tabular/spasial-temporal.

Contoh fitur:
- baseline volume dan speed;
- free-flow speed;
- congestion index;
- jam/hari;
- kelas, lebar, kapasitas, jumlah lajur;
- jumlah lajur ditutup;
- jenis dan durasi pembatasan;
- jarak/hop graph dari pekerjaan;
- konektivitas dan simpang;
- pekerjaan lain;
- aktivitas fasilitas;
- cuaca bila tersedia.

Target dapat berupa:
- `delta_volume`;
- `delta_speed`;
- `congestion_probability`;
- kelas risiko.

Jika data historis belum cukup, gunakan baseline risk scoring dan jangan menyebutnya prediksi AI.

### 6.3 Pengembangan
Jika tersedia data sensor/CCTV padat dan histori panjang, evaluasi Spatio-Temporal Graph Neural Network.

---

## 7. Mesin 3 — Multi-Project Optimization

Optimizer memilih **kombinasi**, bukan hanya mengambil N ranking tertinggi.

### Mode
- pilih 10 ruas;
- pilih 20 ruas;
- pilih sebanyak mungkin dalam batas anggaran;
- pilih untuk periode tertentu.

### Objective konseptual

```text
maximize:
  total_manfaat_prioritas
  - penalti_risiko_lalu_lintas
  - penalti_konflik_proyek
  - penalti_ketidakpastian
```

### Constraint contoh
- jumlah proyek maksimal N;
- total biaya tidak melebihi anggaran;
- batas kapasitas pekerjaan per periode;
- proyek tertentu tidak boleh overlap;
- akses fasilitas penting harus dipertahankan;
- pekerjaan dengan dampak koridor sama dipisahkan bila melewati threshold.

Teknologi kandidat: OR-Tools, Pyomo, atau solver optimisasi setara.

---

## 8. Alur Pengguna

1. Warga mengirim laporan, lokasi, deskripsi, dan foto.
2. LLM mengekstrak informasi dan membantu klarifikasi/duplikasi.
3. Petugas memverifikasi kondisi dan menghubungkan laporan ke ruas.
4. Sistem menghitung need score seluruh kandidat.
5. Petugas memilih target: misalnya `20 ruas` atau `anggaran Rp X`.
6. Sistem menjalankan analisis traffic impact untuk kandidat yang relevan.
7. Optimizer menyusun paket dan tahapan.
8. Dashboard menampilkan rekomendasi, alasan, heatmap, dan konflik.
9. Petugas dapat membandingkan skenario dan melakukan override dengan alasan tercatat.
10. Setelah pelaksanaan, outcome dimasukkan kembali untuk evaluasi dan dataset historis.

---

## 9. Contoh Output

```text
PROGRAM PERBAIKAN JALAN 2027
Target: 20 ruas
Kandidat: 73 ruas

Direkomendasikan: 20 ruas

Jalan A
Need score       : 94%
Traffic impact   : Sedang
Tahap            : 1
Alasan           : kerusakan berat, akses pelayanan tinggi

Jalan B
Need score       : 91%
Traffic impact   : Tinggi
Keputusan        : tetap dipilih, Tahap 2
Alasan tahapan   : konflik dampak dengan Jalan A pada Jalan K/Simpang X
```

Sistem juga menampilkan kandidat yang belum terpilih agar hasil tidak menjadi kotak hitam.

---

## 10. Dashboard

### Perencanaan
- tahun/periode;
- target jumlah ruas;
- batas anggaran;
- kapasitas proyek simultan;
- skenario jam/periode pekerjaan.

### Hasil
- peta kandidat dan paket terpilih;
- need score;
- heatmap dampak traffic;
- area paling terdampak;
- matriks konflik;
- timeline tahapan;
- penggunaan anggaran;
- alasan dan confidence;
- alternatif skenario.

---

## 11. Arsitektur Teknologi

| Komponen | Teknologi | Peran |
|---|---|---|
| Backend | Python / FastAPI | API dan orkestrasi analisis |
| Database | PostgreSQL + PostGIS | data transaksi, spasial, historis |
| Peta | Leaflet / OSM | visualisasi |
| Graph | OSMnx + NetworkX | konektivitas jaringan |
| Priority baseline | SAW/rules | scoring kebutuhan awal |
| Traffic AI | XGBoost / Random Forest | prediksi dampak |
| Optimization | OR-Tools / Pyomo | paket dan tahapan |
| LLM | API LLM | laporan warga dan penjelasan |
| Routing opsional | Dijkstra/A* | jalur alternatif |

---

## 12. Tahapan Implementasi

### Fase 1 — Data dan baseline
- inventarisasi ruas;
- form laporan dan verifikasi;
- mapping laporan ke ruas;
- priority baseline;
- input biaya/durasi;
- graph jaringan jalan;
- pencatatan traffic history.

### Fase 2 — Recommendation MVP
- mode Top 10/Top 20/anggaran;
- optimizer paket berdasarkan need score, biaya, dan constraint dasar;
- dashboard rekomendasi;
- alasan pemilihan/non-pemilihan.

### Fase 3 — Traffic AI
- dataset historis traffic dan pekerjaan;
- feature engineering;
- training dan validasi XGBoost/Random Forest;
- prediksi area dampak;
- heatmap dan confidence.

### Fase 4 — Multi-project scheduling
- matriks konflik;
- optimasi tahapan/waktu;
- simulasi skenario;
- feedback outcome.

### Fase 5 — Lanjutan
- integrasi ATCS/CCTV;
- vehicle counting computer vision;
- spatio-temporal graph model;
- integrasi sistem PUPR/Dishub.

---

## 13. Evaluasi

### Priority
- kesesuaian dengan verifikasi ahli;
- stabilitas ranking;
- audit faktor penentu;
- pemeriksaan bias terhadap wilayah dengan sedikit laporan.

### Traffic AI
- MAE/RMSE untuk target numerik;
- precision/recall/F1 untuk klasifikasi risiko;
- akurasi spasial area terdampak;
- kalibrasi probabilitas/confidence.

### Optimizer
- total manfaat paket dibanding baseline Top-N sederhana;
- penggunaan anggaran;
- jumlah konflik yang berhasil dihindari;
- sensitivitas terhadap constraint dan bobot penalti.

### Operasional
- waktu penyusunan rekomendasi;
- persentase rekomendasi yang dapat dijelaskan;
- persentase override petugas dan alasannya;
- outcome setelah pelaksanaan.

---

## 14. Prinsip Tata Kelola

- Rekomendasi tidak otomatis menjadi keputusan.
- Petugas/pejabat dapat override dan alasannya dicatat.
- Laporan warga diverifikasi dan dideduplikasi.
- Jumlah laporan bukan bukti tunggal tingkat kerusakan.
- Data teknis tidak dihasilkan oleh LLM.
- Model/version/dataset dan parameter rekomendasi dicatat untuk audit.
- Ketidakpastian ditampilkan, bukan disembunyikan.
- Jika data belum cukup, gunakan baseline yang jujur daripada klaim AI yang tidak tervalidasi.

---

## 15. Keluaran Proyek

1. aplikasi prototipe JalanTanggap;
2. basis data ruas, laporan, pekerjaan, dan histori traffic;
3. modul priority scoring;
4. modul AI Traffic Impact Prediction;
5. multi-project optimizer;
6. dashboard rekomendasi Top 10/20/anggaran;
7. heatmap dan matriks konflik;
8. dokumentasi model, data, asumsi, dan evaluasi;
9. mekanisme feedback outcome untuk pengembangan model berikutnya.
