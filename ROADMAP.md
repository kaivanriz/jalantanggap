# Roadmap Pengembangan JalanTanggap

Dokumen ini menjadi **acuan utama pengembangan JalanTanggap**. Pengembangan dilakukan bertahap agar sistem dapat digunakan sejak data masih terbatas, kemudian berevolusi menjadi sistem rekomendasi berbasis AI setelah data historis mencukupi.

## Visi

JalanTanggap membantu pemerintah menjawab:

> Dari laporan warga dan hasil survei kondisi jalan, ruas mana yang perlu diprioritaskan; jika anggaran terbatas, kombinasi pekerjaan mana yang memberikan manfaat terbaik; dan bagaimana pekerjaan tersebut dapat dilaksanakan tanpa menciptakan masalah lalu lintas baru?

## Prinsip Pengembangan

1. Mulai dari metode yang transparan dan dapat diaudit.
2. Laporan warga harus diverifikasi dan tidak menggantikan survei teknis.
3. SAW digunakan sebagai baseline pada fase awal, bukan diklaim sebagai AI.
4. AI dikembangkan setelah tersedia data historis dan target/label yang layak.
5. Model AI tidak sekadar dilatih untuk meniru skor SAW.
6. Keputusan akhir tetap berada pada petugas/pejabat.
7. Setiap fase harus menghasilkan data yang berguna untuk fase berikutnya.

---

# Fase 1 — Smart Reporting + Survey Jalan + SAW

## Tujuan
Membangun MVP yang mampu mengolah laporan warga, menggabungkannya dengan hasil survei jalan, dan menghasilkan ranking prioritas perbaikan secara transparan.

## Alur

```text
Laporan Warga
     ↓
BERT / NLP
     ↓
Klasifikasi + Ekstraksi Informasi
     ↓
SBERT / Semantic Similarity
     ↓
Deteksi kandidat laporan duplikat
     ↓
Verifikasi Petugas
     +
Hasil Survey Jalan
     ↓
Data Ruas Terverifikasi
     ↓
SAW
     ↓
Priority Score
     ↓
Ranking Prioritas
     ↓
Top 10 / Top 20
```

## NLP

BERT/IndoBERT atau model NLP Bahasa Indonesia digunakan untuk memahami teks laporan warga, misalnya:
- klasifikasi jenis laporan;
- ekstraksi jenis keluhan;
- identifikasi dampak yang dilaporkan;
- ekstraksi landmark/lokasi dari teks;
- normalisasi laporan.

Sentence-BERT/SBERT atau sentence embedding digunakan untuk:
- semantic similarity;
- clustering laporan;
- kandidat deteksi laporan duplikat.

Similarity teks harus dikombinasikan dengan koordinat, waktu, dan verifikasi petugas.

NLP tidak boleh mengubah kalimat warga menjadi kesimpulan teknis final. Contoh `indikasi kerusakan berat` dari teks tetap harus dikonfirmasi melalui survei.

## SAW

Kriteria awal dapat mencakup:
- tingkat kerusakan;
- panjang kerusakan;
- dampak akses;
- kelas/fungsi jalan;
- jumlah laporan warga valid dan terdeduplikasi;
- lama belum ditangani;
- riwayat penanganan;
- fasilitas publik/akses penting.

Bobot dan normalisasi harus terdokumentasi dan disepakati dengan petugas teknis.

## Output
- database laporan terstruktur;
- data survei jalan;
- laporan valid/duplikat;
- skor SAW;
- ranking ruas;
- rekomendasi Top 10/Top 20;
- peta prioritas;
- alasan/skor per kriteria.

## Data yang wajib disimpan
Selain output, simpan keputusan petugas, kandidat yang dipilih/tidak dipilih, biaya, pelaksanaan, dan outcome agar menjadi dataset fase AI.

---

# Fase 2 — AI Prioritization

## Tujuan
Mengembangkan model AI yang mampu mempelajari pola kebutuhan/prioritas berdasarkan histori JalanTanggap dan outcome nyata.

## Alur

```text
Historical JalanTanggap Dataset
     ↓
Data Cleaning + Feature Engineering
     ↓
Train / Validation / Test
     ↓
XGBoost / LightGBM / Random Forest / model terpilih
     ↓
AI Priority Score
     ↓
Bandingkan dengan SAW + Penilaian Ahli
     ↓
AI Recommendation
```

## Data training kandidat
- kondisi jalan;
- laporan warga valid;
- hasil survei;
- fungsi jalan;
- fasilitas sekitar;
- riwayat penanganan;
- estimasi/realisasi biaya;
- keputusan petugas;
- kondisi setelah penanganan;
- outcome/manfaat yang dapat diukur.

## Prinsip
SAW tetap dipertahankan sebagai **baseline pembanding dan audit**. AI baru menjadi rekomendasi utama setelah evaluasi menunjukkan kualitas yang memadai.

AI tidak boleh hanya belajar `SAW score → AI score`. Target sebisa mungkin berasal dari keputusan ahli terverifikasi dan outcome nyata.

## Output
- AI Priority Model;
- AI Priority Score;
- feature importance/explanation;
- evaluasi AI vs SAW;
- rekomendasi prioritas berbasis AI.

---

# Fase 3 — AI-Assisted Multi-Project Optimization

## Tujuan
Mengubah ranking menjadi **paket pekerjaan optimal** dengan mempertimbangkan keterbatasan nyata.

## Pertanyaan

> Jika terdapat 73 kandidat tetapi anggaran hanya Rp20 miliar atau kapasitas maksimal 20 ruas, kombinasi mana yang sebaiknya dipilih?

## Input
- AI Priority Score;
- estimasi biaya;
- estimasi durasi;
- target jumlah ruas;
- anggaran;
- jumlah tim/sumber daya;
- periode pekerjaan;
- constraint teknis.

## Optimizer
Gunakan metode seperti OR-Tools CP-SAT, MILP/Pyomo, atau solver setara sesuai bentuk constraint.

Konsep objective:

```text
maximize:
    total manfaat / priority
    - penalti constraint
    - penalti risiko
```

Dengan constraint seperti:

```text
total_biaya <= anggaran
jumlah_proyek <= target
proyek_simultan <= kapasitas_tim
```

Optimization adalah optimisasi matematis; tidak perlu disebut AI jika komponennya bukan model belajar.

## Output
- paket Top 10/20;
- paket berdasarkan anggaran;
- kandidat terpilih/tidak terpilih beserta alasan;
- penggunaan anggaran;
- tahapan awal berdasarkan resource constraint.

---

# Fase 4 — AI Traffic Impact Prediction

## Tujuan
Memprediksi dampak pekerjaan jalan terhadap ruas/kawasan di sekitarnya.

## Data
- historical traffic per ruas;
- volume;
- speed/free-flow speed;
- congestion index;
- historical roadworks;
- waktu/hari;
- kapasitas dan jumlah lajur;
- jenis penutupan;
- pekerjaan aktif;
- road network/graph;
- fasilitas/event/cuaca bila tersedia.

## Alur

```text
Rencana Pekerjaan
       +
Historical Traffic
       +
Historical Roadworks
       +
Road Network
       ↓
Feature Engineering
       ↓
Traffic Impact AI
       ↓
Prediksi delta volume / delta speed
       ↓
Congestion Probability
       ↓
Affected Road / Area
       ↓
Heatmap Dampak
```

Untuk MVP, kandidat model adalah XGBoost/Random Forest dengan fitur spasial/graph. Model dipilih berdasarkan hasil validasi.

Jika data sensor/CCTV dan time-series sudah besar, fase lanjutan dapat mengevaluasi Spatio-Temporal Graph Neural Network.

## Output
- prediksi ruas terdampak;
- `delta_volume`;
- `delta_speed`;
- `congestion_probability`;
- kelas risiko;
- heatmap area terdampak;
- confidence/uncertainty.

Jika data historis belum memadai, gunakan baseline risk scoring dan jangan menyebutnya prediksi AI.

---

# Fase 5 — Intelligent Road Maintenance Planning

## Tujuan
Mengintegrasikan NLP, AI Prioritization, Traffic Impact AI, graph analysis, dan optimization menjadi sistem perencanaan perbaikan jalan yang utuh.

## Arsitektur Akhir

```text
                 LAPORAN WARGA
                       ↓
                  BERT / NLP
                       ↓
                 DATA SURVEY
                       ↓
              AI PRIORITY MODEL
                       ↓
              Kandidat Perbaikan
                       │
         ┌─────────────┴─────────────┐
         ↓                           ↓
 Anggaran / Resource         Historical Traffic
                                     ↓
                            TRAFFIC IMPACT AI
         │                           │
         └─────────────┬─────────────┘
                       ↓
              MULTI-PROJECT OPTIMIZER
                       ↓
              REKOMENDASI PROGRAM
                       ↓
       ┌───────────────┼───────────────┐
       ↓               ↓               ↓
 Paket Jalan       Tahapan/Jadwal   Dampak Traffic
 Top 10/20         Timeline         Heatmap
```

## Sistem harus dapat menjawab

> Dengan anggaran dan sumber daya yang tersedia, ruas mana yang sebaiknya diperbaiki, mana yang dapat dikerjakan bersamaan, kapan waktu pelaksanaannya, dan wilayah mana yang berpotensi terkena dampak lalu lintas?

## Output Akhir
- paket ruas terpilih;
- prioritas dan alasan;
- penggunaan anggaran;
- timeline/tahapan pekerjaan;
- konflik antarproyek;
- pekerjaan yang aman dilakukan bersamaan;
- pekerjaan yang harus dipisahkan;
- heatmap dampak;
- confidence AI;
- opsi skenario;
- jalur alternatif sebagai fitur pendukung bila dibutuhkan.

---

# Ringkasan Evolusi

```text
JalanTanggap 1.0
BERT/SBERT + Survey + SAW
→ Mana jalan yang prioritas?

JalanTanggap 2.0
NLP + AI Prioritization
→ Mana jalan yang direkomendasikan AI berdasarkan histori dan outcome?

JalanTanggap 3.0
AI Prioritization + Optimization
→ Dengan anggaran/resource yang tersedia, paket mana yang terbaik?

JalanTanggap 4.0
+ AI Traffic Impact Prediction
→ Jika paket tersebut dikerjakan, wilayah mana yang terdampak?

JalanTanggap 5.0
NLP + AI Priority + Traffic AI + Graph + Optimization
→ Mana yang diperbaiki, kapan, mana yang dapat bersamaan, dan apa dampaknya?
```

---

# Definition of Done per Fase

| Fase | Selesai ketika |
|---|---|
| 1 | laporan → NLP → verifikasi → survey → SAW → ranking dapat berjalan end-to-end dan dapat diaudit |
| 2 | AI priority tervalidasi terhadap baseline SAW dan penilaian/outcome nyata |
| 3 | optimizer dapat menghasilkan paket berdasarkan jumlah/anggaran dan menjelaskan constraint utama |
| 4 | traffic model tervalidasi pada pekerjaan nyata dan dapat menghasilkan peta dampak dengan uncertainty |
| 5 | semua komponen terintegrasi menjadi scenario planning dengan human approval dan audit trail |

---

# Aturan Acuan

Dokumen ini menjadi roadmap pengembangan. Perubahan besar pada urutan fase, peran model, atau tujuan utama sebaiknya diikuti pembaruan `ROADMAP.md`, `README.md`, `Rencana-Proyek.md`, dan `Kebutuhan-Data.md` agar dokumentasi tetap konsisten.
