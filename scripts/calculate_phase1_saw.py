"""Calculate JalanTanggap Fase 1 SAW ranking from synthetic survey data.

Inputs:
- data/sample-tangerang/survey_fase1.csv
- data/sample-tangerang/aturan_fase1.json

For the current synthetic fixture, each of the 20 segments has two deduplicated
complaint incidents, so jumlah_laporan_valid=2 for every segment.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "sample-tangerang"


def main():
    with (DATA / "aturan_fase1.json").open(encoding="utf-8") as f:
        rules = json.load(f)
    with (DATA / "survey_fase1.csv").open(encoding="utf-8") as f:
        surveys = list(csv.DictReader(f))

    criteria = rules["saw"]["criteria"]
    numeric_fields = {c["name"] for c in criteria}
    for row in surveys:
        for field in numeric_fields:
            if field == "jumlah_laporan_valid":
                row[field] = 2
            else:
                row[field] = float(row[field])

    max_values = {
        c["name"]: max(float(r[c["name"]]) for r in surveys)
        for c in criteria
    }

    results = []
    for row in surveys:
        score = 0.0
        for c in criteria:
            name = c["name"]
            value = float(row[name])
            if c["type"] == "benefit":
                normalized = value / max_values[name] if max_values[name] else 0
            else:
                positive = [float(r[name]) for r in surveys if float(r[name]) > 0]
                normalized = min(positive) / value if value and positive else 0
            score += normalized * float(c["weight"])

        sid = row["id_segmen"]
        results.append({
            "id_segmen": sid,
            "nama_jalan": f"Jalan simulasi Tangerang {sid[1:]}",
            "saw_score": score,
            **{c["name"]: row[c["name"]] for c in criteria},
        })

    results.sort(key=lambda x: x["saw_score"], reverse=True)
    for rank, row in enumerate(results, 1):
        row["rank"] = rank
        row["rekomendasi"] = "prioritas_top_10" if rank <= 10 else "cadangan"

    out = DATA / "hasil_saw_fase1.csv"
    fields = [
        "rank", "id_segmen", "nama_jalan", "saw_score",
        "tingkat_kerusakan", "dampak_akses", "peran_jalan",
        "panjang_rusak_m", "jumlah_laporan_valid", "fasilitas_kritis",
        "lama_tidak_ditangani_hari", "rekomendasi"
    ]
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in results:
            row["saw_score"] = f"{row['saw_score']:.4f}"
            writer.writerow({k: row[k] for k in fields})

    for row in results[:10]:
        print(f"{row['rank']:>2}. {row['nama_jalan']:<31} {row['saw_score']:.4f}")


if __name__ == "__main__":
    main()
