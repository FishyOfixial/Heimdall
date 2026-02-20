import csv
from pathlib import Path
from collections import defaultdict
import math

modes = ["reactive", "intelligent"]
output_file = "compare.csv"

fields = [
    "avg_response_time",
    "coverage_percent",
    "incidents_prevented",
    "prediction_rate",
    "prediction_precision",
    "prediction_recall",
    "incidents_total",
    "resolved_incidents",
]

averages = {}
stddevs = {}

for mode in modes:
    file_path = Path(f"results_{mode}.csv")
    if not file_path.exists():
        print(f"{file_path} no existe, saltando...")
        continue

    # Listas para cada campo, para poder calcular desviación
    data = {field: [] for field in fields}

    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for field in fields:
                data[field].append(float(row[field]))

    # Promedio
    averages[mode] = {field: sum(data[field]) / len(data[field]) for field in fields}

    # Desviación estándar
    stddevs[mode] = {}
    for field in fields:
        mean = averages[mode][field]
        variance = sum((x - mean) ** 2 for x in data[field]) / len(data[field])
        stddevs[mode][field] = math.sqrt(variance)

# Guardar en compare.csv
with open(output_file, "w", newline="", encoding="utf-8") as f:
    # Escribimos header con promedio y std
    header = ["mode"]
    for field in fields:
        header.append(f"{field}_mean")
        header.append(f"{field}_std")
    writer = csv.DictWriter(f, fieldnames=header)
    writer.writeheader()

    for mode in averages.keys():
        row = {"mode": mode}
        for field in fields:
            row[f"{field}_mean"] = averages[mode][field]
            row[f"{field}_std"] = stddevs[mode][field]
        writer.writerow(row)

print(f"Archivo de promedios y desviaciones generado: {output_file}")
