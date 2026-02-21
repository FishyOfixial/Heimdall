import csv
from pathlib import Path
from collections import defaultdict
import math
import matplotlib.pyplot as plt

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

# --------------------------
# Generar gráficas
# --------------------------
df = averages  # Usaremos el diccionario de promedios

# Métricas a graficar
plot_fields = [
    "avg_response_time",
    "coverage_percent",
    "incidents_total",
    "resolved_incidents",
]

for metric in plot_fields:
    mean_col = metric
    std_col = metric  # tomamos la misma métrica para std, del diccionario stddevs

    plt.figure(figsize=(6,4))
    means = [averages[mode][mean_col] for mode in modes]
    errors = [stddevs[mode][std_col] for mode in modes]
    plt.bar(modes, means, yerr=errors, capsize=5, color=["#1f77b4", "#ff7f0e"])
    plt.title(f"{metric.replace('_',' ').title()} Comparison")
    plt.ylabel(metric.replace('_',' ').title())
    plt.xlabel("Mode")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.show()
