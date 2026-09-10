# Sumber Data Eksternal

Catatan ini merangkum cara memperoleh data pendukung JalanTanggap dari sumber eksternal, status biaya, dan batas legal penggunaannya. Diperbarui 10 September 2026.

## Ringkasan sumber

| Sumber | Cocok untuk | Biaya | Batas penggunaan |
|---|---|---|---|
| OpenStreetMap (OSM) | Jaringan jalan, fasilitas | Gratis | Lisensi ODbL; wajib atribusi; boleh disimpan & dipakai latih model |
| **Waze for Cities (WFC)** | **Lalu lintas real-time untuk pemerintah** | **Gratis (program mitra)** | Tanpa data historis; partner menyimpan feed sendiri; atribusi Waze |
| Google Maps Platform | Peta, rute, geocoding, uji alur | Berbayar / ada tier gratis | Dilarang scraping, caching, dan **melatih model AI** dengan kontennya |
| Dishub Kota Tangerang (ATCS/counter/CCTV) | Historical traffic nyata (Fase 4) | Perlu koordinasi | Sesuai perjanjian data; biasanya butuh izin resmi |
| Survei/collector sendiri | Volume lalu lintas | Biaya operasional | Milik sendiri; paling aman untuk training |
| BPS / Satu Data Indonesia | Statistik jalan, panjang, kondisi | Gratis | Sesuai ketentuan portal |

## Waze for Cities (WFC) — jalur resmi Google untuk data lalu lintas pemerintah

Google **memang punya** data lalu lintas, dan membagikannya ke **instansi pemerintah** lewat program **Waze for Cities** — terpisah dari Google Maps Platform dan **gratis**. Inilah cara sah mendapatkan data lalu lintas bergaya Google untuk pengelolaan jalan, tanpa melanggar ToS Maps API.

### Apa yang diberikan

Feed GeoRSS (XML/JSON) yang diperbarui **setiap 2 menit**, berisi:

| Bagian | Isi | Field penting |
|---|---|---|
| Traffic jams | Kemacetan per segmen | `speed`, `speedKPH`, `length`, `delay`, `level` (0–5), `street`, `line` (koordinat), `blockingAlertUuid` |
| Alerts | Insiden & laporan pengguna | `type`, `subtype` (ACCIDENT, ROAD_CLOSED, CONSTRUCTION, HAZARD_ON_ROAD_POT_HOLE, dll.), `reliability`, `confidence` |
| Irregularities | Kemacetan tak wajar | `speed`, **`regularSpeed`** (kecepatan normal historis), `delaySeconds`, `severity`, `jamLevel`, `trend` |

### Kenapa ini cocok untuk Fase 4

- `speed` + `regularSpeed` → bisa dihitung `congestion_index = 1 - speed/regularSpeed`.
- `level` (0–5) → kelas keparahan.
- `street` + `line` → bisa dipetakan ke `id_segmen`.
- **Tidak ada `volume`** — itu tetap butuh traffic counter/survei Dishub.

### Batasan penting

- **Waze tidak membagikan data historis.** Partner hanya menerima feed real-time; histori dibangun sendiri dengan menyimpan feed secara berkala. Google justru menyediakan panduan menyimpan WFC di Google Cloud.
- Data boleh disimpan & dianalisis oleh partner sesuai perjanjian mitra (jauh berbeda dari Maps Platform yang melarang caching/training).
- Wajib atribusi Waze.
- **Yang bisa mendaftar adalah instansi/lembaga**, bukan perorangan. Untuk JalanTanggap, yang mengajukan adalah Dishub/PUPR/Kominfo Kota Tangerang.

### Cara mengajukan

1. Buka Partner Hub Waze for Cities: `https://www.waze.com/wfc` (pendaftaran via `https://support.google.com/waze/partners/answer/10453062`).
2. Daftar sebagai instansi pemerintah; tentukan **managed area** (wilayah Kota Tangerang).
3. Setelah disetujui, ambil URL feed di **Toolbox → Waze Data Feed → Feed Links** (format JSON/XML).
4. Simpan feed berkala (mis. tiap 2–5 menit) untuk membangun histori.
5. Konversi ke skema `traffic_history.csv` memakai `scripts/waze_feed_to_traffic_history.py`.

Contoh struktur URL feed: `https://www.waze.com/partnerhub-api/partners/<partner-id>/waze-feeds/<token>?format=1&types=traffic,irregularities`

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
2. **Untuk lalu lintas real-time yang legal:** ajukan **Waze for Cities** melalui Dishub/PUPR/Kominfo Kota Tangerang (gratis, khusus instansi). Konverter sudah tersedia: `scripts/waze_feed_to_traffic_history.py`.
3. **Untuk volume kendaraan & histori panjang:** ajukan permintaan data ke Dishub Kota Tangerang (ATCS/counter/CCTV); Waze tidak menyediakan volume dan tidak membagikan histori.
4. **Selama data nyata belum ada:** tetap pakai `data/sample-tangerang/traffic_history.csv` (simulasi) untuk menguji pipeline, dengan label jelas sebagai simulasi.
5. **Untuk menampilkan peta di prototipe:** Google Maps atau Leaflet+OSM sama-sama boleh; Leaflet+OSM sudah dipakai dan bebas biaya.

## Catatan penting: Google punya datanya, tapi bukan lewat Maps API

- **Google Maps Platform** (berbayar) → untuk peta/rute/geocoding. **Dilarang** dipakai untuk data latih model.
- **Waze for Cities** (gratis, program mitra pemerintah) → inilah jalur sah untuk data lalu lintas ala Google: feed jams + irregularities tiap 2 menit, lengkap `speed`, `regularSpeed`, `delay`, `level`.
- Kekurangannya: **tanpa volume** dan **tanpa histori** — partner harus menyimpan feed sendiri. Volume tetap perlu Dishub/survei.

Jadi jawaban atas "Dishub tidak punya data kemacetan, Google punya": benar untuk sisi kepadatan, dan jalur resmi mengambilnya adalah **Waze for Cities**, bukan scraping Google Maps.
