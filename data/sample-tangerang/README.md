# Data demo Tangerang–Rajeg

**SIMULASI, bukan data kondisi jalan Tangerang sebenarnya.** Konteks berasal dari cerita perjalanan M. Toha menuju Rajeg. Seluruh koordinat, jalan, fasilitas, laporan, proyek, dan lalu lintas dibuat untuk uji aplikasi. Garis GeoJSON adalah jaringan skematis di area geografis Tangerang, bukan hasil digitasi jalan nyata. Jangan digunakan untuk navigasi atau keputusan pekerjaan nyata.

## Isi paket

| File | Isi / penggunaan |
|---|---|
| nodes.csv | 25 simpul koordinat; latitude/longitude terpisah |
| segmen.csv | 40 ruas terhubung, arah, panjang, akses kendaraan, lebar |
| jaringan.geojson | Garis untuk peta Leaflet; koordinat [longitude, latitude] |
| laporan.csv | 100 laporan, termasuk duplikat dan lokasi yang belum jelas |
| label_llm.csv | Label referensi buatan manusia lewat template generator, bukan hasil model |
| penilaian.csv | 20 penilaian kondisi untuk input SAW |
| proyek.csv | 4 proyek usulan, aktif, dan selesai |
| pembatasan.csv | Penutupan total dan parsial; usulan terpisah dari kondisi aktif |
| aktivitas.csv | 12 aktivitas sekolah, pasar, fasilitas kesehatan, dan pulang kerja |
| traffic.csv | 237 observasi sintetis per arah pada 3 jam pengamatan |
| skenario.json | Empat kombinasi penutupan dengan hasil ada/tidak ada rute |
| aturan.json | Bobot contoh, jendela pelaporan, kendaraan, dan pasangan asal–tujuan |
| manifest.json | Sumber, versi, label simulasi, dan jumlah record |
| hasil_validasi.json | Hasil rute yang benar-benar dihitung validator |

## Cara memakai

```powershell
uv run python scripts/generate_sample.py
uv run python scripts/validate_sample.py
```

Generator deterministik dan akan menimpa file hasil generate dalam direktori ini. Edit generator untuk mengubah fixture. Tidak memerlukan API, token, maupun library tambahan.

## Cerita demo

- BASE: jaringan sebelum penutupan, rute tersedia.
- UTAMA: jalan keluar pertama ditutup, pengalihan masih tersedia.
- KONFLIK: jalan utama dan jalan keluar alternatif ditutup bersamaan; tidak ada rute dari asal. Sistem harus memberi tahu bahwa pengalihan tidak layak.
- SETELAH: tepat pukul 18.00 penutupan alternatif berakhir; jalan utama masih ditutup, tetapi rute tersedia kembali.

Semua waktu memakai WIB (+07:00). Interval adalah **[mulai, selesai)**: pada waktu selesai, pembatasan sudah tidak aktif. Pembatasan parsial tetap dapat dilalui pada fixture ini; kapasitasnya berkurang, tetapi validator tidak memprediksi antrean.

## Relasi dan aturan data

- segmen.from_node/to_node → nodes.id_node.
- laporan, penilaian, aktivitas, traffic, pembatasan.id_segmen → segmen.id_segmen.
- pembatasan.id_proyek → proyek.id_proyek.
- label_llm.id_laporan dan laporan.duplicate_of → laporan.id_laporan.
- Nilai kosong berarti belum tersedia, bukan nol. foto_url sengaja kosong karena tidak ada bukti foto.
- Scope candidate baru diterapkan jika dipilih dalam skenario; jangan otomatis menutup usulan pada kondisi dasar.
- Hitung pelapor unik hanya dari laporan valid untuk segmen dan jendela waktu yang dipilih. Duplikat dan laporan tanpa lokasi tidak ikut skor.
- Gunakan penilaian terbaru per segmen. Bobot 40/30/20/10 adalah contoh. Nilai kerusakan 1–5, dampak 1–4, peran 1–3 adalah skala demo, bukan standar teknis PUPR.
- Normalisasi SAW benefit dengan maksimum setiap kriteria; tangani kolom maksimum nol secara eksplisit. Jangan menilai segmen yang belum memiliki penilaian lengkap.
- traffic memakai mobil penumpang/jam/arah untuk volume dan kapasitas. Angka bukan kapasitas standar, hasil survei, atau konversi resmi satuan kendaraan campuran.

## Batas penggunaan dan pengembangan

Label development/test membantu uji alur, tetapi teks sengaja berbasis template dan mirip. Jangan memakai akurasi fixture ini sebagai klaim kualitas LLM terhadap laporan warga nyata. Evaluasi nyata perlu laporan beragam dengan split berdasarkan lokasi/kejadian dan label independen.

Graf memiliki satu arah dan satu ruas khusus motor. Daftar larangan belok kosong secara sengaja; peta nyata tetap membutuhkan pemrosesan pembatasan belok. Kewenangan jalan belum diverifikasi. Jalur pengalihan resmi dan proporsi perpindahan arus belum tersedia: rute yang dihitung adalah kandidat, bukan pengalihan yang disetujui.

Untuk pilot Tangerang sungguhan, ganti graf dengan OSM/data GIS yang diverifikasi, isi lokasi M. Toha dan jalur alternatif yang sebenarnya, konfirmasi jadwal proyek dari instansi berwenang, lalu kumpulkan data aktivitas/lalu lintas. Pertahankan provenance dan waktu pembaruan setiap sumber.
