# Analisis koridor Kota Tangerang (data nyata)

Dibuat 10 September 2026 dari OpenStreetMap (© kontributor, ODbL) dan berita resmi Pemkot Tangerang. Semua ini **bukan data simulasi**.

## Rangkuman

1. **Konteks riwayatmu terbukti di data resmi:** Dishub Kota Tangerang menetapkan jalur alternatif M. Toha melalui **Jalan Arya Wangsakara dan Arya Santikan ke arah Otista**, sementara **Iskandar Muda dan Marsekal Suryadarma diperbaiki bersamaan** pada Agustus 2026. Inilah bentuk konflik yang kamu alami.
2. **Graf koridor dibangun dari OSM asli:** 26.939 node persimpangan, 61.275 edge berarah (bebas library, ID node OSM asli, kontraksi ruas).
3. **Rute uji nyata:** dari **Jalan Aria Wangsakara ke Aria Santika** (jarak 3,44 km) rute terpendek benar-benar melewati **kedua jalan alternatif resmi** tersebut. Artinya graf mampu menemukan jalur pengalihan resmi tanpa input manual.
4. **Keterbatasan penting:** jalan utama **"Jalan Raya M. Toha" tidak terpetakan dengan nama itu di OSM**; hanya muncul "Jalan Toha Raya" (spur kecil) dan gang-gang. Untuk menutup segmen pekerjaan M. Toha yang tepat, perlu pemetaan manual ke way OSM atau data batas pekerjaan dari PUPR.
5. Uji "Barat–Timur koridor" dan "Wangsakara→Otista" **tidak menemukan rute**, karena Otista berada di luar bbox koridor dan batas bbox memotong konektivitas. Ini menunjukkan graf per-koridor belum cukup untuk analisis seluruh Kota; butuh jaringan kota penuh.

## Bagaimana membuat ulang

```powershell
# 1. Ambil semua jalan drivable koridor Karawaci–Neglasari, bangun graf persimpangan
uv run python scripts/build_corridor_graph.py
# 2. Uji rute dan tulis analisis_rute.json
uv run python scripts/route_corridor.py
# 3. Koridor nama jalur alternatif resmi (GeoJSON kecil)
uv run python scripts/analyze_osm_detour.py
# 4. (Opsional) Jalan bernama seluruh Kota Tangerang
uv run python scripts/fetch_osm_tangerang.py
```

File besar hasil unduhan (`koridor_raw.json`, `koridor_jaringan.geojson`, `osm_raw.json`) sengaja **tidak masuk git** (dibuat ulang). Yang masuk git: `koridor_nodes.csv`, `koridor_edges.csv`, `jalan_tangerang.geojson`, `koridor_detour_mtoha.geojson`, `analisis_rute.json`, dan script.

## Status data

| Data | Status |
|---|---|
| Daftar pekerjaan resmi (6 ruas) | Ada (`pekerjaan_resmi.csv`) |
| Jalur alternatif resmi | Ada (`jalur_alternatif_resmi.csv`) |
| Graf jalan koridor (OSM) | Ada (`koridor_nodes.csv`, `koridor_edges.csv`) |
| Batas/koordinat segmen pekerjaan | **Belum ada** — perlu PUPR atau pemetaan manual |
| Jam penutupan/laju | **Belum ada** — berita hanya menyebut skema (contraflow/buka-tutup) |
| Volume lalu lintas | **Belum ada** |
| Sekolah/pasar/faskes + jam | **Belum diambil** |

## Implikasi untuk JalanTanggap

- Konsep "cek jalur alternatif sebelum pengalihan" **terverifikasi relevan** terhadap kejadian nyata M. Toha 2026.
- Rute alternatif bisa ditemukan otomatis dari OSM, tetapi **closure harus ditetapkan ke segmen OSM yang benar**; nama jalan di berita ≠ nama OSM selalu.
- Untuk prototipe, siapkan **pemetaan nama jalan resmi ↔ way OSM** sebagai langkah data tersendiri.