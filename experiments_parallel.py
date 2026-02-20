import subprocess
import csv
from multiprocessing import Pool, cpu_count

RUNS = 30
TICKS = 3600

def run_single(args):
    mode, seed = args

    cmd = [
        "python",
        "main.py",
        "--mode", mode,
        "--seed", str(seed),
        "--ticks", str(TICKS),
        "--headless",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    # si el proceso falló → guardar error
    if result.returncode != 0:
        with open(f"crash_{mode}_seed_{seed}.log", "w", encoding="utf-8") as f:
            f.write("STDOUT:\n")
            f.write(result.stdout)
            f.write("\n\nSTDERR:\n")
            f.write(result.stderr)

        raise RuntimeError(f"Simulation crashed seed={seed}")

    lines = [l for l in result.stdout.splitlines() if l.strip()]

    if len(lines) < 2:
        with open(f"bad_output_{mode}_seed_{seed}.log", "w", encoding="utf-8") as f:
            f.write(result.stdout)

        raise RuntimeError(f"Incomplete output seed={seed}")

    header = lines[-2]
    data = lines[-1]

    return header, data


def run_all(mode):
    filename = f"results_{mode}.csv"

    tasks = [(mode, seed) for seed in range(RUNS)]

    workers = max(1, cpu_count() - 1)

    print(f"\nRunning {mode} with {workers} parallel processes...\n")

    with Pool(workers) as pool:
        results = pool.map(run_single, tasks)

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)

        header_written = False

        for header, data in results:
            if not header_written:
                writer.writerow(header.split(","))
                header_written = True

            writer.writerow(data.split(","))


if __name__ == "__main__":
    run_all("reactive")
    run_all("intelligent")
