import csv
import subprocess
from multiprocessing import Pool, cpu_count
from pathlib import Path
from statistics import fmean, pstdev

SEED_START = 0
RUNS = 30
TICKS = 3600
MIN_COVERAGE = 60.0
LOG_DIR = Path("logs")
CRASH_DIR = LOG_DIR / "crash"
INTELLIGENT_CONFIG_DIR = LOG_DIR / "intelligent_config"

PREDICTOR_CONFIGS = [
    {"name": "baseline", "tau": 40.0, "alpha": 0.08, "threshold": 0.55, "window": 160, "radius": 2},
    {"name": "sensitive_a", "tau": 40.0, "alpha": 0.18, "threshold": 0.24, "window": 220, "radius": 2},
    {"name": "sensitive_b", "tau": 55.0, "alpha": 0.20, "threshold": 0.22, "window": 260, "radius": 2},
    {"name": "balanced_a", "tau": 45.0, "alpha": 0.16, "threshold": 0.26, "window": 220, "radius": 2},
    {"name": "balanced_b", "tau": 35.0, "alpha": 0.20, "threshold": 0.25, "window": 180, "radius": 2},
    {"name": "recall_a", "tau": 80.0, "alpha": 0.20, "threshold": 0.10, "window": 500, "radius": 2},
    {"name": "recall_b", "tau": 80.0, "alpha": 0.20, "threshold": 0.05, "window": 500, "radius": 2},
    {"name": "recall_c", "tau": 80.0, "alpha": 0.20, "threshold": 0.03, "window": 500, "radius": 2},
]

METRIC_FIELDS = [
    "avg_response_time",
    "coverage_percent",
    "incidents_prevented",
    "prediction_rate",
    "prediction_precision",
    "prediction_recall",
    "incidents_total",
    "resolved_incidents",
]


def run_single(args):
    mode, seed, predictor = args
    cmd = [
        "python",
        "main.py",
        "--mode",
        mode,
        "--seed",
        str(SEED_START + seed),
        "--ticks",
        str(TICKS),
        "--headless",
    ]
    if mode == "intelligent" and predictor is not None:
        cmd.extend(
            [
                "--predictor-tau",
                str(predictor["tau"]),
                "--predictor-alpha",
                str(predictor["alpha"]),
                "--predictor-threshold",
                str(predictor["threshold"]),
                "--predictor-window",
                str(predictor["window"]),
                "--predictor-radius",
                str(predictor["radius"]),
            ]
        )

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        name = predictor["name"] if predictor is not None else mode
        CRASH_DIR.mkdir(parents=True, exist_ok=True)
        with open(CRASH_DIR / f"crash_{name}_seed_{seed}.log", "w", encoding="utf-8") as f:
            f.write("CMD:\n")
            f.write(" ".join(cmd))
            f.write("\n\nSTDOUT:\n")
            f.write(result.stdout)
            f.write("\n\nSTDERR:\n")
            f.write(result.stderr)
        raise RuntimeError(f"Simulation crashed mode={mode} cfg={name} seed={seed}")

    lines = [line for line in result.stdout.splitlines() if line.strip()]
    if len(lines) < 2:
        name = predictor["name"] if predictor is not None else mode
        CRASH_DIR.mkdir(parents=True, exist_ok=True)
        with open(CRASH_DIR / f"bad_output_{name}_seed_{seed}.log", "w", encoding="utf-8") as f:
            f.write(result.stdout)
        raise RuntimeError(f"Incomplete output mode={mode} cfg={name} seed={seed}")

    header = lines[-2].split(",")
    values = lines[-1].split(",")
    parsed = {k: float(v) for k, v in zip(header, values)}
    return parsed


def run_batch(mode, predictor=None):
    tasks = [(mode, seed, predictor) for seed in range(RUNS)]
    workers = max(1, cpu_count() - 1)
    with Pool(workers) as pool:
        return pool.map(run_single, tasks)


def write_rows(file_path, rows):
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=METRIC_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row[k] for k in METRIC_FIELDS})


def summarize_rows(rows):
    summary = {}
    for key in METRIC_FIELDS:
        values = [row[key] for row in rows]
        summary[f"{key}_mean"] = fmean(values) if values else 0.0
        summary[f"{key}_std"] = pstdev(values) if len(values) > 1 else 0.0
    return summary


def score_summary(summary):
    coverage = summary["coverage_percent_mean"]
    if coverage < MIN_COVERAGE:
        return -1e9
    precision = summary["prediction_precision_mean"]
    recall = summary["prediction_recall_mean"]
    prevention = summary["prediction_rate_mean"]
    f1 = (2.0 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    return f1 + (0.10 * prevention)


def run_reactive():
    print(f"\nRunning reactive baseline ({RUNS} runs)...\n")
    rows = run_batch("reactive")
    write_rows("results_reactive.csv", rows)
    return summarize_rows(rows)


def run_intelligent_tuning():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    INTELLIGENT_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    all_summaries = []
    best_cfg = None
    best_rows = []
    best_score = -1e18

    for cfg in PREDICTOR_CONFIGS:
        print(f"\nRunning intelligent config={cfg['name']} ({RUNS} runs)...\n")
        rows = run_batch("intelligent", predictor=cfg)
        cfg_file = INTELLIGENT_CONFIG_DIR / f"results_intelligent_{cfg['name']}.csv"
        write_rows(cfg_file, rows)

        summary = summarize_rows(rows)
        summary["config"] = cfg["name"]
        summary["tau"] = cfg["tau"]
        summary["alpha"] = cfg["alpha"]
        summary["threshold"] = cfg["threshold"]
        summary["window"] = cfg["window"]
        summary["radius"] = cfg["radius"]
        summary["objective_score"] = score_summary(summary)
        p = summary["prediction_precision_mean"]
        r = summary["prediction_recall_mean"]
        summary["f1_mean"] = (2.0 * p * r / (p + r)) if (p + r) > 0 else 0.0
        all_summaries.append(summary)

        if summary["objective_score"] > best_score:
            best_score = summary["objective_score"]
            best_cfg = cfg
            best_rows = rows

    write_rows(LOG_DIR / "results_intelligent.csv", best_rows)

    summary_fields = [
        "config",
        "tau",
        "alpha",
        "threshold",
        "window",
        "radius",
        "objective_score",
        "f1_mean",
    ] + [f"{k}_mean" for k in METRIC_FIELDS] + [f"{k}_std" for k in METRIC_FIELDS]

    with open(INTELLIGENT_CONFIG_DIR / "predictor_tuning_summary.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=summary_fields)
        writer.writeheader()
        for row in sorted(all_summaries, key=lambda item: item["objective_score"], reverse=True):
            writer.writerow({field: row.get(field, "") for field in summary_fields})

    return best_cfg, all_summaries


def main():
    reactive_summary = run_reactive()
    best_cfg, all_summaries = run_intelligent_tuning()

    best_summary = max(all_summaries, key=lambda item: item["objective_score"])
    print("\nBest predictor configuration selected:")
    print(best_cfg)
    print("Best averaged metrics:")
    for field in METRIC_FIELDS:
        print(f"  {field}: {best_summary[field + '_mean']:.6f} +- {best_summary[field + '_std']:.6f}")
    print(f"  objective_score: {best_summary['objective_score']:.6f}")

    print("\nReactive averaged metrics:")
    for field in METRIC_FIELDS:
        print(f"  {field}: {reactive_summary[field + '_mean']:.6f} +- {reactive_summary[field + '_std']:.6f}")


if __name__ == "__main__":
    main()
