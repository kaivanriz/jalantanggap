# Kebutuhan Data

## Sistem Pendukung Keputusan Prioritas dan Penjadwalan Perbaikan Jalan
### dengan Analisis Konflik Proyek Aktif dan Pencarian Rute Alternatif Otomatis

Dokumen ini menjelaskan seluruh data yang dibutuhkan sistem, cara memperolehnya, dan formatnya. Setiap kategori data diberi prioritas dan catatan keterbatasan.

---

## Ringkasan Kategori Data

| No | Kategori | Dipakai untuk | Sumber utama |
|---|---|---|---|
| A | Laporan warga | Prioritas & pengaduan | Form sistem |
| B | Ruas & kondisi jalan | Penilaian prioritas | PUPR / verifikasi petugas |
| C | Jaringan jalan | Pencarian rute otomatis | OpenStreetMap + verifikasi |
| D | Aktivitas sekitar | Analisis dampak waktu kerja | Pendataan manual |
| E | Rencana pekerjaan baru | Konteks skenario | Petugas teknis |
| F | Pekerjaan aktif | Deteksi konflik & kemacetan | Pengawas proyek |
| G | Lalu lintas dasar | Estimasi beban & risiko kemacetan | Dishub / survei |
| H | Aturan keputusan | Perhitungan DSS yang konsisten | Kesepakatan petugas |

---

## A. Data Laporan Warga

Dibuat langsung lewat formulir sistem (web/Google Form).

| Kolom | Tipe | Wajib | Catatan |
|---|---|---|---|
| `id_laporan` | Teks | Ya | Otomatis |
| `waktu_laporan` | Tanggal-waktu | Ya | Otomatis |
| `koordinat` | Lat, long | Ya | Pin peta |
| `nama_jalan` | Teks | Ya | Dari peta/diisi warga |
| `deskripsi` | Teks bebas | Ya | Kondisi & dampak |
| `foto` | Gambar | Opsional | Bukti pendukung |
| `dampak` | Teks | Opsional | Mis. "kendaraan sulit melintas" |
| `id_pelapor` | Teks | Ya | Internal, untuk deteksi duplikasi; tidak ditampilkan publik |
| `status` | Enum | Ya | Baru / Perlu klarifikasi / Valid / Duplikat / Ditangani / Selesai |
| `hasil_ekstraksi_llm` | JSON | - | Lokasi, jenis keluhan, dampak, info kurang |
| `hasil_verifikasi` | JSON | - | Catatan petugas, penilaian kondisi |

**Aturan penting:**
- Identitas pelapor hanya untuk deteksi laporan berulang, tidak untuk publik.
- Duplikasi diperiksa dengan kedekatan koordinat + kemiripan isi (LLM) + konfirmasi petugas.
- Laporan yang tidak jelas masuk antrean klarifikasi, bukan langsung bernilai rendah.

---

## B. Data Ruas dan Kondisi Jalan

Dipakai sebagai unit penilaian prioritas.

| Kolom | Tipe | Sumber | Catatan |
|---|---|---|---|
| `id_segmen` | Teks | PUPR / pendataan | Penghubung ke peta & laporan |
| `geometri` | Geom (garis) | OSM / data GIS | Bentuk segmen di peta |
| `status_kewenangan` | Enum | PUPR | Kota/kab/provinsi/nasional |
| `kelas_jalan` | Teks | PUPR | Fungsi jalan |
| `tingkat_kerusakan` | Skala 1–5 | Verifikasi petugas | Berdasarkan pedoman penilaian |
| `panjang_rusak_m` | Angka | Survei/verifikasi | Bagian yang rusak |
| `dampak_akses` | Enum | Verifikasi | Normal / Terganggu / Sulit / Terputus |
| `tgl_penanganan_terakhir` | Tanggal | Riwayat PUPR | Opsional |

**Catatan:** Pin laporan warga perlu dihubungkan ke segmen yang benar. Segmen terdekat secara koordinat belum tentu yang dimaksud (persimpangan, jalan bertingkat).

---

## C. Data Jaringan Jalan (untuk Rute Otomatis)

**Ini data inti pencarian rute.**

| Data | Kegunaan |
|---|---|
| Simpul & hubungan antarsegmen | Mengetahui jalan yang benar-benar tersambung |
| Panjang segmen | Menghitung jarak rute |
| Arah jalan (satu/dua arah) | Menghindari rute melawan arah |
| Pembatasan akses & belokan | Menghindari ruas/manuver yang dilarang |
| Jenis jalan & kendaraan yang diizinkan | Menyesuaikan rute dengan pengguna |
| Lebar jalan | Memeriksa kelayakan pengalihan |
| Kondisi permukaan | Kelayakan pengalihan |
| Batas tinggi/berat | Penting untuk kendaraan besar |

**Sumber:**
- **OpenStreetMap (OSM)** sebagai sumber awal.
- Atribut yang tidak tercatat (lebar, batasan kendaraan) ditandai **"belum diketahui"** dan diverifikasi untuk kandidat rute yang akan digunakan.
- `segmen_tertutup` (segmen yang ditutup + periode) dimasukkan oleh petugas.

**Cara kerja pencarian rute:**
1. Ambil jaringan jalan sekitar lokasi.
2. Keluarkan segmen yang ditutup total pada waktu skenario.
3. Terapkan pembatasan akses pada segmen lain.
4. Cari kandidat rute antara titik sebelum & sesudah penutupan (atau antara asal & tujuan).
5. Bandingkan tambahan jarak, benturan aktivitas, dan tumpang tindih dengan pengalihan proyek lain.
6. Jika tidak ada rute layak: tampilkan "belum ditemukan rute yang layak", jangan memaksakan jalan kecil.

---

## D. Data Aktivitas Sekitar

Dipakai untuk membandingkan waktu pengerjaan dan dampak jalur pengalihan.

| Data | Contoh | Sumber |
|---|---|---|
| Lokasi fasilitas | Sekolah, pasar, puskesmas, rumah sakit | OSM / data daerah / survei |
| Jadwal aktivitas | Jam masuk/pulang sekolah, hari pasar | Form pendataan / konfirmasi pengelola |
| Kegiatan sementara | Acara warga, penutupan jalan lain | Kecamatan / kelurahan |
| Kebutuhan akses penting | Pintu faskes harus tetap terjangkau | Konfirmasi petugas/pengelola |

**Keterbatasan:** Tanpa data volume lalu lintas, sistem hanya menilai **potensi benturan aktivitas**, bukan besarnya kemacetan.

---

## E. Data Rencana Pekerjaan Baru

| Kolom | Isi | Sumber |
|---|---|---|
| `id_segmen` | Segmen yang dikerjakan | Petugas teknis |
| `jenis_pekerjaan` | Perbaikan/penambalan/rekonstruksi | Petugas |
| `durasi_rencana` | Hari & jam | Petugas |
| `opsi_waktu` | Kandidat tanggal/jam yang layak secara teknis | Petugas |
| `jenis_penutupan` | Tutup total / sebagian lajur / buka-tutup | Petugas |
| `kendaraan_diizinkan` | Jenis kendaraan yang boleh lewat | Petugas |
| `status_persetujuan` | Draf / disetujui / ditolak / dikerjakan | Pejabat |

**Penting:** Durasi proyek ≠ durasi penutupan jalan. Proyek bisa sebulan, tetapi jalan hanya ditutup jam tertentu.

---

## F. Data Pekerjaan Aktif / Terjadwal

Untuk mendeteksi konflik dan menilai kemacetan.

| Kolom | Isi |
|---|---|
| `id_proyek` | Identitas proyek |
| `segmen_terkena` | Segmen yang ditutup/dibatasi |
| `status_proyek` | Aktif / Terjadwal / Selesai |
| `periode_pembatasan` | Tanggal & jam pembatasan |
| `jenis_pembatasan` | Tutup total / sebagian / buka-tutup |
| `rute_pengalihan_aktif` | Segmen yang sedang dipakai sebagai pengalihan |
| `progres_terakhir` | Pembaruan jadwal & waktu pembaruan |
| `pic` | Pengawas/pelaksana penanggung jawab |

**Sumber:** Pengawas proyek, PUPR, Dishub.

---

## G. Data Lalu Lintas Dasar

Dua tingkat analisis:

### G1. Indikator risiko konflik (tanpa data lalu lintas — direkomendasikan untuk awal)
Sistem memeriksa:
- Tumpang tindih waktu pembatasan antarpoyek.
- Jalur alternatif yang melewati pekerjaan aktif.
- Beberapa pengalihan memakai segmen yang sama.
- Jalan penerima pengalihan sempit / akses terbatas.
- Benturan dengan jam sekolah atau pasar.
- Ketersediaan rute lain yang layak.

**Keluaran:** Risiko rendah / sedang / tinggi + alasan. Ini **penilaian risiko**, bukan prediksi waktu antrean.

### G2. Estimasi beban lalu lintas (jika data volume tersedia)
Data yang dibutuhkan:

| Kolom | Contoh |
|---|---|
| `volume_per_jam` | Kendaraan/jam per arah (jam sibuk & non-sibuk) |
| `kapasitas_jalan` | Kendaraan/jam per lajur |
| `jumlah_lajur` | Termasuk lajur yang ditutup saat kerja |
| `asumsi_peralihan` | % kendaraan yang diperkirakan pindah ke rute alternatif |
| `arah_dominan` | Arus pagi/sore |

Perhitungan:
```
Beban setelah pengalihan = lalu lintas dasar + kendaraan yang beralih
Beban dibandingkan dengan kapasitas efektif saat pekerjaan berlangsung
```

**Keterbatasan:** Prediksi waktu tempuh/antrean memerlukan model tambahan dan validasi. Asumsi peralihan harus dinyatakan jelas dan diuji kepekaannya.

---

## H. Aturan Keputusan (Bukan data, tapi wajib ditetapkan)

| Aturan | Isi |
|---|---|
| Kriteria prioritas | Tingkat kerusakan, dampak akses, peran jalan, jumlah pelapor valid, lama belum ditangani |
| Bobot kriteria | Ditetapkan/konfirmasi bersama petugas, didokumentasikan |
| Definisi skor | Skala tiap kriteria harus jelas agar penilaian konsisten |
| Ketentuan laporan valid | Koordinat jelas, foto/deskripsi cukup, bukan duplikat |
| Batasan rute wajib | Jalan dilarang untuk kendaraan tertentu tidak boleh jadi alternatif |
| Preferensi rute | Tambahan jarak, kesesuaian jalan, benturan aktivitas |

---

## I. Prioritas Ketersediaan Data

| Urutan | Data | Keterangan |
|---|---|---|
| 1 | Jaringan jalan (OSM) | Gratis, langsung diunduh |
| 2 | Laporan warga | Dibuat lewat form sistem |
| 3 | Ruas & kondisi jalan | Data PUPR atau survei |
| 4 | Aktivitas sekitar | Pendataan manual (sekolah, pasar, faskes) |
| 5 | Rencana pekerjaan | Dari petugas |
| 6 | Pekerjaan aktif | Perlu koordinasi pengawas proyek |
| 7 | Lalu lintas dasar | Opsional; mulai dari indikator risiko |

---

## J. Contoh Format (CSV)

### `laporan.csv`
```csv
id_laporan,waktu,koordinat,nama_jalan,deskripsi,dampak,status
L001,2026-09-01 08:12,-6.9174,107.6191,Jalan Melati,Lubang besar di depan sekolah banyak lubang,ban bocor jika lewat,Valid
L002,2026-09-02 10:30,-6.9176,107.6195,Jalan Melati,Depan sekolah rusak parah,sulit melintas saat pagi,Valid
```

### `segmen_jalan.csv`
```csv
id_segmen,nama_jalan,kewenangan,tingkat_kerusakan,panjang_rusak_m,dampak_akses
S001,Jalan Melati,Kota,5,120,Terputus
S002,Jalan Anggrek,Kota,3,40,Terganggu
```

### `pekerjaan_aktif.csv`
```csv
id_proyek,segmen_terkena,status,periode_mulai,periode_selesai,jenis_pembatasan,rute_pengalihan
P001,S010,Aktif,2026-09-01,2026-10-15,Tutup total,S009
```

### `aktivitas_sekitar.csv`
```csv
id,nama,tipe,koordinat,jam_padat,keterangan
A001,SDN 01 Melati,Sekolah,-6.9180,107.6198,06.30-07.30;15.00-16.00,
A002,Pasar Melati,Pasar,-6.9170,107.6180,04.00-09.00,,
```

---

## K. Keterbatasan dan Asumsi

1. **Laporan warga** menggambarkan lokasi yang dilaporkan, bukan kondisi seluruh jalan di daerah.
2. **Jumlah laporan ≠ bukti kondisi.** Diberi bobot kecil agar jalan di wilayah yang jarang melapor tetap bisa diprioritaskan berdasarkan kondisi.
3. **OSM** belum tentu lengkap atribut lebar/pembatasan → verifikasi kandidat rute.
4. **Indikator kemacetan awal** adalah risiko konflik, bukan simulasi lalu lintas.
5. **LLM** tidak menghitung volume/capaK; angka berasal dari data.
6. Data simulasi hanya untuk demonstrasi sistem, bukan kesimpulan pelayanan nyata.