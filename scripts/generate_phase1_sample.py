"""Generate deterministic synthetic fixtures for JalanTanggap Fase 1.

Outputs:
- data/sample-tangerang/laporan_fase1.csv
- data/sample-tangerang/ground_truth_fase1.csv
- data/sample-tangerang/survey_fase1.csv
- data/sample-tangerang/aturan_fase1.json

The coordinates are synthetic and based on the schematic road grid already used by
scripts/generate_sample.py. They are not real road-condition reports.
"""
import csv
import json
import math
import random
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "data" / "sample-tangerang"


def save_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def offset_point(a, b, t, along_jitter_m=0, cross_m=0):
    lat0 = a["latitude"] + t * (b["latitude"] - a["latitude"])
    lon0 = a["longitude"] + t * (b["longitude"] - a["longitude"])
    dy = (b["latitude"] - a["latitude"]) * 111320
    dx = (b["longitude"] - a["longitude"]) * 111320 * math.cos(math.radians(lat0))
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    xoff = ux * along_jitter_m - uy * cross_m
    yoff = uy * along_jitter_m + ux * cross_m
    lat = lat0 + yoff / 111320
    lon = lon0 + xoff / (111320 * math.cos(math.radians(lat0)))
    return round(lat, 7), round(lon, 7)


def build_graph():
    nodes = [
        {
            "id_node": f"N{r * 5 + c:02}",
            "latitude": round(-6.18 + r * .018, 6),
            "longitude": round(106.51 + c * .025, 6),
        }
        for r in range(5)
        for c in range(5)
    ]
    lookup = {n["id_node"]: n for n in nodes}
    edges = []
    for r in range(5):
        for c in range(5):
            u = r * 5 + c
            for v in ([u + 1] if c < 4 else []) + ([u + 5] if r < 4 else []):
                a, b = nodes[u], nodes[v]
                i = len(edges)
                lebar = 4 if i % 7 == 0 else 7
                edges.append(
                    {
                        "id_segmen": f"S{i:02}",
                        "from_node": a["id_node"],
                        "to_node": b["id_node"],
                        "nama": f"Jalan simulasi Tangerang {i:02}",
                        "lebar_m": lebar,
                        "jumlah_lajur": 1 if lebar < 5 else 2,
                    }
                )
    return lookup, {e["id_segmen"]: e for e in edges}


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    lookup, segments = build_graph()

    issue_defs = [
        ("jalan_rusak", "lubang", "keselamatan_pengendara"),
        ("jalan_rusak", "retak_memanjang", "kenyamanan_perjalanan"),
        ("jalan_rusak", "aspal_mengelupas", "keselamatan_pengendara"),
        ("jalan_rusak", "permukaan_bergelombang", "kecepatan_kendaraan"),
        ("drainase_jalan", "genangan", "akses_terganggu"),
        ("jalan_rusak", "aspal_amblas", "keselamatan_pengendara"),
    ]

    templates = {
        "lubang": [
            "Ada lubang cukup besar di {jalan} dekat {landmark}, motor sering menghindar mendadak.",
            "Mohon cek {jalan} sekitar {landmark}. Jalannya berlubang dan cukup mengganggu kendaraan.",
            "Aspal di {jalan}, dekat {landmark}, berlubang. Kalau ramai kendaraan jadi saling menghindar.",
        ],
        "retak_memanjang": [
            "Permukaan {jalan} dekat {landmark} retak memanjang dan terasa makin tidak rata.",
            "Mohon survei {jalan} sekitar {landmark}, ada retakan panjang pada badan jalan.",
            "Di sekitar {landmark} pada {jalan} aspalnya retak-retak memanjang.",
        ],
        "aspal_mengelupas": [
            "Aspal {jalan} dekat {landmark} mulai mengelupas dan kerikil berserakan.",
            "Lapisan atas jalan di {jalan} sekitar {landmark} banyak yang terkelupas.",
            "Mohon perbaikan {jalan} dekat {landmark}; permukaan aspalnya lepas dan kasar.",
        ],
        "permukaan_bergelombang": [
            "{jalan} dekat {landmark} terasa bergelombang sehingga kendaraan banyak mengurangi kecepatan.",
            "Permukaan {jalan} sekitar {landmark} naik turun dan tidak nyaman dilalui.",
            "Mohon dicek {jalan} dekat {landmark}, ada bagian jalan yang bergelombang.",
        ],
        "genangan": [
            "Setelah hujan, {jalan} dekat {landmark} sering tergenang dan kendaraan melambat.",
            "Ada genangan di {jalan} sekitar {landmark} setiap habis hujan, mohon dicek drainasenya.",
            "{jalan} dekat {landmark} sering ada air menggenang setelah hujan dan akses jadi terganggu.",
        ],
        "aspal_amblas": [
            "Ada bagian aspal amblas di {jalan} dekat {landmark}, cukup berbahaya saat malam.",
            "Permukaan {jalan} sekitar {landmark} turun seperti ambles, mohon segera disurvei.",
            "Mohon cek {jalan} dekat {landmark}; ada penurunan permukaan jalan yang cukup terasa.",
        ],
    }
    landmarks = [
        "sekolah simulasi",
        "pasar simulasi",
        "puskesmas simulasi",
        "halte simulasi",
        "persimpangan simulasi",
        "pertokoan simulasi",
    ]

    reports = []
    truth = []
    start = datetime(2026, 8, 1, 8, 0, 0)
    rid = 0

    # 20 segments x 5 reports = 100 reports.
    # Each segment contains two synthetic incidents: one with 3 reports and one with 2.
    for sidx in range(20):
        sid = f"S{sidx:02}"
        edge = segments[sid]
        a = lookup[edge["from_node"]]
        b = lookup[edge["to_node"]]
        issue1 = issue_defs[sidx % len(issue_defs)]
        issue2 = issue_defs[(sidx + 2) % len(issue_defs)]

        for group_idx, (issue, tbase, n_reports) in enumerate(
            [(issue1, 0.33, 3), (issue2, 0.70, 2)]
        ):
            category, indication, impact = issue
            duplicate_group = f"DG-{sid}-{group_idx + 1}"
            landmark = landmarks[(sidx + group_idx) % len(landmarks)]

            for j in range(n_reports):
                rng = random.Random(f"{sid}-{group_idx}-{j}")
                lat, lon = offset_point(
                    a,
                    b,
                    tbase,
                    along_jitter_m=rng.uniform(-12, 12),
                    cross_m=rng.uniform(-15, 15),
                )
                text = templates[indication][j % len(templates[indication])].format(
                    jalan=edge["nama"], landmark=landmark
                )
                if j == 1:
                    text += " Sudah terlihat beberapa hari."
                elif j == 2:
                    text += " Paling terasa saat jam ramai."

                reported_at = start + timedelta(
                    days=(sidx * 2 + group_idx * 5 + j) % 38,
                    hours=(sidx + j) % 10,
                    minutes=(sidx * 7 + j * 13) % 60,
                )
                report_id = f"F1-{rid:04d}"

                reports.append(
                    {
                        "id_laporan": report_id,
                        "id_pelapor": f"WSIM-{rid:04d}",
                        "waktu": reported_at.strftime("%Y-%m-%dT%H:%M:%S+07:00"),
                        "latitude": lat,
                        "longitude": lon,
                        "deskripsi": text,
                        "foto_url": "",
                        "status": "submitted",
                        "is_simulation": True,
                    }
                )
                truth.append(
                    {
                        "id_laporan": report_id,
                        "expected_id_segmen": sid,
                        "expected_category": category,
                        "expected_indication": indication,
                        "expected_impact": impact,
                        "expected_landmark": landmark,
                        "expected_duplicate_group": duplicate_group,
                        "expected_is_duplicate": j > 0,
                        "expected_needs_clarification": False,
                        "split": "test" if rid % 5 == 0 else "development",
                        "is_simulation": True,
                    }
                )
                rid += 1

    survey_types = ["lubang", "retak", "aspal_mengelupas", "gelombang", "genangan"]
    surveys = []
    for i in range(20):
        surveys.append(
            {
                "id_survey": f"SV-{i:03d}",
                "id_segmen": f"S{i:02d}",
                "tanggal_survey": "2026-09-09",
                "tingkat_kerusakan": 1 + (i * 3) % 5,
                "jenis_kerusakan": survey_types[i % len(survey_types)],
                "panjang_rusak_m": 20 + i * 6,
                "dampak_akses": 1 + (i * 2) % 4,
                "peran_jalan": 1 + i % 3,
                "fasilitas_kritis": i % 4,
                "lama_tidak_ditangani_hari": 30 + i * 11,
                "penilai": "PETUGAS_SIMULASI",
                "status_verifikasi": "verified",
                "is_simulation": True,
            }
        )

    rules = {
        "version": 1,
        "is_simulation": True,
        "purpose": "Fase 1 - NLP, semantic deduplication, map matching, survey, SAW",
        "input_file": "laporan_fase1.csv",
        "ground_truth_file": "ground_truth_fase1.csv",
        "survey_file": "survey_fase1.csv",
        "map_matching": {
            "expected_max_distance_m": 50,
            "note": "Koordinat dibuat 0-15 m dari segmen sintetis dan dijauhkan dari simpang.",
        },
        "deduplication": {
            "signals": ["semantic_similarity", "distance_m", "time_delta"],
            "ground_truth": "expected_duplicate_group",
        },
        "saw": {
            "criteria": [
                {"name": "tingkat_kerusakan", "weight": 0.30, "type": "benefit"},
                {"name": "dampak_akses", "weight": 0.20, "type": "benefit"},
                {"name": "peran_jalan", "weight": 0.15, "type": "benefit"},
                {"name": "panjang_rusak_m", "weight": 0.15, "type": "benefit"},
                {"name": "jumlah_laporan_valid", "weight": 0.10, "type": "benefit"},
                {"name": "fasilitas_kritis", "weight": 0.05, "type": "benefit"},
                {"name": "lama_tidak_ditangani_hari", "weight": 0.05, "type": "benefit"},
            ],
            "normalization": "benefit: value/max(value)",
            "note": "Bobot/skala hanya fixture demo, bukan standar teknis PUPR.",
        },
    }

    save_csv(ROOT / "laporan_fase1.csv", reports)
    save_csv(ROOT / "ground_truth_fase1.csv", truth)
    save_csv(ROOT / "survey_fase1.csv", surveys)
    (ROOT / "aturan_fase1.json").write_text(
        json.dumps(rules, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "laporan_fase1": len(reports),
                "ground_truth_fase1": len(truth),
                "survey_fase1": len(surveys),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
