from __future__ import annotations

import argparse
import csv
import random
import subprocess
from datetime import datetime, timezone
from pathlib import Path


METRIC_ORDER = [
    "avg_response_time",
    "coverage_percent",
    "incidents_prevented",
    "prediction_rate",
    "prediction_precision",
    "prediction_recall",
    "incidents_total",
    "resolved_incidents",
]


def _parse_metrics_from_output(output: str) -> dict[str, float]:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    header_idx = -1
    for i, line in enumerate(lines):
        if line == ",".join(METRIC_ORDER):
            header_idx = i
    if header_idx < 0 or header_idx + 1 >= len(lines):
        raise ValueError("No metrics CSV block found in process output.")

    header = lines[header_idx].split(",")
    values = lines[header_idx + 1].split(",")
    parsed = {k: float(v) for k, v in zip(header, values)}
    return parsed


def _run_both(seed: int, ticks: int) -> tuple[dict[str, float], dict[str, float], str, str, str, str]:
    cmd_intelligent = [
        "python",
        "main.py",
        "--mode",
        "intelligent",
        "--seed",
        str(seed),
        "--ticks",
        str(ticks),
        "--emit-metrics",
        "--predictor-tau",
        "80.0",
        "--predictor-alpha",
        "0.20",
        "--predictor-threshold",
        "0.03",
        "--predictor-window",
        "500",
        "--predictor-radius",
        "2",
    ]
    cmd_reactive = [
        "python",
        "main.py",
        "--mode",
        "reactive",
        "--seed",
        str(seed),
        "--ticks",
        str(ticks),
        "--emit-metrics",
    ]

    p_int = subprocess.Popen(cmd_intelligent, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    p_rea = subprocess.Popen(cmd_reactive, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    out_int, err_int = p_int.communicate()
    out_rea, err_rea = p_rea.communicate()

    if p_int.returncode != 0:
        raise RuntimeError(f"intelligent crashed (code={p_int.returncode}):\n{err_int}")
    if p_rea.returncode != 0:
        raise RuntimeError(f"reactive crashed (code={p_rea.returncode}):\n{err_rea}")

    metrics_int = _parse_metrics_from_output(out_int)
    metrics_rea = _parse_metrics_from_output(out_rea)
    return metrics_int, metrics_rea, out_int, out_rea, err_int, err_rea


def _save_run(
    seed: int,
    ticks: int,
    intelligent: dict[str, float],
    reactive: dict[str, float],
    log_dir: Path,
) -> Path:
    log_dir.mkdir(parents=True, exist_ok=True)
    file_path = log_dir / "dual_simulation_stats.csv"
    row = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "seed": seed,
        "ticks": ticks,
    }
    for key in METRIC_ORDER:
        row[f"intelligent_{key}"] = intelligent.get(key, 0.0)
        row[f"reactive_{key}"] = reactive.get(key, 0.0)
        row[f"delta_{key}"] = intelligent.get(key, 0.0) - reactive.get(key, 0.0)

    fieldnames = list(row.keys())
    write_header = not file_path.exists()
    with file_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow(row)
    return file_path


def _print_comparison(intelligent: dict[str, float], reactive: dict[str, float], seed: int, ticks: int) -> None:
    print(f"\nComparacion de simulaciones (seed={seed}, ticks={ticks})")
    print(f"{'metrica':<24} {'intelligent':>14} {'reactive':>14} {'delta':>14}")
    print("-" * 70)
    for key in METRIC_ORDER:
        i_val = intelligent.get(key, 0.0)
        r_val = reactive.get(key, 0.0)
        d_val = i_val - r_val
        print(f"{key:<24} {i_val:>14.6f} {r_val:>14.6f} {d_val:>14.6f}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Lanza intelligent y reactive al mismo tiempo, muestra UI y guarda comparacion de stats."
    )
    parser.add_argument("--ticks", type=int, default=1200)
    parser.add_argument("--seed", type=int, default=None, help="Si no se especifica, se genera una aleatoria.")
    parser.add_argument("--log-dir", type=str, default="logs")
    args = parser.parse_args()

    seed = args.seed if args.seed is not None else random.SystemRandom().randint(1, 10_000_000)
    log_dir = Path(args.log_dir)
    crash_dir = log_dir / "crash"

    try:
        metrics_int, metrics_rea, _, _, _, _ = _run_both(seed=seed, ticks=args.ticks)
    except Exception as exc:
        crash_dir.mkdir(parents=True, exist_ok=True)
        error_file = crash_dir / f"dual_simulation_error_{seed}.log"
        error_file.write_text(str(exc), encoding="utf-8")
        raise

    csv_file = _save_run(seed=seed, ticks=args.ticks, intelligent=metrics_int, reactive=metrics_rea, log_dir=log_dir)
    _print_comparison(metrics_int, metrics_rea, seed=seed, ticks=args.ticks)
    print(f"\nStats guardadas en: {csv_file}")


if __name__ == "__main__":
    main()
