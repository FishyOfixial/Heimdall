import subprocess
import csv
from multiprocessing import Pool, cpu_count

RUNS = 30


def run_single(args):
    mode, seed = args

    cmd = [
        "python",
        "main.py",
        "--mode", mode,
        "--seed", str(seed),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    lines = result.stdout.strip().split("\n")

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
