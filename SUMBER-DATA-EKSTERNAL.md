# Sumber Data Eksternal

Catatan ini merangkum cara memperoleh data pendukung JalanTanggap dari sumber eksternal, status biaya, dan batas legal penggunaannya. Diperbarui 10 September 2026.

## Ringkasan sumber

| Sumber | Cocok untuk | Biaya | Batas penggunaan |
|---|---|---|---|
| OpenStreetMap (OSM) | Jaringan jalan, fasilitas | Gratis | Lisensi ODbL; wajib atribusi; boleh disimpan & dipakai latih model |
| Google Maps Platform | Peta, rute, geocoding, uji alur | Berbayar / ada tier gratis | Dilarang scraping, caching, dan **melatih model AI** dengan kontennya |
| Dishub Kota Tangerang (ATCS/counter/CCTV) | Historical traffic nyata (Fase 4) | Perlu koordinasi | Sesuai perjanjian data; biasanya butuh izin resmi |
| Survei/collector sendiri | Volume lalu lintas | Biaya operasional | Milik sendiri; paling aman untuk training |
| BPS / Satu Data Indonesia | Statistik jalan, panjang, kondisi | Gratis | Sesuai ketentuan portal |

## Google Maps Platform

### Jenis kunci API

| | Maps Demo Key | Standard Key |
|---|---|---|
| Kartu kredit | **Tidak perlu** | Perlu |
| Kuota | Terbatas, harian per API | Kuota normal |
| Tier gratis | Selalu gratis | 10.000 panggilan gratis per SKU/bulan |
| Untuk | Prototipe & belajar | Produksi |
| Bonus | — | Uji coba Google Cloud $300 untuk pelanggan baru |

### Langkah mendapatkan

**A. Demo Key (untuk belajar, tanpa kartu kredit)**

1. Punya akun Google.
2. Buka halaman Maps Demo Key: `https://mapsplatform.google.com/maps-demo-key/` → **Try for free** (mengarah ke `console.cloud.google.com/google/maps-hosted/tos`).
3. Setujui Terms of Service.
4. API key langsung terbit; bisa dipakai di sandbox.
5. Batasi kunci (HTTP referrer / aplikasi) dan aktifkan hanya API yang dipakai.
6. Jika kuota harian habis, panggilan berhenti sampai besok — tidak ada tagihan.

**B. Standard Key (jika butuh kuota lebih / produksi)**

1. Buat akun di Google Cloud Console.
2. Aktifkan **billing account** (butuh kartu kredit).
3. Aktifkan **Google Maps Platform** untuk proyek.
4. Buat API key, batasi penggunaannya, aktifkan API yang diperlukan saja.
5. Pelanggan baru bisa klaim uji coba **$300**.

### Harga (per 10 Sep 2026)

- **Pay as you go** — bayar sesuai pemakaian, ada tier gratis bulanan.
- **Langganan bulanan** (produk populer):
  - Starter — **$100/bulan**, 50.000 panggilan
  - Essentials — **$275/bulan**, 100.000 panggilan
  - Pro — **$1.200/bulan**, 250.000 panggilan
  - Enterprise — harga khusus

API yang relevan untuk JalanTanggap: Compute Routes, Compute Routes Matrix, Roads (Nearest Road / Route Traveled), Geocoding, Places, Dynamic Maps.

### Batas penting (ToS Google Maps Platform)

Dari Google Maps Platform Terms of Service, pasal **3.2.3 Restrictions Against Misusing the Services**:

- **(a) No Scraping** — dilarang mengekspor/mengunduh massal konten (petunjuk arah, matriks jarak, geocode, informasi jalan, dsb.).
- **(b) No Caching** — dilarang menyimpan konten Google Maps kecuali yang diizinkan khusus.
- **(c) No Creating Content From Google Maps Content** — termasuk **(vii) dilarang memakai konten Google Maps untuk melatih, menguji, memvalidasi, atau fine-tune model machine learning/AI.**

**Konsekuensi untuk JalanTanggap:**

- Google Maps **tidak boleh** menjadi sumber `traffic_history` atau fitur training model Fase 4.
- Google Maps **boleh** dipakai sebagai lapisan tampilan peta di aplikasi (dengan atribusi), atau untuk uji alur saat pengembangan.
- Untuk data lalu lintas yang boleh dilatih, gunakan **Dishub (ATCS/counter/CCTV)**, **survei sendiri**, atau produk khusus seperti **Roads Management Insights** (BigQuery, berbayar) yang memang ditujukan untuk pengelolaan jalan.

## OSM

- Sumber jaringan jalan dan fasilitas yang sudah dipakai proyek ini.
- Lisensi **ODbL**: wajib atribusi "© OpenStreetMap contributors", dan hasil turunan mengikuti ketentuan share-alike.
- Boleh disimpan, dimodifikasi, dan dipakai untuk model.

## Rekomendasi untuk JalanTanggap

1. **Untuk belajar/menguji integrasi peta:** pakai Maps Demo Key (gratis, tanpa kartu).
2. **Untuk `traffic_history` nyata:** ajukan permintaan data ke Dishub Kota Tangerang; jangan ambil dari Google.
3. **Selama data nyata belum ada:** tetap pakai `data/sample-tangerang/traffic_history.csv` (simulasi) untuk menguji pipeline, dengan label jelas sebagai simulasi.
4. **Untuk menampilkan peta di prototipe:** Google Maps atau Leaflet+OSM sama-sama boleh; Leaflet+OSM sudah dipakai dan bebas biaya.
