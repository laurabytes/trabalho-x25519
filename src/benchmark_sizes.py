#!/usr/bin/env python3
"""Gera tabelas e gráficos de tamanhos, comunicação e recursos ECDLP."""
import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
data_dir = ROOT / "data"
figures_dir = ROOT / "figures"
data_dir.mkdir(exist_ok=True)
figures_dir.mkdir(exist_ok=True)

rows = [
    ["Chave pública", "X25519", 32, "ML-KEM-768", 1184],
    ["Chave privada", "X25519 (escalar bruto)", 32, "ML-KEM-768 (decapsulation key)", 2400],
    ["Mensagem de estabelecimento", "X25519 (chave pública)", 32, "ML-KEM-768 (ciphertext)", 1088],
    ["Segredo compartilhado", "X25519", 32, "ML-KEM-768", 32],
]

with (data_dir / "size_comparison.csv").open("w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow([
        "metric", "classic_item", "classic_bytes", "pqc_item",
        "pqc_bytes", "difference_bytes", "increase_percent",
    ])
    for metric, classic_item, classic_bytes, pqc_item, pqc_bytes in rows:
        difference = pqc_bytes - classic_bytes
        increase = (difference / classic_bytes * 100) if classic_bytes else 0
        writer.writerow([
            metric, classic_item, classic_bytes, pqc_item, pqc_bytes,
            difference, round(increase, 2),
        ])

sessions = 1_000_000
x25519_bytes = 32 * sessions
ml_kem_bytes = 1088 * sessions
with (data_dir / "communication_scenario.csv").open("w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["sessions", "x25519_bytes", "ml_kem_768_bytes", "additional_bytes"])
    writer.writerow([sessions, x25519_bytes, ml_kem_bytes, ml_kem_bytes - x25519_bytes])

plt.figure(figsize=(8, 5))
plt.bar(
    ["X25519: public key", "ML-KEM-768: ciphertext"],
    [x25519_bytes / 1e9, ml_kem_bytes / 1e9],
)
plt.ylabel("GB para 1.000.000 de sessões (decimal)")
plt.title("Volume de comunicação — cenário ilustrativo")
plt.xticks(rotation=8, ha="right")
plt.tight_layout()
plt.savefig(figures_dir / "communication_1m.svg", format="svg", bbox_inches="tight")
plt.close()

labels = [row[0] for row in rows]
classic = [row[2] for row in rows]
pqc = [row[4] for row in rows]
positions = list(range(len(labels)))
width = 0.36
plt.figure(figsize=(9, 5))
plt.bar([p - width / 2 for p in positions], classic, width, label="X25519")
plt.bar([p + width / 2 for p in positions], pqc, width, label="ML-KEM-768")
plt.xticks(positions, labels, rotation=12, ha="right")
plt.ylabel("Bytes")
plt.title("Tamanho dos elementos criptográficos")
plt.legend()
plt.tight_layout()
plt.savefig(figures_dir / "size_comparison.svg", format="svg", bbox_inches="tight")
plt.close()

results_path = data_dir / "ecdlog_shor_results.json"
if results_path.exists():
    results = json.loads(results_path.read_text())
    labels = [item["name"] for item in results]
    qubits = [item["logical_qubits"] for item in results]
    plt.figure(figsize=(8, 5))
    plt.plot(labels, qubits, marker="o")
    plt.xlabel("Instância")
    plt.ylabel("Qubits lógicos abstratos")
    plt.title("Registradores do modelo ECDLP reduzido")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(figures_dir / "ecdlog_qubits.svg", format="svg", bbox_inches="tight")
    plt.close()


qiskit_results_path = data_dir / "ecdlog_qiskit_results.json"
if qiskit_results_path.exists():
    qresults = json.loads(qiskit_results_path.read_text())
    metrics_path = data_dir / "ecdlog_qiskit_metrics.csv"
    metric_fields = [
        "name", "order", "secret_d", "recovered_d", "success", "shots",
        "logical_qubits", "transpiled_qubits", "transpiled_depth", "transpiled_total_operations",
        "transpiled_two_qubit_operations", "transpile_seconds", "simulation_transpile_seconds", "simulation_seconds",
        "informative_fraction", "period_relation_fraction",
    ]
    with metrics_path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=metric_fields)
        writer.writeheader()
        for item in qresults:
            writer.writerow({key: item.get(key) for key in metric_fields})

    case_labels = [item["name"] for item in qresults]
    for field, ylabel, title, filename in [
        ("transpiled_depth", "Profundidade", "Profundidade do circuito ECDLP transpilado", "ecdlog_qiskit_depth.svg"),
        ("transpiled_total_operations", "Operações", "Operações totais do circuito ECDLP", "ecdlog_qiskit_operations.svg"),
        ("transpiled_two_qubit_operations", "Portas de dois qubits", "Operações de dois qubits do circuito ECDLP", "ecdlog_qiskit_2q.svg"),
    ]:
        plt.figure(figsize=(8, 5))
        plt.bar(case_labels, [item[field] for item in qresults])
        plt.xlabel("Instância ECDLP")
        plt.ylabel(ylabel)
        plt.title(title)
        plt.tight_layout()
        plt.savefig(figures_dir / filename, format="svg", bbox_inches="tight")
        plt.close()

print(f"X25519: {x25519_bytes:,} bytes")
print(f"ML-KEM-768: {ml_kem_bytes:,} bytes")
print(f"Adicional: {ml_kem_bytes - x25519_bytes:,} bytes")
print("Tabelas e gráficos atualizados.")
