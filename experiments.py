import subprocess
import csv

RUNS = 30   # numero de simulaciones por modo

def run(mode, seed):
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

    with open(filename, "w", newline="") as f:
        writer = None

        for seed in range(RUNS):
            print(f"{mode} seed {seed}")

            header, data = run(mode, seed)

            if writer is None:
                writer = csv.writer(f)
                writer.writerow(header.split(","))

            writer.writerow(data.split(","))


if __name__ == "__main__":
    run_all("reactive")
    run_all("intelligent")
