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
| roadworks_events.csv | 2 event pekerjaan historis (tutup total S01, lajur ditutup S09) + segmen terdampak |
| traffic_history.csv | 9.954 baris time-series per ruas/jam (Fase 4): speed, free_flow_speed, volume, congestion_index, source, quality_flag |
| traffic_ai_dataset.csv | 34 baris pasangan baseline vs event untuk training XGBoost: fitur (hop, lajur, jam sibuk, fasilitas, overlap) + target (delta_volume, delta_speed, congestion) |
| skenario.json | Empat kombinasi penutupan dengan hasil ada/tidak ada rute |
| waze_feed_contoh.json | **Contoh simulasi** struktur feed Waze for Cities (bukan data Waze asli) |
| contoh_mapping_jalan.csv | Contoh pemetaan nama jalan → id_segmen untuk konverter Waze |
| traffic_history_from_waze.csv | Hasil uji konverter Waze → skema traffic_history (volume kosong: Waze tidak menyediakan) |
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
- laporan, penilaian, aktivitas, pembatasan.id_segmen → segmen.id_segmen.
- pembatasan.id_proyek → proyek.id_proyek.
- label_llm.id_laporan → laporan.id_laporan; laporan.id_cluster_duplikat menandai laporan sejenis (satu cluster = satu segmen).
- roadworks_events.id_segmen_pekerjaan & segmen_terdampak → segmen.id_segmen.
- traffic_ai_dataset.id_event → roadworks_events.id_event; source_pekerjaan & target_segment → segmen.id_segmen.
- Nilai kosong berarti belum tersedia, bukan nol. foto_url sengaja kosong karena tidak ada bukti foto.
- Scope candidate baru diterapkan jika dipilih dalam skenario; jangan otomatis menutup usulan pada kondisi dasar.
- Hitung pelapor unik hanya dari laporan valid untuk segmen dan jendela waktu yang dipilih. Duplikat dan laporan tanpa lokasi tidak ikut skor.
- Gunakan penilaian terbaru per segmen. Bobot 40/30/20/10 adalah contoh. Nilai kerusakan 1–5, dampak 1–4, peran 1–3 adalah skala demo, bukan standar teknis PUPR.
- Normalisasi SAW benefit dengan maksimum setiap kriteria; tangani kolom maksimum nol secara eksplisit. Jangan menilai segmen yang belum memiliki penilaian lengkap.
- traffic_history memakai mobil penumpang/jam/arah. Angka bukan kapasitas standar, hasil survei, atau konversi resmi satuan kendaraan campuran.
- Baseline dataset dihitung dari hari tanpa event (1–2 dan 8–9 September); event aktif 3–7 September pukul 16.00–17.00. `quality_flag` menandai kondisi (`ok`, `penutupan_total`, `lajur_ditutup`, `penerima_pengalihan`, digabung `+` bila beririsan).

## Batas penggunaan dan pengembangan

Label development/test membantu uji alur, tetapi teks sengaja berbasis template dan mirip. Jangan memakai akurasi fixture ini sebagai klaim kualitas LLM terhadap laporan warga nyata. Evaluasi nyata perlu laporan beragam dengan split berdasarkan lokasi/kejadian dan label independen.

**Kesesuaian roadmap:** `traffic_history.csv`, `roadworks_events.csv`, dan `traffic_ai_dataset.csv` mengikuti skema Fase 4 di `Kebutuhan-Data.md` dan `AI-Traffic-Impact.md` (time-series per ruas + pasangan baseline vs gangguan). Model XGBoost/Random Forest bisa diuji langsung pada `traffic_ai_dataset.csv`, tetapi angka di sini **sintetis** sehingga hanya membuktikan pipeline berjalan, bukan kualitas prediksi nyata.

Graf memiliki satu arah dan satu ruas khusus motor. Daftar larangan belok kosong secara sengaja; peta nyata tetap membutuhkan pemrosesan pembatasan belok. Kewenangan jalan belum diverifikasi. Jalur pengalihan resmi dan proporsi perpindahan arus belum tersedia: rute yang dihitung adalah kandidat, bukan pengalihan yang disetujui.

Untuk pilot Tangerang sungguhan, ganti graf dengan OSM/data GIS yang diverifikasi, isi lokasi M. Toha dan jalur alternatif yang sebenarnya, konfirmasi jadwal proyek dari instansi berwenang, lalu kumpulkan data aktivitas/lalu lintas. Pertahankan provenance dan waktu pembaruan setiap sumber.
