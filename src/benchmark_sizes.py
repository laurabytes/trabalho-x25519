#!/usr/bin/env python3
"""Gera comparação de tamanhos e cenário de comunicação X25519 x ML-KEM-768."""
import csv
from pathlib import Path

import matplotlib.pyplot as plt


rows = [
    ["Chave pública", "X25519", 32, "ML-KEM-768", 1184],
    ["Chave privada", "X25519 (escalar bruto)", 32, "ML-KEM-768 (decapsulation key)", 2400],
    ["Mensagem de troca", "X25519 (duas shares públicas)", 64, "ML-KEM-768 (ciphertext)", 1088],
    ["Segredo compartilhado", "X25519", 32, "ML-KEM-768", 32],
]

data_dir = Path("data")
figures_dir = Path("figures")
data_dir.mkdir(exist_ok=True)
figures_dir.mkdir(exist_ok=True)

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

# Uma chave pública ML-KEM provisionada uma vez e reutilizada no cenário.
sessions = 1_000_000
x25519_bytes = 64 * sessions
ml_kem_bytes = 1088 * sessions + 1184
with (data_dir / "communication_scenario.csv").open("w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow([
        "sessions", "x25519_bytes", "ml_kem_768_bytes",
        "additional_bytes",
    ])
    writer.writerow([
        sessions, x25519_bytes, ml_kem_bytes,
        ml_kem_bytes - x25519_bytes,
    ])

plt.figure(figsize=(8, 5))
plt.bar(
    ["X25519: 2 public shares", "ML-KEM-768: ciphertext + public key"],
    [x25519_bytes / 1e9, ml_kem_bytes / 1e9],
)
plt.ylabel("GB para 1.000.000 de sessões (decimal)")
plt.title("Comparação ilustrativa do volume de comunicação")
plt.xticks(rotation=8, ha="right")
plt.tight_layout()
plt.savefig(figures_dir / "communication_1m.png", dpi=180)

print(f"X25519: {x25519_bytes:,} bytes")
print(f"ML-KEM-768: {ml_kem_bytes:,} bytes")
print(f"Adicional: {ml_kem_bytes - x25519_bytes:,} bytes")
