# 🛣️ JalanTanggap

## Biar jalur alternatif nggak jadi masalah baru

Ide ini berawal dari pengalaman pulang kerja menuju Rajeg. Di Jalan M. Toha ada perbaikan jalan dan saya diarahkan melalui jalur alternatif. Ternyata, di jalur alternatif itu juga ada perbaikan jalan.

**Sebelum mengalihkan kendaraan, apakah kondisi jalur alternatif sudah dibandingkan dengan pekerjaan jalan lain yang sedang berjalan?**

JalanTanggap merupakan rancangan sistem pendukung keputusan untuk membantu petugas menentukan prioritas perbaikan, membandingkan waktu pekerjaan, dan mencari jalur alternatif otomatis.

## Cara kerjanya

1. Warga mengirim laporan beserta lokasi, deskripsi, dan foto pendukung.
2. LLM mengambil informasi penting dan membantu meminta klarifikasi.
3. Petugas memverifikasi lokasi dan kondisi jalan.
4. DSS menyusun peringkat prioritas perbaikan.
5. Sistem membandingkan rencana dengan pekerjaan aktif dan aktivitas sekitar.
6. Mesin rute mencari jalur yang mempertimbangkan penutupan, arah, dan pembatasan akses.
7. Petugas meninjau rekomendasi dan menyetujui rencana.

## Apa yang ditampilkan?

- Prioritas kebutuhan perbaikan beserta alasan.
- Konflik jadwal dan jalur pengalihan dengan pekerjaan lain.
- Kandidat rute alternatif dan tambahan jarak.
- Dampak terhadap aktivitas sekolah, pasar, dan akses fasilitas penting.
- Perbandingan skenario waktu pengerjaan.

Versi awal menilai **risiko konflik lalu lintas**, bukan menjanjikan prediksi waktu kemacetan. Estimasi beban membutuhkan data volume kendaraan, kapasitas efektif, dan asumsi pengalihan yang divalidasi.

## Dokumentasi

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
| Peta | Leaflet / OpenStreetMap |
| Jaringan jalan | OSMnx / NetworkX, dengan penanganan pembatasan akses dan belokan |
| Prioritas | SAW, bobot dikonfirmasi petugas |
| Bahasa | API LLM untuk ekstraksi dan penjelasan |
| Workflow | Status dan aturan di backend |

RAG belum diperlukan untuk prototipe awal. Petugas tetap memvalidasi data dan menetapkan keputusan.

## Status

Tahap **perencanaan dan dokumentasi**; aplikasi belum diimplementasikan. Lokasi detail, data lapangan, bobot keputusan, dan jadwal pelaksanaan masih perlu dikonfirmasi. Contoh skenario dan target dalam dokumen merupakan rancangan, bukan hasil pengukuran atau standar resmi.
