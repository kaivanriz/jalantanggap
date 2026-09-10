# Data nyata awal: pekerjaan jalan Kota Tangerang

Wilayah studi: **Kota Tangerang**. Diakses 10 September 2026. Isi folder ini berasal dari sumber resmi dan OpenStreetMap, bukan data simulasi. Paket simulasi tetap terpisah di `../sample-tangerang`.

## Isi folder

| File | Isi |
|---|---|
| pekerjaan_resmi.csv | Enam ruas pekerjaan dari berita resmi Pemkot Tangerang: jadwal, panjang, skema lalu lintas, status |
| jalur_alternatif_resmi.csv | Jalur alternatif dan imbauan resmi Dishub |
| osm/jalan_tangerang.geojson | Geometri jalan asli dari OpenStreetMap untuk koridor studi |
| osm/osm_raw.json | Respons mentah Overpass API |

## Temuan utama

- **Konflik yang kamu alami memang terdokumentasi resmi.** Dishub menyebut M. Toha dan Iskandar Muda punya jalur alternatif, Marsekal Suryadarma memakai contraflow, dan Sitanala tanpa rekayasa.
- **Jalur alternatif M. Toha (ALT01):** Arya Wangsakara dan Arya Santikan ke arah Otista, untuk arus dari Periuk/Pasar Kemis ke Kota Tangerang dan sebaliknya.
- **Jalur alternatif Iskandar Muda (ALT02):** Bayur–Kedaung Barat–Jembatan Gantung Kedaung Sepatan–Tangga Abu–Iskandar Muda menuju Marsekal Suryadarma (Pintu M1 Bandara).
- Empat ruas dimulai bersamaan pada 10–13 Agustus 2026 (M. Toha, Iskandar Muda, Marsekal Suryadarma, Sitanala), ditambah Teuku Umar (4 September) dan Garuda (5 September).
- Kota Tangerang memiliki sekitar **211 ruas jalan** dengan total **hampir 280 km**, kemantapan **93%** (metode PKRMS), anggaran rekonstruksi 2026 **Rp69 miliar** dari kebutuhan sekitar Rp290 miliar.

## Sumber resmi yang dibaca

- M. Toha resmi dimulai: https://www.tangerangkota.go.id/berita/detail/67779/proyek-perbaikan-jalan-raya-m-toha-karawaci-kota-tangerang-resmi-dimulai
- 4 ruas + rekayasa lalu lintas + jalur alternatif: https://tangerangkota.go.id/berita/detail/67788/4-ruas-jalan-diperbaiki-pemkot-tangerang-siapkan-rekayasa-lalu-lintas-dan-jalur-alternatifnya
- Iskandar Muda + jalur alternatif: https://www.tangerangkota.go.id/berita/detail/67833/jalan-iskandar-muda-diperbaiki-pemkot-tangerang-imbau-masyarakat-gunakan-jalur-alternatif
- Sitanala: https://www.tangerangkota.go.id/berita/detail/67917/jalan-sitanala-segera-direkonstruksi-pemkot-tangerang-pastikan-masih-bisa-dilalui
- Teuku Umar contraflow: https://www.tangerangkota.go.id/berita/detail/68613/perbaikan-jalan-teuku-umar-karawaci-dimulai-pemkot-tangerang-terapkan-rekayasa-contraflow
- M. Toha 98%: https://tangerangkota.go.id/berita/detail/68763/selesai-lebih-cepat-jalan-raya-m-toha-kota-tangerang-segera-dibuka
- Garuda 50%: https://tangerangkota.go.id/berita/detail/68649/satu-jalur-tuntas-dibeton-perbaikan-ruas-jalan-garuda-batuceper-capai-50-persen
- Marsekal Suryadarma 52,14%: https://tangerangkota.go.id/berita/detail/68721/sisa-satu-segmen-terakhir-perbaikan-ruas-jalan-marsekal-suryadarma-kota-tangerang-capai-52-14-persen
- Anggaran dan statistik jalan: https://tangerangkota.go.id/berita/detail/67458/pemkot-tangerang-siapkan-rp69-miliar-untuk-perbaikan-jalan-sejumlah-ruas-strategis-segera-dikerjakan

## Batasan penting

- **Status adalah kondisi saat berita diterbitkan**, bukan status langsung hari ini. M. Toha 98% pada 8 September; perkiraan dibuka Jumat bukan bukti sudah dibuka.
- **Belum ada koordinat batas pekerjaan dan jam penutupan.** Berita menyebut nama ruas, bukan poligon/segmen tiap pekerjaan. Karena itu pekerjaan ini **belum boleh** langsung menutup segmen pada mesin rute.
- Nama jalan OSM perlu diselaraskan: "Jalan Sultan Iskandar Muda" (63 way) adalah koridor panjang di timur (trunk), berbeda dari "Jalan Iskandar Muda" (19 way) di Neglasari. Verifikasi sebelum memakainya.
- Data ini Kota Tangerang. Rajeg berada di Kabupaten Tangerang, sehingga koridor Kabupaten belum tercakup.
- Portal `data.tangerangkota.go.id` dan `satudata.tangerangkab.go.id` tidak berhasil diakses lewat webfetch pada sesi ini; kegagalan akses bukan bukti data tidak tersedia.

## Sumber yang belum diambil

1. **Batas koordinat dan jam pembatasan** tiap pekerjaan: minta ke PUPR/Dishub atau ekstrak dari pengumuman resmi.
2. **Volume lalu lintas per arah/jam**: Dishub atau survei; belum ditemukan dalam sesi ini.
3. **Lokasi sekolah, pasar, fasilitas kesehatan** beserta jam kegiatan: OSM/direktori resmi + konfirmasi pengelola.
4. **Geometri koridor Rajeg (Kabupaten)**: OSM bbox kabupaten; belum diambil.

## Mengambil ulang geometri OSM

```powershell
uv run python scripts/fetch_osm_tangerang.py
```

Data © OpenStreetMap contributors (ODbL). Wajib atribusi. Atribut `lanes`, `oneway`, dan `maxspeed` sering kosong dan harus diverifikasi untuk rute nyata.
