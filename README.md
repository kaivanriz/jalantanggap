# 🛣️ JalanTanggap

## Prediksi dampak perbaikan jalan sebelum kemacetan berpindah ke tempat lain

Ide ini berawal dari pengalaman pulang kerja menuju Rajeg. Di Jalan M. Toha ada perbaikan jalan dan kendaraan diarahkan melalui jalur alternatif. Ternyata, di jalur alternatif tersebut juga terdapat pekerjaan jalan.

Masalah yang ingin dijawab JalanTanggap kemudian diperluas:

> **Jika pemerintah memiliki beberapa rencana perbaikan jalan, ruas atau kawasan mana yang berpotensi mengalami penumpukan kendaraan, pekerjaan mana yang aman dilaksanakan bersamaan, dan pekerjaan mana yang sebaiknya dipisahkan waktunya?**

JalanTanggap merupakan rancangan sistem pendukung keputusan berbasis peta dengan **AI Traffic Impact Prediction**. Sistem membantu petugas menganalisis dampak rencana pekerjaan jalan terhadap jaringan jalan di sekitarnya sebelum pekerjaan dilaksanakan.

## Skenario utama

Misalnya terdapat **10 rencana perbaikan jalan**. Sistem menganalisis setiap pekerjaan berdasarkan lokasi, waktu, jenis penutupan, kondisi jaringan jalan, pekerjaan lain, dan histori lalu lintas.

Keluaran yang diharapkan antara lain:

- ruas/kawasan yang diprediksi mengalami peningkatan kepadatan;
- tingkat risiko dampak per ruas;
- heatmap zona terdampak;
- pekerjaan yang memiliki area dampak saling tumpang tindih;
- pekerjaan yang relatif aman dilakukan bersamaan;
- pekerjaan yang sebaiknya dipisahkan jadwalnya;
- perbandingan skenario waktu pengerjaan;
- jalur alternatif sebagai fitur pendukung bila diperlukan.

Contoh:

```text
Rencana: Perbaikan Jalan A
Waktu: Senin 07.00–16.00
Penutupan: 1 dari 2 lajur

Prediksi dampak:
🔴 Simpang X       risiko 92%
🔴 Jalan B         risiko 87%
🟡 Jalan D         risiko 64%
🟢 Jalan E         risiko 18%

Konflik:
⚠ Perbaikan Jalan D memiliki area dampak yang sama.

Rekomendasi:
Pisahkan jadwal Jalan A dan Jalan D atau pilih waktu di luar jam sibuk.
```

## Cara kerjanya

1. Data rencana pekerjaan dimasukkan: lokasi, waktu, durasi, jenis pekerjaan, dan pembatasan lajur.
2. Sistem mengambil karakteristik ruas dan konektivitas jaringan jalan.
3. Data historis lalu lintas per ruas digunakan sebagai baseline kondisi normal dan pola kemacetan.
4. Model AI/ML memprediksi perubahan volume, kecepatan, atau probabilitas kemacetan pada ruas sekitar.
5. Graph analysis membantu menganalisis penyebaran dampak melalui jaringan jalan.
6. Sistem membandingkan beberapa rencana pekerjaan dan mendeteksi area dampak yang saling bertumpuk.
7. Dashboard menampilkan heatmap, ranking area terdampak, matriks konflik, dan skenario jadwal.
8. Petugas meninjau rekomendasi dan tetap menjadi pengambil keputusan akhir.

## Posisi AI

**SAW (Simple Additive Weighting) bukan AI.** SAW dapat tetap digunakan secara opsional untuk prioritas administratif kebutuhan perbaikan, tetapi bukan komponen AI utama.

Komponen AI utama JalanTanggap adalah **Traffic Impact Prediction**.

Untuk MVP, model yang disarankan adalah **XGBoost atau Random Forest** karena cocok untuk data tabular, relatif mudah dijelaskan, dan lebih realistis dibanding langsung menggunakan model deep learning.

Contoh fitur model:

- histori volume dan kecepatan per ruas;
- hari dan jam;
- kapasitas dan jumlah lajur;
- jumlah lajur yang ditutup;
- jenis penutupan;
- durasi pekerjaan;
- kelas/lebar jalan;
- jarak dan konektivitas dari lokasi pekerjaan;
- pekerjaan lain yang aktif;
- aktivitas sekolah, pasar, atau fasilitas penting;
- cuaca jika tersedia.

Target model dapat berupa `delta_volume`, `delta_speed`, `congestion_probability`, atau kelas risiko rendah/sedang/tinggi.

Jika di kemudian hari tersedia data sensor/CCTV dalam jumlah besar dan historis panjang, model dapat dikembangkan ke **Spatio-Temporal Graph Neural Network** untuk mempelajari penyebaran kemacetan antar-ruas dari waktu ke waktu.

## Data historis kemacetan

Data sebaiknya dikumpulkan sebagai time-series per ruas:

```text
timestamp
id_segmen
speed
free_flow_speed
volume
congestion_index
source
```

Sumber dapat berasal dari Dishub (ATCS, traffic counter, CCTV, survei), penyedia data traffic bila tersedia, atau pengumpulan berkala oleh sistem sendiri.

Riwayat pekerjaan jalan juga penting agar model dapat belajar hubungan antara sebuah penutupan dan perubahan kondisi ruas di sekitarnya.

## Jika data AI belum cukup

Versi awal dapat menggunakan **baseline risk scoring** berbasis graph dan aturan seperti kapasitas jalan, volume normal, jarak dari pekerjaan, overlap pekerjaan, jam sibuk, dan aktivitas sekitar.

Baseline tersebut harus disebut **risk scoring**, bukan prediksi AI. Setelah data historis mencukupi, hasil baseline dibandingkan dengan model machine learning.

## Jalur alternatif

Pencarian jalur alternatif menggunakan Dijkstra/A* tetap dapat disediakan, tetapi menjadi fitur pendukung. Fokus utama JalanTanggap adalah **memprediksi efek domino pekerjaan jalan dan membantu penjadwalan beberapa pekerjaan agar tidak menciptakan titik kemacetan baru**.

## Dokumentasi

- [Konsep AI Traffic Impact Prediction](AI-Traffic-Impact.md)
- [Data nyata Kota Tangerang (sumber resmi + OSM)](data/real-tangerang/README.md)
- [Analisis koridor Kota Tangerang](data/real-tangerang/analisis_koridor.md)
- [Data sampel Tangerang–Rajeg (simulasi)](data/sample-tangerang/README.md)
- [Rencana proyek dan rencana kerja](Rencana-Proyek.md)
- [Kebutuhan data](Kebutuhan-Data.md)
- [Presentasi konsep di Notion](https://www.notion.so/3d7237742b4381ce8e80e08ac6906cc5)

## Teknologi yang direncanakan

| Komponen | Rencana |
|---|---|
| Backend | Python / FastAPI |
| Database spasial | PostgreSQL + PostGIS |
| Peta | Leaflet / OpenStreetMap |
| Jaringan jalan | OSMnx / NetworkX |
| AI Traffic Prediction | XGBoost / Random Forest (MVP) |
| Analisis spasial | Graph analysis |
| Rute opsional | Dijkstra / A* |
| Prioritas administratif | SAW opsional |
| Bahasa | API LLM untuk ekstraksi laporan dan penjelasan |
| Visualisasi | Heatmap dampak, timeline, matriks konflik |

## Status

Tahap **perencanaan dan dokumentasi**; aplikasi belum diimplementasikan. Data historis lalu lintas, data pekerjaan jalan, lokasi studi, dan target model perlu divalidasi sebelum model AI digunakan untuk rekomendasi operasional. Contoh angka dalam dokumentasi merupakan ilustrasi, bukan hasil pengukuran nyata.
